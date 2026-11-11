"""
Medicall Backend — AI Voice Bridge Router
Lets the AI voice assistant query available slots and book appointments
using fuzzy matching (doctor name / specialization / preferred day).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Doctor, Patient, Appointment
from schemas import AISlotQuery, AISlotResponse, TimeSlot, DoctorSummary, AppointmentOut
from services.slot_engine import get_next_available_slots, calculate_end_time
from services.notifications import send_appointment_confirmation

router = APIRouter(prefix="/ai", tags=["AI Voice Bridge"])


def _find_doctor(db: Session, name: Optional[str], specialization: Optional[str]) -> Optional[Doctor]:
    """Fuzzy match a doctor by name or specialization."""
    q = db.query(Doctor).filter(Doctor.is_active == True)
    if name:
        q = q.filter(Doctor.name.ilike(f"%{name}%"))
    elif specialization:
        q = q.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    return q.first()


def _find_or_create_patient(db: Session, name: Optional[str], phone: Optional[str]) -> Optional[Patient]:
    """Find existing patient by phone or create a minimal record."""
    if not phone:
        return None
    existing = db.query(Patient).filter(Patient.phone == phone).first()
    if existing:
        return existing
    if name:
        patient = Patient(name=name, phone=phone)
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient
    return None


# ── Suggest available slots ────────────────────────────────────────────────────

@router.get("/suggest-slots", response_model=AISlotResponse)
def suggest_slots(
    doctor_name:    Optional[str] = None,
    specialization: Optional[str] = None,
    preferred_date: Optional[str] = None,
    preferred_day:  Optional[str] = None,
    count:          int = 5,
    db:             Session = Depends(get_db)
):
    """
    AI endpoint: suggest available slots.
    Called by voice assistant when a patient asks for appointment availability.
    Example: /ai/suggest-slots?specialization=cardiology&preferred_day=friday
    """
    doctor = _find_doctor(db, doctor_name, specialization)
    if not doctor:
        return AISlotResponse(
            message=f"I couldn't find a doctor matching your request. Could you clarify the doctor's name or department?",
            available_slots=[]
        )

    # Resolve start date
    from_date = preferred_date or datetime.now().strftime("%Y-%m-%d")

    # If preferred_day given, jump to the next occurrence of that day
    if preferred_day and not preferred_date:
        day_map = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,"friday":4,"saturday":5,"sunday":6}
        target_weekday = day_map.get(preferred_day.lower())
        if target_weekday is not None:
            today = datetime.now()
            days_ahead = (target_weekday - today.weekday()) % 7 or 7
            from_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    slots = get_next_available_slots(db, doctor.id, from_date, count=count)

    if not slots:
        return AISlotResponse(
            doctor=DoctorSummary.model_validate(doctor),
            message=f"Dr. {doctor.name} has no available slots in the next two weeks. Would you like me to check a different doctor?",
            available_slots=[]
        )

    slot_text = ", ".join([f"{s.date} at {s.start_time}" for s in slots[:3]])
    return AISlotResponse(
        doctor=DoctorSummary.model_validate(doctor),
        available_slots=slots,
        message=f"Dr. {doctor.name} ({doctor.specialization}) has availability on: {slot_text}. Which slot would you prefer?"
    )


# ── Quick book via AI ─────────────────────────────────────────────────────────

@router.post("/quick-book", response_model=AppointmentOut, status_code=201)
def quick_book(
    doctor_name:    str,
    start_time:     str,
    date:           str,
    patient_name:   str,
    patient_phone:  str,
    reason:         Optional[str] = None,
    specialization: Optional[str] = None,
    db:             Session = Depends(get_db)
):
    """
    AI endpoint: book an appointment directly from voice conversation.
    Finds/creates patient and books the slot in one call.
    """
    doctor = _find_doctor(db, doctor_name, specialization)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor '{doctor_name}' not found")

    patient = _find_or_create_patient(db, patient_name, patient_phone)
    if not patient:
        raise HTTPException(status_code=400, detail="Patient name and phone are required")

    # Check slot availability
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id  == doctor.id,
        Appointment.date       == date,
        Appointment.start_time == start_time,
        Appointment.status.notin_(["cancelled"])
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail=f"Slot {date} at {start_time} is already taken")

    end_time = calculate_end_time(start_time, doctor.id, date, db)

    appt = Appointment(
        doctor_id  = doctor.id,
        patient_id = patient.id,
        date       = date,
        start_time = start_time,
        end_time   = end_time,
        status     = "scheduled",
        reason     = reason or "Appointment via Medicall AI"
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    try:
        send_appointment_confirmation(AppointmentOut.model_validate(appt))
    except Exception:
        pass

    return appt


# ── Get upcoming appointments for a patient ────────────────────────────────────

@router.get("/patient-appointments", response_model=List[AppointmentOut])
def patient_appointments_by_phone(
    phone: str = Query(..., description="Patient phone number"),
    db:    Session = Depends(get_db)
):
    """
    AI endpoint: look up a patient's upcoming appointments by phone number.
    Used during a call when a patient asks 'what are my upcoming appointments?'
    """
    patient = db.query(Patient).filter(Patient.phone == phone).first()
    if not patient:
        raise HTTPException(status_code=404, detail="No patient found with that phone number")

    today = datetime.now().strftime("%Y-%m-%d")
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.id,
        Appointment.date >= today,
        Appointment.status.notin_(["cancelled"])
    ).order_by(Appointment.date, Appointment.start_time).limit(5).all()

    return appointments

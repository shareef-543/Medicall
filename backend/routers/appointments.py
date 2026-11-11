"""
Medicall Backend — Appointments Router
Endpoints: Book, view, update, cancel appointments + upcoming schedule
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from database import get_db
from models import Appointment, Doctor, Patient, DoctorAvailability
from schemas import AppointmentCreate, AppointmentOut, AppointmentUpdate
from services.slot_engine import calculate_end_time, get_free_slots_for_doctor
from services.notifications import send_appointment_confirmation, send_appointment_cancellation

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _get_appointment_or_404(appointment_id: int, db: Session) -> Appointment:
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def _validate_slot(doctor_id: int, date_str: str, start_time: str,
                   db: Session, exclude_id: Optional[int] = None):
    """
    Ensure the requested slot is actually free for this doctor.
    Raises HTTPException if slot is taken.
    """
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date      == date_str,
        Appointment.start_time == start_time,
        Appointment.status.notin_(["cancelled"])
    )
    if exclude_id:
        conflict = conflict.filter(Appointment.id != exclude_id)
    if conflict.first():
        raise HTTPException(
            status_code=409,
            detail=f"This slot ({date_str} at {start_time}) is already booked."
        )


# ── List / filter appointments ────────────────────────────────────────────────

@router.get("/", response_model=List[AppointmentOut])
def list_appointments(
    doctor_id:  Optional[int] = None,
    patient_id: Optional[int] = None,
    date:       Optional[str] = None,
    status:     Optional[str] = None,
    upcoming:   bool = False,
    skip:       int  = 0,
    limit:      int  = 100,
    db:         Session = Depends(get_db)
):
    """
    List appointments with optional filters.
    - ?upcoming=true  → only future appointments from today
    - ?doctor_id=1    → appointments for a specific doctor
    - ?date=YYYY-MM-DD → appointments on a specific date
    """
    q = db.query(Appointment)
    if doctor_id:
        q = q.filter(Appointment.doctor_id == doctor_id)
    if patient_id:
        q = q.filter(Appointment.patient_id == patient_id)
    if date:
        q = q.filter(Appointment.date == date)
    if status:
        q = q.filter(Appointment.status == status)
    if upcoming:
        today = datetime.now().strftime("%Y-%m-%d")
        q = q.filter(Appointment.date >= today, Appointment.status != "cancelled")
    return q.order_by(Appointment.date, Appointment.start_time).offset(skip).limit(limit).all()


# ── Today's schedule ──────────────────────────────────────────────────────────

@router.get("/today", response_model=List[AppointmentOut])
def todays_appointments(
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all appointments for today, ordered by time."""
    today = datetime.now().strftime("%Y-%m-%d")
    q = db.query(Appointment).filter(
        Appointment.date == today,
        Appointment.status.notin_(["cancelled"])
    )
    if doctor_id:
        q = q.filter(Appointment.doctor_id == doctor_id)
    return q.order_by(Appointment.start_time).all()


# ── Single appointment ────────────────────────────────────────────────────────

@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Get full details of a specific appointment."""
    return _get_appointment_or_404(appointment_id, db)


# ── Book appointment ──────────────────────────────────────────────────────────

@router.post("/", response_model=AppointmentOut, status_code=201)
def book_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Book a new appointment.
    Validates that the slot is free and that both doctor and patient exist.
    """
    # Check doctor exists and is active
    doctor = db.query(Doctor).filter(
        Doctor.id == payload.doctor_id, Doctor.is_active == True
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found or inactive")

    # Check patient exists
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Validate slot is free
    _validate_slot(payload.doctor_id, payload.date, payload.start_time, db)

    # Calculate end time from doctor's slot duration
    end_time = calculate_end_time(payload.start_time, payload.doctor_id, payload.date, db)

    appt = Appointment(
        doctor_id  = payload.doctor_id,
        patient_id = payload.patient_id,
        date       = payload.date,
        start_time = payload.start_time,
        end_time   = end_time,
        status     = "scheduled",
        reason     = payload.reason,
        notes      = payload.notes
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    # Send confirmation
    try:
        send_appointment_confirmation(AppointmentOut.model_validate(appt))
    except Exception:
        pass   # Don't fail booking if notification fails

    return appt


# ── Update / Reschedule appointment ──────────────────────────────────────────

@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update or reschedule an appointment.
    Supply new date + start_time to reschedule.
    """
    appt = _get_appointment_or_404(appointment_id, db)

    if appt.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot update a cancelled appointment")

    # Rescheduling → validate new slot
    new_date  = payload.date or appt.date
    new_start = payload.start_time or appt.start_time

    if payload.date or payload.start_time:
        _validate_slot(appt.doctor_id, new_date, new_start, db, exclude_id=appointment_id)
        new_end = calculate_end_time(new_start, appt.doctor_id, new_date, db)
        appt.date       = new_date
        appt.start_time = new_start
        appt.end_time   = new_end

    if payload.status:
        appt.status = payload.status
    if payload.reason is not None:
        appt.reason = payload.reason
    if payload.notes is not None:
        appt.notes = payload.notes

    db.commit()
    db.refresh(appt)
    return appt


# ── Cancel appointment ────────────────────────────────────────────────────────

@router.delete("/{appointment_id}", response_model=AppointmentOut)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Cancel an appointment (sets status to 'cancelled', does not delete)."""
    appt = _get_appointment_or_404(appointment_id, db)
    if appt.status == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment is already cancelled")

    appt.status = "cancelled"
    db.commit()
    db.refresh(appt)

    try:
        send_appointment_cancellation(AppointmentOut.model_validate(appt))
    except Exception:
        pass

    return appt

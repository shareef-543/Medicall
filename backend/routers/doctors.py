"""
Medicall Backend — Doctors Router
Endpoints: CRUD for doctors + availability management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from database import get_db
from models import Doctor, DoctorAvailability
from schemas import DoctorCreate, DoctorOut, DoctorUpdate, DoctorSummary, AvailabilityCreate, AvailabilityOut, TimeSlot
from services.slot_engine import get_slots_for_doctor, get_free_slots_for_doctor

router = APIRouter(prefix="/doctors", tags=["Doctors"])


# ── List all doctors ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[DoctorSummary])
def list_doctors(
    active_only: bool = True,
    specialization: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all doctors, optionally filtered by specialization or department."""
    q = db.query(Doctor)
    if active_only:
        q = q.filter(Doctor.is_active == True)
    if specialization:
        q = q.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if department:
        q = q.filter(Doctor.department.ilike(f"%{department}%"))
    return q.all()


# ── Get single doctor ─────────────────────────────────────────────────────────

@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get a doctor's full profile including their availability schedule."""
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doc


# ── Create doctor ─────────────────────────────────────────────────────────────

@router.post("/", response_model=DoctorOut, status_code=201)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    """Register a new doctor with optional weekly availability schedule."""
    doc = Doctor(
        name=payload.name,
        specialization=payload.specialization,
        department=payload.department,
        phone=payload.phone,
        email=payload.email,
        bio=payload.bio,
        is_active=payload.is_active
    )
    db.add(doc)
    db.flush()  # get doc.id before committing

    for av in (payload.availability or []):
        db.add(DoctorAvailability(
            doctor_id=doc.id,
            day_of_week=av.day_of_week,
            start_time=av.start_time,
            end_time=av.end_time,
            slot_duration=av.slot_duration,
            is_available=av.is_available
        ))

    db.commit()
    db.refresh(doc)
    return doc


# ── Update doctor ─────────────────────────────────────────────────────────────

@router.put("/{doctor_id}", response_model=DoctorOut)
def update_doctor(doctor_id: int, payload: DoctorUpdate, db: Session = Depends(get_db)):
    """Update a doctor's profile information."""
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(doc, field, value)
    db.commit()
    db.refresh(doc)
    return doc


# ── Delete doctor ─────────────────────────────────────────────────────────────

@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Soft-delete a doctor (sets is_active = False)."""
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doc.is_active = False
    db.commit()


# ── Get doctor availability ───────────────────────────────────────────────────

@router.get("/{doctor_id}/availability", response_model=List[AvailabilityOut])
def get_availability(doctor_id: int, db: Session = Depends(get_db)):
    """Get a doctor's weekly availability schedule."""
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doc.availability


# ── Add availability slot ─────────────────────────────────────────────────────

@router.post("/{doctor_id}/availability", response_model=AvailabilityOut, status_code=201)
def add_availability(doctor_id: int, payload: AvailabilityCreate, db: Session = Depends(get_db)):
    """Add or update a doctor's availability for a specific day."""
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check if entry for this day already exists
    existing = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.day_of_week == payload.day_of_week
    ).first()

    if existing:
        existing.start_time    = payload.start_time
        existing.end_time      = payload.end_time
        existing.slot_duration = payload.slot_duration
        existing.is_available  = payload.is_available
        db.commit()
        db.refresh(existing)
        return existing

    av = DoctorAvailability(doctor_id=doctor_id, **payload.model_dump())
    db.add(av)
    db.commit()
    db.refresh(av)
    return av


# ── Get free appointment slots ────────────────────────────────────────────────

@router.get("/{doctor_id}/slots", response_model=List[TimeSlot])
def get_slots(
    doctor_id:  int,
    date:       str = Query(..., description="Date in YYYY-MM-DD format"),
    free_only:  bool = Query(True, description="Return only free slots"),
    db:         Session = Depends(get_db)
):
    """
    Get all appointment slots for a doctor on a specific date.
    Use ?free_only=true (default) to see only available slots.
    """
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if free_only:
        return get_free_slots_for_doctor(db, doctor_id, date)
    else:
        return get_slots_for_doctor(db, doctor_id, date)

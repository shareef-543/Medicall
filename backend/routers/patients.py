"""
Medicall Backend — Patients Router
Endpoints: CRUD for patient records
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Patient
from schemas import PatientCreate, PatientOut, PatientUpdate

router = APIRouter(prefix="/patients", tags=["Patients"])


# ── List patients ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[PatientOut])
def list_patients(
    search: Optional[str] = Query(None, description="Search by name or phone"),
    skip:   int = 0,
    limit:  int = 50,
    db:     Session = Depends(get_db)
):
    """List all patients, optionally searching by name or phone number."""
    q = db.query(Patient)
    if search:
        q = q.filter(
            Patient.name.ilike(f"%{search}%") |
            Patient.phone.ilike(f"%{search}%")
        )
    return q.offset(skip).limit(limit).all()


# ── Get single patient ────────────────────────────────────────────────────────

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get a patient's full record."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ── Search patient by phone ────────────────────────────────────────────────────

@router.get("/phone/{phone}", response_model=PatientOut)
def get_patient_by_phone(phone: str, db: Session = Depends(get_db)):
    """Look up a patient by their phone number (used by AI voice assistant)."""
    patient = db.query(Patient).filter(Patient.phone == phone).first()
    if not patient:
        raise HTTPException(status_code=404, detail="No patient found with that phone number")
    return patient


# ── Create patient ─────────────────────────────────────────────────────────────

@router.post("/", response_model=PatientOut, status_code=201)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    """Register a new patient record."""
    # Check if phone already registered
    existing = db.query(Patient).filter(Patient.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=409, detail="A patient with this phone number already exists")

    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


# ── Update patient ─────────────────────────────────────────────────────────────

@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    """Update a patient's record."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


# ── Delete patient ─────────────────────────────────────────────────────────────

@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient record."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()

"""
Medicall Backend — Pydantic Schemas (Request & Response Models)
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import date


# ─── Doctor Availability ───────────────────────────────────────────────────────

class AvailabilityBase(BaseModel):
    day_of_week:    str
    start_time:     str    # "HH:MM"
    end_time:       str    # "HH:MM"
    slot_duration:  int = 30
    is_available:   bool = True

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityOut(AvailabilityBase):
    id:        int
    doctor_id: int
    model_config = {"from_attributes": True}


# ─── Doctor ───────────────────────────────────────────────────────────────────

class DoctorBase(BaseModel):
    name:           str
    specialization: str
    department:     str
    phone:          Optional[str] = None
    email:          Optional[str] = None
    bio:            Optional[str] = None
    is_active:      bool = True

class DoctorCreate(DoctorBase):
    availability:   Optional[List[AvailabilityCreate]] = []

class DoctorUpdate(BaseModel):
    name:           Optional[str] = None
    specialization: Optional[str] = None
    department:     Optional[str] = None
    phone:          Optional[str] = None
    email:          Optional[str] = None
    bio:            Optional[str] = None
    is_active:      Optional[bool] = None

class DoctorOut(DoctorBase):
    id:           int
    availability: List[AvailabilityOut] = []
    model_config  = {"from_attributes": True}

class DoctorSummary(BaseModel):
    id:             int
    name:           str
    specialization: str
    department:     str
    is_active:      bool
    model_config    = {"from_attributes": True}


# ─── Time Slot ────────────────────────────────────────────────────────────────

class TimeSlot(BaseModel):
    date:       str
    start_time: str
    end_time:   str
    is_free:    bool


# ─── Patient ──────────────────────────────────────────────────────────────────

class PatientBase(BaseModel):
    name:          str
    phone:         str
    email:         Optional[str] = None
    date_of_birth: Optional[str] = None
    notes:         Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name:          Optional[str] = None
    phone:         Optional[str] = None
    email:         Optional[str] = None
    date_of_birth: Optional[str] = None
    notes:         Optional[str] = None

class PatientOut(PatientBase):
    id:         int
    model_config = {"from_attributes": True}


# ─── Appointment ──────────────────────────────────────────────────────────────

class AppointmentBase(BaseModel):
    doctor_id:  int
    patient_id: int
    date:       str       # "YYYY-MM-DD"
    start_time: str       # "HH:MM"
    reason:     Optional[str] = None
    notes:      Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    date:       Optional[str] = None
    start_time: Optional[str] = None
    status:     Optional[str] = None
    reason:     Optional[str] = None
    notes:      Optional[str] = None

class AppointmentOut(BaseModel):
    id:         int
    doctor_id:  int
    patient_id: int
    date:       str
    start_time: str
    end_time:   str
    status:     str
    reason:     Optional[str] = None
    notes:      Optional[str] = None
    doctor:     DoctorSummary
    patient:    PatientOut
    model_config = {"from_attributes": True}


# ─── Dashboard Summary ────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_doctors:       int
    total_patients:      int
    total_appointments:  int
    todays_appointments: int
    upcoming_today:      List[AppointmentOut]


# ─── AI Bridge ────────────────────────────────────────────────────────────────

class AISlotQuery(BaseModel):
    doctor_name:        Optional[str] = None
    specialization:     Optional[str] = None
    preferred_date:     Optional[str] = None   # "YYYY-MM-DD"
    preferred_day:      Optional[str] = None   # "monday", "tuesday" etc.
    patient_name:       Optional[str] = None
    patient_phone:      Optional[str] = None

class AISlotResponse(BaseModel):
    doctor:             Optional[DoctorSummary] = None
    available_slots:    List[TimeSlot] = []
    message:            str

"""
Medicall Backend — SQLAlchemy ORM Models
Tables: Doctor, DoctorAvailability, Patient, Appointment
"""
from sqlalchemy import (
    Column, Integer, String, Date, Time, DateTime,
    ForeignKey, Enum, Boolean, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class AppointmentStatus(str, enum.Enum):
    scheduled   = "scheduled"
    confirmed   = "confirmed"
    completed   = "completed"
    cancelled   = "cancelled"
    no_show     = "no_show"

class DayOfWeek(str, enum.Enum):
    monday    = "monday"
    tuesday   = "tuesday"
    wednesday = "wednesday"
    thursday  = "thursday"
    friday    = "friday"
    saturday  = "saturday"
    sunday    = "sunday"


# ─── Doctor ───────────────────────────────────────────────────────────────────

class Doctor(Base):
    __tablename__ = "doctors"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(120), nullable=False)
    specialization  = Column(String(120), nullable=False)
    department      = Column(String(120), nullable=False)
    phone           = Column(String(30), nullable=True)
    email           = Column(String(150), nullable=True)
    bio             = Column(Text, nullable=True)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    availability    = relationship("DoctorAvailability", back_populates="doctor", cascade="all, delete-orphan")
    appointments    = relationship("Appointment", back_populates="doctor")


# ─── Doctor Availability ───────────────────────────────────────────────────────

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    id               = Column(Integer, primary_key=True, index=True)
    doctor_id        = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    day_of_week      = Column(String(10), nullable=False)   # e.g. "monday"
    start_time       = Column(String(5), nullable=False)    # "HH:MM"
    end_time         = Column(String(5), nullable=False)    # "HH:MM"
    slot_duration    = Column(Integer, default=30)          # minutes per appointment
    is_available     = Column(Boolean, default=True)

    doctor           = relationship("Doctor", back_populates="availability")


# ─── Patient ───────────────────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(120), nullable=False)
    phone           = Column(String(30), nullable=False)
    email           = Column(String(150), nullable=True)
    date_of_birth   = Column(String(10), nullable=True)    # "YYYY-MM-DD"
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    appointments    = relationship("Appointment", back_populates="patient")


# ─── Appointment ───────────────────────────────────────────────────────────────

class Appointment(Base):
    __tablename__ = "appointments"

    id              = Column(Integer, primary_key=True, index=True)
    doctor_id       = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id      = Column(Integer, ForeignKey("patients.id"), nullable=False)
    date            = Column(String(10), nullable=False)   # "YYYY-MM-DD"
    start_time      = Column(String(5), nullable=False)    # "HH:MM"
    end_time        = Column(String(5), nullable=False)    # "HH:MM"
    status          = Column(String(20), default=AppointmentStatus.scheduled)
    reason          = Column(String(255), nullable=True)
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    doctor          = relationship("Doctor", back_populates="appointments")
    patient         = relationship("Patient", back_populates="appointments")

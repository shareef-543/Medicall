"""
Medicall Backend — Dashboard Router
Admin summary stats and full appointment schedule view
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List

from database import get_db
from models import Doctor, Patient, Appointment
from schemas import DashboardSummary, AppointmentOut

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    """
    Admin dashboard summary:
    - Total doctors, patients, appointments
    - Today's appointment count + upcoming list
    """
    today = datetime.now().strftime("%Y-%m-%d")

    total_doctors      = db.query(Doctor).filter(Doctor.is_active == True).count()
    total_patients     = db.query(Patient).count()
    total_appointments = db.query(Appointment).count()
    todays_count       = db.query(Appointment).filter(
        Appointment.date == today,
        Appointment.status.notin_(["cancelled"])
    ).count()

    upcoming_today = db.query(Appointment).filter(
        Appointment.date == today,
        Appointment.status.notin_(["cancelled"])
    ).order_by(Appointment.start_time).all()

    return DashboardSummary(
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments,
        todays_appointments=todays_count,
        upcoming_today=upcoming_today
    )

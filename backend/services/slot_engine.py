"""
Medicall Backend — Slot Engine Service
Calculates available appointment slots for a doctor on a given date.
"""
from datetime import date, datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from models import DoctorAvailability, Appointment
from schemas import TimeSlot


# Day name → Python weekday integer (Monday=0 ... Sunday=6)
DAY_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
}


def _str_to_minutes(t: str) -> int:
    """Convert 'HH:MM' string to total minutes from midnight."""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def _minutes_to_str(mins: int) -> str:
    """Convert total minutes from midnight back to 'HH:MM'."""
    return f"{mins // 60:02d}:{mins % 60:02d}"


def get_slots_for_doctor(
    db: Session,
    doctor_id: int,
    target_date: str    # "YYYY-MM-DD"
) -> List[TimeSlot]:
    """
    Returns all time slots (free + booked) for a doctor on a given date.
    Slot duration comes from DoctorAvailability for that day.
    """
    dt = datetime.strptime(target_date, "%Y-%m-%d").date()
    day_name = dt.strftime("%A").lower()

    # Get availability record for that weekday
    avail = (
        db.query(DoctorAvailability)
        .filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.day_of_week == day_name,
            DoctorAvailability.is_available == True
        )
        .first()
    )

    if not avail:
        return []   # Doctor doesn't work this day

    # Fetch existing appointments on that date
    booked = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == target_date,
        Appointment.status.notin_(["cancelled"])
    ).all()
    booked_starts = {appt.start_time for appt in booked}

    # Generate all slots
    slots: List[TimeSlot] = []
    start_mins = _str_to_minutes(avail.start_time)
    end_mins   = _str_to_minutes(avail.end_time)
    duration   = avail.slot_duration

    current = start_mins
    while current + duration <= end_mins:
        slot_start = _minutes_to_str(current)
        slot_end   = _minutes_to_str(current + duration)
        is_free    = slot_start not in booked_starts
        slots.append(TimeSlot(
            date=target_date,
            start_time=slot_start,
            end_time=slot_end,
            is_free=is_free
        ))
        current += duration

    return slots


def get_free_slots_for_doctor(
    db: Session,
    doctor_id: int,
    target_date: str
) -> List[TimeSlot]:
    """Returns only FREE (unbooked) slots for a doctor on a given date."""
    return [s for s in get_slots_for_doctor(db, doctor_id, target_date) if s.is_free]


def get_next_available_slots(
    db: Session,
    doctor_id: int,
    from_date: str,
    count: int = 5,
    days_ahead: int = 14
) -> List[TimeSlot]:
    """
    Scans the next `days_ahead` days and returns the first `count` free slots.
    Used by the AI voice assistant to suggest upcoming slots.
    """
    dt = datetime.strptime(from_date, "%Y-%m-%d").date()
    found: List[TimeSlot] = []

    for i in range(days_ahead):
        check_date = (dt + timedelta(days=i)).strftime("%Y-%m-%d")
        free = get_free_slots_for_doctor(db, doctor_id, check_date)
        for slot in free:
            found.append(slot)
            if len(found) >= count:
                return found

    return found


def calculate_end_time(start_time: str, doctor_id: int, date_str: str, db: Session) -> str:
    """
    Given a start_time and doctor, figure out the slot end time
    based on the doctor's slot_duration for that day.
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_name = dt.strftime("%A").lower()

    avail = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.day_of_week == day_name
    ).first()

    duration = avail.slot_duration if avail else 30
    start_mins = _str_to_minutes(start_time)
    return _minutes_to_str(start_mins + duration)

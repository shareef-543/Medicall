"""
Medicall Backend — Seed Data
Populates the database with sample doctors, availability, patients, and appointments.
Run with: python seed_data.py
"""
from database import SessionLocal, engine
import models
from datetime import datetime, timedelta

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

print("🌱 Seeding Medicall database...")

# ─── Doctors ──────────────────────────────────────────────────────────────────

doctors_data = [
    {
        "name": "Dr. Sarah Ahmed",
        "specialization": "Cardiology",
        "department": "Heart & Vascular",
        "phone": "+1-555-0101",
        "email": "s.ahmed@medicall.hospital",
        "bio": "Board-certified cardiologist with 12 years of experience in interventional cardiology.",
        "availability": [
            {"day": "monday",    "start": "09:00", "end": "17:00", "duration": 30},
            {"day": "tuesday",   "start": "09:00", "end": "17:00", "duration": 30},
            {"day": "wednesday", "start": "09:00", "end": "13:00", "duration": 30},
            {"day": "thursday",  "start": "09:00", "end": "17:00", "duration": 30},
            {"day": "friday",    "start": "09:00", "end": "15:00", "duration": 30},
        ]
    },
    {
        "name": "Dr. James Patel",
        "specialization": "General Medicine",
        "department": "Outpatient Clinic",
        "phone": "+1-555-0102",
        "email": "j.patel@medicall.hospital",
        "bio": "Experienced general practitioner focusing on preventive care and chronic disease management.",
        "availability": [
            {"day": "monday",    "start": "08:00", "end": "16:00", "duration": 20},
            {"day": "tuesday",   "start": "08:00", "end": "16:00", "duration": 20},
            {"day": "wednesday", "start": "08:00", "end": "16:00", "duration": 20},
            {"day": "thursday",  "start": "08:00", "end": "16:00", "duration": 20},
            {"day": "saturday",  "start": "09:00", "end": "13:00", "duration": 20},
        ]
    },
    {
        "name": "Dr. Aisha Malik",
        "specialization": "Pediatrics",
        "department": "Children's Health",
        "phone": "+1-555-0103",
        "email": "a.malik@medicall.hospital",
        "bio": "Dedicated pediatrician with expertise in child development and immunization.",
        "availability": [
            {"day": "monday",    "start": "10:00", "end": "18:00", "duration": 25},
            {"day": "wednesday", "start": "10:00", "end": "18:00", "duration": 25},
            {"day": "friday",    "start": "10:00", "end": "16:00", "duration": 25},
            {"day": "saturday",  "start": "10:00", "end": "14:00", "duration": 25},
        ]
    },
    {
        "name": "Dr. Michael Chen",
        "specialization": "Orthopedics",
        "department": "Bone & Joint",
        "phone": "+1-555-0104",
        "email": "m.chen@medicall.hospital",
        "bio": "Specialist in joint replacement, sports injuries, and minimally invasive procedures.",
        "availability": [
            {"day": "tuesday",   "start": "09:00", "end": "17:00", "duration": 45},
            {"day": "thursday",  "start": "09:00", "end": "17:00", "duration": 45},
            {"day": "friday",    "start": "09:00", "end": "13:00", "duration": 45},
        ]
    },
    {
        "name": "Dr. Fatima Rahman",
        "specialization": "Neurology",
        "department": "Brain & Spine",
        "phone": "+1-555-0105",
        "email": "f.rahman@medicall.hospital",
        "bio": "Neurologist specializing in headache, epilepsy, and stroke rehabilitation.",
        "availability": [
            {"day": "monday",    "start": "09:00", "end": "15:00", "duration": 40},
            {"day": "wednesday", "start": "09:00", "end": "15:00", "duration": 40},
            {"day": "friday",    "start": "09:00", "end": "15:00", "duration": 40},
        ]
    },
]

created_doctors = []
for d in doctors_data:
    existing = db.query(models.Doctor).filter(models.Doctor.email == d["email"]).first()
    if existing:
        created_doctors.append(existing)
        print(f"   ✓ Doctor already exists: {d['name']}")
        continue

    doc = models.Doctor(
        name=d["name"], specialization=d["specialization"],
        department=d["department"], phone=d["phone"],
        email=d["email"], bio=d["bio"], is_active=True
    )
    db.add(doc)
    db.flush()

    for av in d["availability"]:
        db.add(models.DoctorAvailability(
            doctor_id=doc.id,
            day_of_week=av["day"],
            start_time=av["start"],
            end_time=av["end"],
            slot_duration=av["duration"],
            is_available=True
        ))

    created_doctors.append(doc)
    print(f"   ✅ Created doctor: {d['name']} ({d['specialization']})")

db.commit()

# ─── Patients ─────────────────────────────────────────────────────────────────

patients_data = [
    {"name": "John Smith",     "phone": "+1-555-1001", "email": "john.smith@email.com",     "dob": "1985-06-14"},
    {"name": "Maria Garcia",   "phone": "+1-555-1002", "email": "m.garcia@email.com",       "dob": "1992-03-22"},
    {"name": "Robert Johnson", "phone": "+1-555-1003", "email": "r.johnson@email.com",      "dob": "1970-11-05"},
    {"name": "Priya Nair",     "phone": "+1-555-1004", "email": "priya.nair@email.com",     "dob": "1995-08-18"},
    {"name": "Ahmed Hassan",   "phone": "+1-555-1005", "email": "ahmed.hassan@email.com",   "dob": "1988-01-30"},
    {"name": "Lisa Wong",      "phone": "+1-555-1006", "email": "lisa.wong@email.com",      "dob": "2005-07-12"},
    {"name": "David Kim",      "phone": "+1-555-1007", "email": "d.kim@email.com",          "dob": "1965-04-25"},
]

created_patients = []
for p in patients_data:
    existing = db.query(models.Patient).filter(models.Patient.phone == p["phone"]).first()
    if existing:
        created_patients.append(existing)
        print(f"   ✓ Patient already exists: {p['name']}")
        continue

    patient = models.Patient(
        name=p["name"], phone=p["phone"],
        email=p["email"], date_of_birth=p["dob"]
    )
    db.add(patient)
    created_patients.append(patient)
    print(f"   ✅ Created patient: {p['name']}")

db.commit()

# ─── Sample Appointments ───────────────────────────────────────────────────────

today = datetime.now()

def next_weekday(weekday: int) -> str:
    """Get date string of next occurrence of a weekday (0=Monday)."""
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

appointments_data = [
    # Doctor 0 = Dr. Sarah Ahmed (Cardiology, 30-min slots)
    {"doctor_idx": 0, "patient_idx": 0, "date": next_weekday(0), "start": "09:00", "end": "09:30", "reason": "Annual cardiac checkup", "status": "scheduled"},
    {"doctor_idx": 0, "patient_idx": 2, "date": next_weekday(0), "start": "09:30", "end": "10:00", "reason": "Hypertension follow-up",  "status": "scheduled"},
    {"doctor_idx": 0, "patient_idx": 4, "date": next_weekday(1), "start": "10:00", "end": "10:30", "reason": "ECG review",               "status": "confirmed"},

    # Doctor 1 = Dr. James Patel (General, 20-min slots)
    {"doctor_idx": 1, "patient_idx": 1, "date": next_weekday(1), "start": "08:00", "end": "08:20", "reason": "Flu symptoms",             "status": "scheduled"},
    {"doctor_idx": 1, "patient_idx": 3, "date": next_weekday(2), "start": "08:20", "end": "08:40", "reason": "General checkup",          "status": "scheduled"},

    # Doctor 2 = Dr. Aisha Malik (Pediatrics, 25-min slots)
    {"doctor_idx": 2, "patient_idx": 5, "date": next_weekday(2), "start": "10:00", "end": "10:25", "reason": "6-month vaccination",      "status": "confirmed"},

    # Doctor 3 = Dr. Michael Chen (Orthopedics, 45-min slots)
    {"doctor_idx": 3, "patient_idx": 6, "date": next_weekday(3), "start": "09:00", "end": "09:45", "reason": "Knee replacement consult",  "status": "scheduled"},
]

for appt_data in appointments_data:
    doc     = created_doctors[appt_data["doctor_idx"]]
    patient = created_patients[appt_data["patient_idx"]]

    if not doc.id or not patient.id:
        continue

    # Avoid duplicates
    existing = db.query(models.Appointment).filter(
        models.Appointment.doctor_id  == doc.id,
        models.Appointment.date       == appt_data["date"],
        models.Appointment.start_time == appt_data["start"]
    ).first()

    if existing:
        print(f"   ✓ Appointment already exists: {doc.name} on {appt_data['date']} at {appt_data['start']}")
        continue

    appt = models.Appointment(
        doctor_id  = doc.id,
        patient_id = patient.id,
        date       = appt_data["date"],
        start_time = appt_data["start"],
        end_time   = appt_data["end"],
        status     = appt_data["status"],
        reason     = appt_data["reason"]
    )
    db.add(appt)
    print(f"   ✅ Booked: {patient.name} → {doc.name} on {appt_data['date']} at {appt_data['start']}")

db.commit()
db.close()

print("\n✅ Database seeded successfully!")
print("   Run: uvicorn main:app --reload --port 8000")
print("   Docs: http://localhost:8000/docs\n")

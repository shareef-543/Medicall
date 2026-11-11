# Medicall — AI Receptionist for Healthcare

> **Your hospital's AI receptionist, available 24/7.**

Medicall is an AI-powered receptionist for hospitals. It handles patient calls, answers common questions, assists with appointment-related requests, and routes important calls to the right hospital staff.

---

## Project Structure

```
medicall-monorepo/
├── frontend/           # Website (HTML + CSS + JS)
│   ├── index.html      # Main marketing website
│   ├── voice.html      # Live AI voice assistant (GPT-4o + Web Speech API)
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── main.js
│   └── assets/
│       └── medicall-logo.jpg
│
└── backend/            # REST API (Python FastAPI + SQLite)
    ├── main.py         # FastAPI app entry point
    ├── database.py     # SQLAlchemy DB connection
    ├── models.py       # ORM models (Doctor, Patient, Appointment)
    ├── schemas.py      # Pydantic request/response schemas
    ├── seed_data.py    # Sample data seeder
    ├── requirements.txt
    ├── routers/
    │   ├── doctors.py        # Doctor CRUD + availability
    │   ├── patients.py       # Patient records
    │   ├── appointments.py   # Booking, rescheduling, cancellation
    │   ├── ai_bridge.py      # AI voice assistant integration
    │   └── dashboard.py      # Admin summary stats
    └── services/
        ├── slot_engine.py    # Smart available slot calculator
        └── notifications.py  # Email/SMS stubs (ready for SendGrid/Twilio)
```

---

## Frontend

### Tech Stack
- Pure **HTML5 + CSS3 + JavaScript** (no build step)
- **Tailwind CSS** (CDN)
- **Font Awesome** icons
- **Google Fonts** — Outfit + Plus Jakarta Sans
- **HTML5 Canvas** for medical background animations

### Features
- 🏥 Full responsive medical website (desktop + mobile 4-frame layout)
- 🎙️ **Live AI Voice Assistant** (`voice.html`) — speak to Medicall AI
- 🤖 Powered by **OpenAI GPT-4o** + **Web Speech API**
- 📱 Animated medical background (ECG lines, floating crosses, particles)
- 📞 Call + Message floating action buttons
- 📋 Contact form + appointment request modal

### Running the Frontend

```bash
# Python simple server (no install needed)
python -m http.server 5500 --directory frontend/

# Then open:
# http://localhost:5500
# http://localhost:5500/voice.html
```

### Using the Voice Assistant
1. Open `http://localhost:5500/voice.html`
2. Enter your **OpenAI API key** (`sk-proj-...`)
3. Click the **blue orb** and speak naturally
4. Medicall AI responds with voice

> **Browser Support:** Chrome or Edge (required for Web Speech API)

---

## Backend

### Tech Stack
- **Python 3.11+**
- **FastAPI** — modern async REST API
- **SQLAlchemy** — ORM
- **SQLite** — database (zero config, file-based)
- **Uvicorn** — ASGI server
- **Pydantic** — data validation

### Database Models

| Model | Description |
|---|---|
| `Doctor` | Doctor profile, specialization, department |
| `DoctorAvailability` | Weekly schedule per doctor (day, start/end time, slot duration) |
| `Patient` | Patient records (name, phone, email) |
| `Appointment` | Booked slots (doctor + patient + date + time + status) |

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/doctors` | List all doctors |
| `GET` | `/doctors/{id}` | Doctor profile + availability |
| `POST` | `/doctors` | Create a new doctor |
| `GET` | `/doctors/{id}/slots?date=YYYY-MM-DD` | Free slots for a date |
| `POST` | `/doctors/{id}/availability` | Set/update weekly schedule |
| `GET` | `/patients` | List patients |
| `POST` | `/patients` | Register a patient |
| `GET` | `/appointments` | List/filter appointments |
| `POST` | `/appointments` | Book a new appointment |
| `PUT` | `/appointments/{id}` | Reschedule / update status |
| `DELETE` | `/appointments/{id}` | Cancel appointment |
| `GET` | `/ai/suggest-slots` | AI: suggest available slots by specialty/day |
| `POST` | `/ai/quick-book` | AI: book appointment from voice conversation |
| `GET` | `/ai/patient-appointments?phone=...` | AI: patient's upcoming appointments |
| `GET` | `/dashboard/summary` | Admin dashboard stats |
| `GET` | `/appointments/today` | Today's full schedule |

### Setup & Running

```bash
cd backend/

# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed the database with sample doctors + appointments
python seed_data.py

# 3. Start the API server
uvicorn main:app --reload --port 8000
```

### API Docs (auto-generated)
Once running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Sample API Calls

```bash
# List all doctors
curl http://localhost:8000/doctors/

# Get free slots for Dr. Sarah Ahmed (id=1) on Nov 10
curl "http://localhost:8000/doctors/1/slots?date=2026-11-10"

# Book an appointment
curl -X POST http://localhost:8000/appointments/ \
  -H "Content-Type: application/json" \
  -d '{"doctor_id":1,"patient_id":1,"date":"2026-11-10","start_time":"11:00","reason":"Checkup"}'

# AI: suggest cardiology slots
curl "http://localhost:8000/ai/suggest-slots?specialization=Cardiology&count=5"

# Dashboard summary
curl http://localhost:8000/dashboard/summary
```

---

## Seeded Data

The `seed_data.py` script creates:

**5 Doctors:**
- Dr. Sarah Ahmed — Cardiology (Mon–Fri, 30-min slots)
- Dr. James Patel — General Medicine (Mon–Sat, 20-min slots)
- Dr. Aisha Malik — Pediatrics (Mon/Wed/Fri/Sat, 25-min slots)
- Dr. Michael Chen — Orthopedics (Tue/Thu/Fri, 45-min slots)
- Dr. Fatima Rahman — Neurology (Mon/Wed/Fri, 40-min slots)

**7 Sample Patients** + **7 Sample Appointments**

---

## Roadmap

- [ ] Connect AI voice assistant to backend for real-time slot booking during calls
- [ ] Add SendGrid email confirmations
- [ ] Add Twilio SMS reminders
- [ ] Admin dashboard UI (React or plain HTML)
- [ ] Deploy backend to Railway / Render
- [ ] Deploy frontend to GitHub Pages / Netlify
- [ ] Add authentication (API keys or OAuth)

---

## License

© 2026 Medicall. All rights reserved.

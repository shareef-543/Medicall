"""
Medicall Backend — FastAPI Application Entry Point
Run with: uvicorn main:app --reload --port 8000
Docs:     http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
import models

# ─── Create all tables on startup ─────────────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Medicall API",
    description="""
## Medicall — AI Receptionist Backend

Manages **doctors**, **patients**, and **appointments** for the Medicall AI receptionist system.

### Key Features
- 🩺 Doctor profiles with weekly availability schedules
- 📅 Smart appointment slot engine (auto-calculates free/booked slots)
- 🤖 AI Voice Bridge — lets the Medicall voice assistant query and book appointments
- 📊 Admin dashboard summary
- 🔔 Appointment confirmation notifications (stubbed, ready for SendGrid/Twilio)

### Quick Start
1. `POST /patients` — register a patient
2. `GET /doctors` — list all doctors
3. `GET /doctors/{id}/slots?date=YYYY-MM-DD` — see free slots
4. `POST /appointments` — book a slot
""",
    version="1.0.0",
    contact={
        "name": "Medicall Team",
        "email": "hello@medicall.ai"
    }
)

# ─── CORS — allow frontend at localhost:5500 and any origin in dev ─────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
from routers import doctors, patients, appointments, ai_bridge, dashboard

app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(ai_bridge.router)
app.include_router(dashboard.router)

# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Medicall API",
        "status":  "running",
        "version": "1.0.0",
        "docs":    "/docs",
        "redoc":   "/redoc"
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}

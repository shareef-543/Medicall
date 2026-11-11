"""
Medicall Backend — Notification Service (Stubs)
In production: plug in SendGrid (email) or Twilio (SMS).
"""
from schemas import AppointmentOut


def send_appointment_confirmation(appointment: AppointmentOut) -> bool:
    """
    Send appointment confirmation to patient.
    TODO: Replace prints with real email/SMS integration.
    """
    patient = appointment.patient
    doctor  = appointment.doctor

    print(f"\n📧 [EMAIL STUB] To: {patient.email or patient.phone}")
    print(f"   Subject: Appointment Confirmation — Medicall")
    print(f"   Dear {patient.name},")
    print(f"   Your appointment with Dr. {doctor.name} ({doctor.specialization})")
    print(f"   is confirmed for {appointment.date} at {appointment.start_time}.")
    print(f"   Status: {appointment.status}\n")
    return True


def send_appointment_cancellation(appointment: AppointmentOut) -> bool:
    """Send cancellation notice to patient."""
    patient = appointment.patient
    doctor  = appointment.doctor

    print(f"\n📧 [EMAIL STUB] To: {patient.email or patient.phone}")
    print(f"   Subject: Appointment Cancelled — Medicall")
    print(f"   Dear {patient.name},")
    print(f"   Your appointment with Dr. {doctor.name} on {appointment.date}")
    print(f"   at {appointment.start_time} has been cancelled.\n")
    return True


def send_appointment_reminder(appointment: AppointmentOut) -> bool:
    """Send reminder 24 hours before appointment."""
    patient = appointment.patient
    doctor  = appointment.doctor

    print(f"\n📱 [SMS STUB] To: {patient.phone}")
    print(f"   Reminder: Appointment with Dr. {doctor.name}")
    print(f"   Tomorrow at {appointment.start_time}. — Medicall\n")
    return True

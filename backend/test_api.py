import urllib.request, json

# Test doctors
r = urllib.request.urlopen('http://localhost:8000/doctors/')
doctors = json.loads(r.read())
print("=== DOCTORS ===")
for d in doctors:
    print(f"  [{d['id']}] Dr. {d['name']} - {d['specialization']} | {d['department']}")

# Test free slots for doctor 1 on a specific date
print("\n=== FREE SLOTS: Dr. Sarah Ahmed on 2026-11-10 ===")
r2 = urllib.request.urlopen('http://localhost:8000/doctors/1/slots?date=2026-11-10&free_only=true')
slots = json.loads(r2.read())
for s in slots[:6]:
    print(f"  {s['start_time']} - {s['end_time']}  free={s['is_free']}")

# Test dashboard
print("\n=== DASHBOARD ===")
r3 = urllib.request.urlopen('http://localhost:8000/dashboard/summary')
dash = json.loads(r3.read())
print(f"  Doctors: {dash['total_doctors']}")
print(f"  Patients: {dash['total_patients']}")
print(f"  Appointments: {dash['total_appointments']}")
print(f"  Today's appointments: {dash['todays_appointments']}")

# Test AI suggest slots
print("\n=== AI SLOT SUGGESTION: Cardiology, next Friday ===")
r4 = urllib.request.urlopen('http://localhost:8000/ai/suggest-slots?specialization=Cardiology&count=3')
ai = json.loads(r4.read())
print(f"  Message: {ai['message']}")
for s in ai['available_slots']:
    print(f"  {s['date']} at {s['start_time']}")

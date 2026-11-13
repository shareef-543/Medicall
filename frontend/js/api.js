/**
 * Medicall API Client
 * Central module for all backend API calls.
 * Change BASE_URL to your deployed backend URL when going to production.
 */

const MedicallAPI = (() => {

  // ── Config ────────────────────────────────────────────────────────────────
  // Local dev:  http://localhost:8000
  // Production: https://your-render-url.onrender.com
  const BASE_URL = window.MEDICALL_API_URL || 'http://localhost:8000';

  // ── Helper ────────────────────────────────────────────────────────────────
  async function request(path, options = {}) {
    try {
      const res = await fetch(`${BASE_URL}${path}`, {
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
        ...options,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return res.status === 204 ? null : await res.json();
    } catch (e) {
      console.error(`[MedicallAPI] ${path}`, e.message);
      throw e;
    }
  }

  // ── Health ────────────────────────────────────────────────────────────────
  const health = () => request('/health');

  // ── Doctors ───────────────────────────────────────────────────────────────
  const getDoctors = (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/doctors/${q ? '?' + q : ''}`);
  };

  const getDoctor = (id) => request(`/doctors/${id}`);

  const getDoctorAvailability = (id) => request(`/doctors/${id}/availability`);

  const getDoctorSlots = (doctorId, date, freeOnly = true) =>
    request(`/doctors/${doctorId}/slots?date=${date}&free_only=${freeOnly}`);

  // ── Patients ──────────────────────────────────────────────────────────────
  const getPatients = (search = '') =>
    request(`/patients/${search ? '?search=' + encodeURIComponent(search) : ''}`);

  const getPatientByPhone = (phone) =>
    request(`/patients/phone/${encodeURIComponent(phone)}`);

  const createPatient = (data) =>
    request('/patients/', { method: 'POST', body: JSON.stringify(data) });

  // ── Appointments ──────────────────────────────────────────────────────────
  const getAppointments = (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/appointments/${q ? '?' + q : ''}`);
  };

  const getTodaysAppointments = (doctorId = null) =>
    request(`/appointments/today${doctorId ? '?doctor_id=' + doctorId : ''}`);

  const bookAppointment = (data) =>
    request('/appointments/', { method: 'POST', body: JSON.stringify(data) });

  const updateAppointment = (id, data) =>
    request(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(data) });

  const cancelAppointment = (id) =>
    request(`/appointments/${id}`, { method: 'DELETE' });

  // ── Dashboard ─────────────────────────────────────────────────────────────
  const getDashboard = () => request('/dashboard/summary');

  // ── AI Bridge ─────────────────────────────────────────────────────────────
  const suggestSlots = (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/ai/suggest-slots?${q}`);
  };

  const quickBook = (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/ai/quick-book?${q}`, { method: 'POST' });
  };

  const getPatientAppointmentsByPhone = (phone) =>
    request(`/ai/patient-appointments?phone=${encodeURIComponent(phone)}`);

  // ── Utility: check if backend is reachable ─────────────────────────────
  async function isOnline() {
    try { await health(); return true; }
    catch { return false; }
  }

  // Public API
  return {
    BASE_URL,
    isOnline,
    health,
    getDoctors,
    getDoctor,
    getDoctorAvailability,
    getDoctorSlots,
    getPatients,
    getPatientByPhone,
    createPatient,
    getAppointments,
    getTodaysAppointments,
    bookAppointment,
    updateAppointment,
    cancelAppointment,
    getDashboard,
    suggestSlots,
    quickBook,
    getPatientAppointmentsByPhone,
  };

})();

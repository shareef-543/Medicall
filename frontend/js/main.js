/**
 * Medicall — AI Receptionist for Hospitals
 * Main JavaScript: Canvas Animation, Header Scroll, 4-Frame Nav, Modals, Forms
 */

/* ═══════════════════════════════════════════════════════════════
   1. MEDICAL CANVAS BACKGROUND ANIMATION
═══════════════════════════════════════════════════════════════ */
(function initCanvas() {
  const canvas = document.getElementById('medicalCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width, height, particles = [], crosses = [], pulses = [];
  let mouse = { x: null, y: null, radius: 160 };

  window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
  window.addEventListener('mouseout', () => { mouse.x = null; mouse.y = null; });

  const resize = () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    initElements();
  };

  const initElements = () => {
    particles = []; crosses = []; pulses = [];
    const count = Math.floor(Math.min(width, 1600) / 32);
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width, y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5, vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2.5 + 1.2,
        color: Math.random() > 0.5 ? 'rgba(29,104,216,' : 'rgba(13,148,136,',
        alpha: Math.random() * 0.4 + 0.2
      });
    }
    for (let i = 0; i < 14; i++) {
      crosses.push({
        x: Math.random() * width, y: Math.random() * height,
        size: Math.random() * 10 + 8,
        speedY: -(Math.random() * 0.35 + 0.18),
        speedX: (Math.random() - 0.5) * 0.1,
        rot: Math.random() * Math.PI,
        rotSpeed: (Math.random() - 0.5) * 0.007,
        alpha: Math.random() * 0.3 + 0.18,
        color: Math.random() > 0.4 ? '#0d9488' : '#0284c7'
      });
    }
    pulses.push({ x: 0, speed: 2.6, yBase: height * 0.38, color: 'rgba(14,165,233,0.45)' });
    pulses.push({ x: -width * 0.5, speed: 3.0, yBase: height * 0.84, color: 'rgba(16,185,129,0.42)' });
  };

  window.addEventListener('resize', resize);
  resize();

  const animate = () => {
    ctx.clearRect(0, 0, width, height);

    // ECG Waves
    pulses.forEach(p => {
      p.x += p.speed;
      if (p.x > width + 120) p.x = -150;
      ctx.beginPath();
      ctx.strokeStyle = p.color;
      ctx.lineWidth = 2;
      for (let x = 0; x < width; x += 6) {
        let dy = 0;
        const dist = Math.abs(x - p.x);
        if (dist < 100) {
          if (dist < 15) dy = -Math.sin(dist / 15 * Math.PI) * 34;
          else if (dist < 32) dy = Math.sin((dist - 15) / 17 * Math.PI) * 13;
          else dy = -Math.sin((dist - 32) / 68 * Math.PI) * 7;
        }
        x === 0 ? ctx.moveTo(x, p.yBase + dy) : ctx.lineTo(x, p.yBase + dy);
      }
      ctx.stroke();
      // Pulse dot
      ctx.fillStyle = p.color;
      ctx.shadowColor = p.color;
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(p.x, p.yBase, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    // Floating Medical Crosses
    crosses.forEach(c => {
      c.y += c.speedY; c.x += c.speedX; c.rot += c.rotSpeed;
      if (c.y < -40) { c.y = height + 40; c.x = Math.random() * width; }
      ctx.save();
      ctx.translate(c.x, c.y);
      ctx.rotate(c.rot);
      ctx.globalAlpha = c.alpha;
      ctx.fillStyle = 'rgba(255,255,255,0.6)';
      ctx.beginPath();
      ctx.arc(0, 0, c.size * 1.35, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = c.color;
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(-c.size, 0); ctx.lineTo(c.size, 0);
      ctx.moveTo(0, -c.size); ctx.lineTo(0, c.size);
      ctx.stroke();
      ctx.restore();
    });

    // Particle Constellation
    particles.forEach((p, i) => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;
      if (mouse.x && mouse.y) {
        const d = Math.hypot(p.x - mouse.x, p.y - mouse.y);
        if (d < mouse.radius) {
          const a = Math.atan2(p.y - mouse.y, p.x - mouse.x);
          p.x += Math.cos(a) * 1.1;
          p.y += Math.sin(a) * 1.1;
        }
      }
      ctx.fillStyle = `${p.color}${p.alpha})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fill();
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
        if (dist < 130) {
          ctx.strokeStyle = `rgba(14,165,233,${(1 - dist / 130) * 0.25})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }
    });

    requestAnimationFrame(animate);
  };
  requestAnimationFrame(animate);
})();

/* ═══════════════════════════════════════════════════════════════
   2. HEADER SCROLL EFFECT
═══════════════════════════════════════════════════════════════ */
(function initHeader() {
  const header = document.getElementById('mainHeader');
  if (!header) return;
  const onScroll = () => {
    header.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

/* ═══════════════════════════════════════════════════════════════
   3. MOBILE MENU TOGGLE
═══════════════════════════════════════════════════════════════ */
function closeMobileMenu() {
  const menu = document.getElementById('mobileMenu');
  const btn  = document.getElementById('mobileMenuBtn');
  if (menu) menu.classList.add('hidden');
  if (btn)  btn.setAttribute('aria-expanded', 'false');
  document.body.classList.remove('overflow-hidden');
}

(function initMobileMenu() {
  const btn  = document.getElementById('mobileMenuBtn');
  const menu = document.getElementById('mobileMenu');
  if (!btn || !menu) return;
  btn.addEventListener('click', () => {
    const isOpen = !menu.classList.contains('hidden');
    if (isOpen) {
      closeMobileMenu();
    } else {
      menu.classList.remove('hidden');
      btn.setAttribute('aria-expanded', 'true');
    }
  });
})();

/* ═══════════════════════════════════════════════════════════════
   4. MOBILE 4-FRAME SCROLLSPY
═══════════════════════════════════════════════════════════════ */
(function initScrollSpy() {
  const tabs = document.querySelectorAll('.frame-tab');
  if (!tabs.length) return;

  const frameMap = { 'frame-1': '#hero', 'frame-2': '#how', 'frame-3': '#features', 'frame-4': '#contact' };

  const getScrollCenter = () => window.scrollY + window.innerHeight * 0.45;

  const update = () => {
    let activeFrame = 'frame-1';
    const scroll = getScrollCenter();
    Object.entries(frameMap).forEach(([frame, sel]) => {
      const el = document.querySelector(sel);
      if (el && scroll >= el.offsetTop) activeFrame = frame;
    });
    tabs.forEach(t => {
      const isActive = t.getAttribute('data-frame') === activeFrame;
      t.classList.toggle('active', isActive);
    });
  };

  window.addEventListener('scroll', update, { passive: true });
  update();
})();

/* ═══════════════════════════════════════════════════════════════
   5. SCROLL REVEAL (fade-in-up)
═══════════════════════════════════════════════════════════════ */
(function initReveal() {
  const obs = new IntersectionObserver((entries, observer) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

  document.querySelectorAll('.fade-in-up').forEach(el => obs.observe(el));
})();

/* ═══════════════════════════════════════════════════════════════
   6. CALL MODAL  (live API-powered appointment scenario)
═══════════════════════════════════════════════════════════════ */

// Fallback static scripts (used when API is offline)
const callScenarios = {
  appointment: [
    { who: 'patient', text: 'Hi, I need to book an appointment with Dr. Ahmed.' },
    { who: 'ai', text: 'Hello! I\'d be happy to help with that. May I have your name and preferred date for the appointment?' },
    { who: 'patient', text: 'I\'m Sara. I\'d like Thursday or Friday morning if possible.' },
    { who: 'ai', text: 'Thank you, Sara. Dr. Ahmed has availability on Thursday at 10:30 AM and Friday at 11:00 AM. Which works better for you?' },
    { who: 'patient', text: 'Friday 11 AM please.' },
    { who: 'ai', text: 'Perfect! I\'ve noted Friday at 11:00 AM for Dr. Ahmed. Is there anything else I can help you with today?' },
  ],
  triage: [
    { who: 'patient', text: 'Hello, I\'ve been feeling dizzy since taking my new medication this morning.' },
    { who: 'ai', text: 'I\'m here to help. Are you experiencing any chest pain, shortness of breath, or sudden weakness alongside the dizziness?' },
    { who: 'patient', text: 'No, just lightheaded when I stand up.' },
    { who: 'ai', text: 'Thank you. This could be a positional side effect. I\'m connecting you to our on-call nurse with your medication notes. Please stay on the line.' },
  ],
  general: [
    { who: 'patient', text: 'What are visiting hours for the surgical recovery ward?' },
    { who: 'ai', text: 'Visiting hours for the Surgical Recovery Ward are 10:00 AM to 8:00 PM daily. Up to two visitors are permitted per patient at a time.' },
    { who: 'patient', text: 'Is there parking near the west entrance?' },
    { who: 'ai', text: 'Yes! The West Pavilion has a multi-storey car park directly adjacent. The first 30 minutes are free, and patient and visitor rates apply thereafter.' },
  ]
};

let callState = { active: false, timerId: null, timeouts: [], liveDoctors: [] };

// ── Live Appointment Flow ──────────────────────────────────────────────────
// When API is online, the appointment scenario fetches real doctors + slots.
let _liveAppointmentScript = null;  // built dynamically from API data

async function buildLiveAppointmentScript() {
  try {
    const doctors = await MedicallAPI.getDoctors();
    if (!doctors || doctors.length === 0) return null;

    callState.liveDoctors = doctors;

    // Pick first doctor as the demo subject
    const doc = doctors[0];
    const today = new Date().toISOString().split('T')[0];
    let slots = [];
    try {
      slots = await MedicallAPI.getDoctorSlots(doc.id, today, true);
    } catch (_) { slots = []; }

    const slotText = slots.length
      ? slots.slice(0, 2).map(s => s.start_time).join(' and ')
      : '10:30 AM and 11:00 AM';

    const speciality = doc.specialization || doc.speciality || 'General Medicine';

    return [
      { who: 'patient', text: `Hi, I need to book an appointment with ${doc.name}.` },
      { who: 'ai',      text: `Hello! I'd be happy to help. ${doc.name} specialises in ${speciality}. May I have your name?` },
      { who: 'patient', text: 'My name is Sara.' },
      { who: 'ai',      text: `Thank you Sara. I'm checking availability for ${doc.name} today…` },
      { who: 'ai',      text: `${doc.name} has open slots at ${slotText}. Which time works for you?` },
      { who: 'patient', text: `The first one, please.` },
      { who: 'ai',      text: `I've reserved that slot for you, Sara. You'll receive a confirmation shortly. Is there anything else I can help you with?` },
    ];
  } catch (e) {
    console.warn('[Medicall] Live appointment script failed, using fallback:', e.message);
    return null;
  }
}

function openCallModal() {
  const modal = document.getElementById('callModal');
  if (!modal) return;
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  const scenSel = document.getElementById('scenarioSelect');
  const activeCall = document.getElementById('activeCall');
  if (scenSel) scenSel.classList.remove('hidden');
  if (activeCall) activeCall.classList.add('hidden');

  // Pre-fetch live appointment script in background
  buildLiveAppointmentScript().then(script => { _liveAppointmentScript = script; });
}

function closeCallModal() {
  const modal = document.getElementById('callModal');
  if (!modal) return;
  modal.classList.add('hidden');
  document.body.style.overflow = '';
  endCall();
}

function startCall(scenarioKey) {
  const scenSel    = document.getElementById('scenarioSelect');
  const active     = document.getElementById('activeCall');
  const transcript = document.getElementById('callTranscript');
  if (!active || !transcript) return;

  if (scenSel) scenSel.classList.add('hidden');
  active.classList.remove('hidden');

  transcript.innerHTML = '';
  callState.timeouts.forEach(clearTimeout);
  callState.timeouts = [];
  if (callState.timerId) clearInterval(callState.timerId);
  callState.active = true;

  // Use live API script for appointment scenario if available
  const msgs = (scenarioKey === 'appointment' && _liveAppointmentScript)
    ? _liveAppointmentScript
    : (callScenarios[scenarioKey] || callScenarios.appointment);

  let delay = 600;
  msgs.forEach(msg => {
    const t = setTimeout(() => {
      if (!callState.active) return;
      appendCallMsg(transcript, msg.who, msg.text);
    }, delay);
    callState.timeouts.push(t);
    delay += msg.text.length * 38 + 1000;
  });
}

function appendCallMsg(container, who, text) {
  const div = document.createElement('div');
  div.className = `call-msg ${who}`;
  if (who === 'ai') {
    div.innerHTML = `
      <div class="call-msg-icon"><i class="fa-solid fa-robot"></i></div>
      <div class="call-msg-bubble">${text}</div>`;
  } else {
    div.innerHTML = `
      <div class="call-msg-icon"><i class="fa-solid fa-user"></i></div>
      <div class="call-msg-bubble">${text}</div>`;
  }
  container.appendChild(div);
  setTimeout(() => { container.scrollTop = container.scrollHeight; }, 50);
}

function endCall() {
  callState.active = false;
  callState.timeouts.forEach(clearTimeout);
  callState.timeouts = [];
  if (callState.timerId) { clearInterval(callState.timerId); callState.timerId = null; }

  const scenSel  = document.getElementById('scenarioSelect');
  const active   = document.getElementById('activeCall');
  const transcript = document.getElementById('callTranscript');
  if (scenSel) scenSel.classList.remove('hidden');
  if (active) active.classList.add('hidden');
  if (transcript) transcript.innerHTML = '';
}

// Close call modal on overlay click
document.addEventListener('DOMContentLoaded', () => {
  const callModal = document.getElementById('callModal');
  if (callModal) {
    callModal.addEventListener('click', e => {
      if (e.target === callModal) closeCallModal();
    });
  }
});

/* ═══════════════════════════════════════════════════════════════
   7. QUICK MESSAGE MODAL
═══════════════════════════════════════════════════════════════ */
function openQuickMessage() {
  const modal = document.getElementById('quickMessageModal');
  if (!modal) return;
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  // Reset form
  const form    = document.getElementById('quickMsgForm');
  const success = document.getElementById('qmSuccess');
  if (form)    { form.classList.remove('hidden'); form.reset(); }
  if (success) success.classList.add('hidden');
}

function closeQuickMessage() {
  const modal = document.getElementById('quickMessageModal');
  if (!modal) return;
  modal.classList.add('hidden');
  document.body.style.overflow = '';
}

function submitQuickMsg(e) {
  e.preventDefault();
  const btn = e.submitter || e.target.querySelector('[type="submit"]');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Sending…'; }
  setTimeout(() => {
    const form    = document.getElementById('quickMsgForm');
    const success = document.getElementById('qmSuccess');
    if (form)    form.classList.add('hidden');
    if (success) success.classList.remove('hidden');
    setTimeout(closeQuickMessage, 2000);
  }, 900);
}

// Close quick message modal on overlay click
document.addEventListener('DOMContentLoaded', () => {
  const qmModal = document.getElementById('quickMessageModal');
  if (qmModal) {
    qmModal.addEventListener('click', e => {
      if (e.target === qmModal) closeQuickMessage();
    });
  }
});

/* ═══════════════════════════════════════════════════════════════
   8. CONTACT FORM  (registers patient lead via API when online)
═══════════════════════════════════════════════════════════════ */
async function submitContactForm(e) {
  e.preventDefault();
  const btn = e.submitter || e.target.querySelector('[type="submit"]');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Sending…'; }

  // Collect form values
  const name  = (document.getElementById('cf-name')    || {}).value || '';
  const email = (document.getElementById('cf-email')   || {}).value || '';
  const phone = (document.getElementById('cf-phone')   || {}).value || '';
  const msg   = (document.getElementById('cf-message') || {}).value || '';

  // Try to register as a patient lead if phone provided
  if (phone) {
    try {
      await MedicallAPI.createPatient({
        name:  name  || 'Unknown',
        phone: phone,
        email: email || null,
        notes: msg   || null,
      });
      console.info('[Medicall] Patient lead registered via API');
    } catch (err) {
      console.warn('[Medicall] Patient registration skipped (backend offline):', err.message);
    }
  }

  setTimeout(() => {
    const form    = document.getElementById('contactForm');
    const success = document.getElementById('formSuccess');
    if (form)    form.classList.add('hidden');
    if (success) success.classList.remove('hidden');
    if (btn) { btn.disabled = false; }
  }, 800);
}

/* ═══════════════════════════════════════════════════════════════
   9. API INTEGRATION — boot sequence
═══════════════════════════════════════════════════════════════ */
(function initAPI() {
  if (typeof MedicallAPI === 'undefined') {
    console.warn('[Medicall] api.js not loaded — running in offline mode.');
    return;
  }

  // ── A. API status indicator (green/grey dot in header) ─────────────────
  function setApiStatus(online) {
    const dot = document.getElementById('apiStatusDot');
    const lbl = document.getElementById('apiStatusLabel');
    if (!dot) return;
    if (online) {
      dot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
      if (lbl) lbl.textContent = 'Live';
    } else {
      dot.className = 'w-2 h-2 rounded-full bg-slate-300';
      if (lbl) lbl.textContent = 'Offline';
    }
  }

  MedicallAPI.isOnline().then(online => {
    setApiStatus(online);
    if (!online) return;

    // ── B. Dashboard stats ──────────────────────────────────────────────
    MedicallAPI.getDashboard().then(data => {
      const totalDoctors       = data.total_doctors       ?? data.doctors_count      ?? '—';
      const totalPatients      = data.total_patients      ?? data.patients_count     ?? '—';
      const todayAppointments  = data.today_appointments  ?? data.appointments_today ?? '—';

      const el = (id, val) => {
        const node = document.getElementById(id);
        if (node) node.textContent = val;
      };
      el('stat-doctors',      totalDoctors);
      el('stat-patients',     totalPatients);
      el('stat-appointments', todayAppointments);
    }).catch(() => {});

    // ── C. Doctors live list ────────────────────────────────────────────
    MedicallAPI.getDoctors().then(doctors => {
      const grid = document.getElementById('doctorsLiveGrid');
      if (!grid || !doctors || !doctors.length) return;

      grid.innerHTML = doctors.map(doc => {
        const initials = doc.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
        const spec     = doc.specialization || doc.speciality || 'General';
        const avail    = doc.is_available !== false ? 'Available' : 'Busy';
        const dotCls   = doc.is_available !== false ? 'bg-emerald-400' : 'bg-amber-400';
        return `
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 hover:shadow-md transition-all">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#1d68d8] to-[#0d9488]
                        flex items-center justify-center text-white font-outfit font-bold text-sm flex-shrink-0">
              ${initials}
            </div>
            <div class="min-w-0">
              <p class="font-semibold text-[#091e36] text-sm truncate">${doc.name}</p>
              <p class="text-xs text-slate-500 truncate">${spec}</p>
            </div>
          </div>
          <div class="flex items-center gap-1.5 mt-1">
            <span class="w-2 h-2 rounded-full ${dotCls} flex-shrink-0"></span>
            <span class="text-xs text-slate-500">${avail} today</span>
          </div>
        </div>`;
      }).join('');

      // Show the doctors section
      const section = document.getElementById('doctorsLiveSection');
      if (section) section.classList.remove('hidden');
    }).catch(() => {});

  });
})();

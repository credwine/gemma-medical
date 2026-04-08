/* ============================================
   GEMMA MEDICAL -- Hospital Management System
   Application Logic
   ============================================ */

// ============================================
// STATE
// ============================================
const APP = {
    currentPage: 'dashboard',
    currentPatientId: null,
    patients: [],
    settings: {
        clinicName: '',
        workerName: '',
        model: 'gemma3:12b-it-qat',
        language: 'en',
    },
    aiConversationHistory: [],
    dashboardAiHistory: [],
    clinicImageBase64: '',
    drugImageBase64: '',
    debounceTimers: {},
    aiConsultationCount: 0,
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadSettings();
    checkHealth();
    loadDashboard();
    populatePatientSelectors();
    initKeyboardShortcuts();
    initAiInputHandlers();
    if (window.lucide) lucide.createIcons();
});

// ============================================
// NAVIGATION
// ============================================
function switchPage(page) {
    APP.currentPage = page;

    // Update sidebar nav
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page);
    });

    // Update mobile nav
    document.querySelectorAll('.mobile-nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page);
    });

    // Update pages
    document.querySelectorAll('.page').forEach(el => {
        el.classList.toggle('active', el.id === 'page-' + page);
    });

    // Update breadcrumb
    const names = {
        dashboard: 'Dashboard',
        patients: 'Patients',
        clinic: 'Clinic Copilot',
        drugs: 'Drug Checker',
        maternal: 'Maternal Health',
        translator: 'Translator',
        settings: 'Settings',
    };
    const bc = document.getElementById('breadcrumbCurrent');
    if (bc) bc.textContent = names[page] || page;

    // Close mobile sidebar
    closeMobileSidebar();

    // Page-specific loads
    if (page === 'dashboard') loadDashboard();
    if (page === 'patients') loadPatients();
    if (page === 'clinic' || page === 'drugs' || page === 'maternal') populatePatientSelectors();

    // Reset sub-views for patients
    if (page === 'patients') {
        showPatientList();
    }

    // Re-init icons
    setTimeout(() => { if (window.lucide) lucide.createIcons(); }, 50);
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('open');
}

function closeMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('open');
}

// ============================================
// THEME
// ============================================
function initTheme() {
    const saved = localStorage.getItem('gemma-theme');
    if (saved === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    updateThemeIcons();
}

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (isDark) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('gemma-theme', 'light');
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('gemma-theme', 'dark');
    }
    updateThemeIcons();
}

function updateThemeIcons() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('.theme-icon-dark').forEach(el => {
        el.style.display = isDark ? 'none' : 'inline-flex';
    });
    document.querySelectorAll('.theme-icon-light').forEach(el => {
        el.style.display = isDark ? 'inline-flex' : 'none';
    });
}

// ============================================
// LANGUAGE
// ============================================
function changeLanguage(lang) {
    APP.settings.language = lang;
    // Sync selectors
    const topbar = document.getElementById('languageSelector');
    const settings = document.getElementById('settingsLanguage');
    if (topbar) topbar.value = lang;
    if (settings) settings.value = lang;
    saveSettings();
}

// ============================================
// HEALTH CHECK
// ============================================
async function checkHealth() {
    const statusEl = document.getElementById('sidebarStatus');
    const badgeEl = document.getElementById('gemmaReadyBadge');
    try {
        const res = await fetch('/health');
        const data = await res.json();
        if (data.model_status && data.model_status.gemma4_ready) {
            if (statusEl) {
                statusEl.innerHTML = '<span class="status-dot status-dot-ok"></span><span class="status-label">Gemma 4 Online</span>';
            }
            if (badgeEl) badgeEl.style.opacity = '1';
        } else {
            if (statusEl) {
                statusEl.innerHTML = '<span class="status-dot status-dot-error"></span><span class="status-label">Gemma 4 Unavailable</span>';
            }
            if (badgeEl) badgeEl.style.opacity = '0.4';
        }
    } catch (e) {
        if (statusEl) {
            statusEl.innerHTML = '<span class="status-dot status-dot-error"></span><span class="status-label">Server Offline</span>';
        }
        if (badgeEl) badgeEl.style.opacity = '0.4';
    }

    // Re-check every 30 seconds
    setTimeout(checkHealth, 30000);
}

// ============================================
// DASHBOARD
// ============================================
async function loadDashboard() {
    try {
        // Try analytics endpoint first
        const [patientsRes, visitsRes] = await Promise.allSettled([
            fetch('/api/patients'),
            fetch('/api/visits?today=true'),
        ]);

        let patientCount = '--';
        let visitCount = '--';
        let recentVisits = [];

        if (patientsRes.status === 'fulfilled' && patientsRes.value.ok) {
            const patients = await patientsRes.value.json();
            patientCount = Array.isArray(patients) ? patients.length : 0;
            APP.patients = Array.isArray(patients) ? patients : [];
        }

        if (visitsRes.status === 'fulfilled' && visitsRes.value.ok) {
            const visits = await visitsRes.value.json();
            recentVisits = Array.isArray(visits) ? visits : [];
            // Count today's visits
            const today = new Date().toISOString().split('T')[0];
            visitCount = recentVisits.filter(v =>
                (v.visit_date || '').startsWith(today)
            ).length;
        }

        // Update stat cards
        setStatValue('statPatients', patientCount);
        setStatValue('statVisits', visitCount);
        setStatValue('statAI', APP.aiConsultationCount);
        setStatValue('statAlerts', 0);

        // Populate recent activity
        renderRecentActivity(recentVisits.slice(0, 10));

    } catch (e) {
        console.warn('[Dashboard] Load error:', e);
        setStatValue('statPatients', '--');
        setStatValue('statVisits', '--');
        setStatValue('statAI', APP.aiConsultationCount);
        setStatValue('statAlerts', '--');
    }
}

function setStatValue(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function renderRecentActivity(visits) {
    const tbody = document.getElementById('recentActivityBody');
    if (!tbody) return;

    if (!visits.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="table-empty">No recent visits recorded</td></tr>';
        return;
    }

    tbody.innerHTML = visits.map(v => {
        const date = v.visit_date ? new Date(v.visit_date).toLocaleDateString() : '--';
        const patient = findPatientName(v.patient_id);
        const complaint = escapeHtml(v.chief_complaint || v.symptoms || '--').substring(0, 60);
        const diagnosis = escapeHtml(v.diagnosis || '--').substring(0, 60);
        return `<tr>
            <td>${date}</td>
            <td>${patient}</td>
            <td>${complaint}</td>
            <td>${diagnosis}</td>
        </tr>`;
    }).join('');
}

function findPatientName(patientId) {
    const p = APP.patients.find(pt => pt.patient_id === patientId);
    if (p) return escapeHtml((p.first_name || '') + ' ' + (p.last_name || ''));
    return patientId ? patientId.substring(0, 8) + '...' : '--';
}

// ============================================
// DASHBOARD AI QUICK CHAT
// ============================================
async function sendDashboardAi() {
    const input = document.getElementById('dashboardAiInput');
    const messages = document.getElementById('dashboardAiMessages');
    if (!input || !messages) return;

    const text = input.value.trim();
    if (!text) return;
    input.value = '';

    // Add user message
    const userEl = document.createElement('div');
    userEl.className = 'ai-quick-msg ai-quick-user';
    userEl.textContent = text;
    messages.appendChild(userEl);

    // Add loading
    const loadingEl = document.createElement('div');
    loadingEl.className = 'ai-quick-msg ai-quick-bot ai-quick-loading';
    loadingEl.textContent = 'Thinking...';
    messages.appendChild(loadingEl);
    messages.scrollTop = messages.scrollHeight;

    APP.dashboardAiHistory.push({ role: 'user', content: text });

    try {
        const res = await fetch('/api/assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                history: APP.dashboardAiHistory.slice(0, -1),
                language: APP.settings.language,
            }),
        });

        const data = await res.json();
        const reply = data.response || 'Unable to generate a response.';
        loadingEl.textContent = reply;
        loadingEl.classList.remove('ai-quick-loading');
        APP.dashboardAiHistory.push({ role: 'assistant', content: reply });
        APP.aiConsultationCount++;
    } catch (e) {
        loadingEl.textContent = 'Could not reach Gemma 4. Ensure Ollama is running.';
        loadingEl.classList.remove('ai-quick-loading');
    }

    messages.scrollTop = messages.scrollHeight;
}

// ============================================
// PATIENTS
// ============================================
async function loadPatients(query) {
    try {
        const url = query ? `/api/patients?search=${encodeURIComponent(query)}` : '/api/patients';
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to load patients');
        const patients = await res.json();
        APP.patients = Array.isArray(patients) ? patients : [];
        renderPatientsTable(APP.patients);
    } catch (e) {
        console.warn('[Patients] Load error:', e);
        renderPatientsTable([]);
    }
}

function searchPatients(query) {
    clearTimeout(APP.debounceTimers.patientSearch);
    APP.debounceTimers.patientSearch = setTimeout(() => {
        loadPatients(query);
    }, 300);
}

function renderPatientsTable(patients) {
    const tbody = document.getElementById('patientsBody');
    if (!tbody) return;

    if (!patients.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="table-empty">No patients found. Register a new patient to get started.</td></tr>';
        return;
    }

    tbody.innerHTML = patients.map(p => {
        const age = calcAge(p.date_of_birth);
        const lastVisit = p.last_visit ? new Date(p.last_visit).toLocaleDateString() : 'Never';
        const conditions = (p.chronic_conditions || []).slice(0, 2).map(c =>
            `<span class="condition-tag">${escapeHtml(c)}</span>`
        ).join('');
        const shortId = (p.patient_id || '').substring(0, 8);

        return `<tr>
            <td class="patient-id-cell">${shortId}</td>
            <td><strong>${escapeHtml(p.first_name || '')} ${escapeHtml(p.last_name || '')}</strong></td>
            <td>${age}</td>
            <td>${capitalize(p.sex || '--')}</td>
            <td>${lastVisit}</td>
            <td>${conditions || '<span class="text-muted">None</span>'}</td>
            <td class="table-actions">
                <button class="table-btn" onclick="viewPatient('${p.patient_id}')">View</button>
                <button class="table-btn" onclick="editPatient('${p.patient_id}')">Edit</button>
            </td>
        </tr>`;
    }).join('');
}

// Patient Form
function openPatientForm(patientId) {
    document.getElementById('patientListView').style.display = 'none';
    document.getElementById('patientDetailView').style.display = 'none';
    document.getElementById('patientFormView').style.display = 'block';

    const form = document.getElementById('patientForm');
    if (form) form.reset();
    document.getElementById('patientEditId').value = '';

    if (patientId) {
        // Edit mode
        const p = APP.patients.find(pt => pt.patient_id === patientId);
        if (p) {
            document.getElementById('patientFormTitle').textContent = 'Edit Patient';
            document.getElementById('patientFormSubmitBtn').innerHTML = '<i data-lucide="save"></i> Update Patient';
            document.getElementById('patientEditId').value = p.patient_id;
            document.getElementById('pfFirstName').value = p.first_name || '';
            document.getElementById('pfLastName').value = p.last_name || '';
            document.getElementById('pfDob').value = p.date_of_birth || '';
            document.getElementById('pfSex').value = p.sex || '';
            document.getElementById('pfBloodType').value = p.blood_type || '';
            document.getElementById('pfAddress').value = p.village_or_address || '';
            document.getElementById('pfAllergies').value = (p.allergies || []).join(', ');
            document.getElementById('pfConditions').value = (p.chronic_conditions || []).join(', ');
            document.getElementById('pfEmergencyName').value = p.emergency_contact_name || '';
            document.getElementById('pfEmergencyPhone').value = p.emergency_contact_phone || '';
            document.getElementById('pfNotes').value = p.notes || '';
        }
    } else {
        document.getElementById('patientFormTitle').textContent = 'Register New Patient';
        document.getElementById('patientFormSubmitBtn').innerHTML = '<i data-lucide="save"></i> Register Patient';
    }

    setTimeout(() => { if (window.lucide) lucide.createIcons(); }, 50);
}

function closePatientForm() {
    document.getElementById('patientFormView').style.display = 'none';
    showPatientList();
}

async function submitPatientForm(e) {
    e.preventDefault();
    const editId = document.getElementById('patientEditId').value;
    const data = {
        first_name: document.getElementById('pfFirstName').value.trim(),
        last_name: document.getElementById('pfLastName').value.trim(),
        date_of_birth: document.getElementById('pfDob').value,
        sex: document.getElementById('pfSex').value,
        blood_type: document.getElementById('pfBloodType').value,
        village_or_address: document.getElementById('pfAddress').value.trim(),
        allergies: document.getElementById('pfAllergies').value.split(',').map(s => s.trim()).filter(Boolean),
        chronic_conditions: document.getElementById('pfConditions').value.split(',').map(s => s.trim()).filter(Boolean),
        emergency_contact_name: document.getElementById('pfEmergencyName').value.trim(),
        emergency_contact_phone: document.getElementById('pfEmergencyPhone').value.trim(),
        notes: document.getElementById('pfNotes').value.trim(),
    };

    try {
        let res;
        if (editId) {
            res = await fetch(`/api/patients/${editId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        } else {
            res = await fetch('/api/patients', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        }

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Failed to save patient');
        }

        showToast(editId ? 'Patient updated successfully' : 'Patient registered successfully', 'success');
        closePatientForm();
        loadPatients();
        populatePatientSelectors();
    } catch (e) {
        showToast('Error: ' + e.message, 'error');
    }
}

function editPatient(id) {
    openPatientForm(id);
}

function editCurrentPatient() {
    if (APP.currentPatientId) {
        openPatientForm(APP.currentPatientId);
    }
}

function showPatientList() {
    document.getElementById('patientListView').style.display = 'block';
    document.getElementById('patientFormView').style.display = 'none';
    document.getElementById('patientDetailView').style.display = 'none';
}

// Patient Detail
async function viewPatient(id) {
    APP.currentPatientId = id;

    document.getElementById('patientListView').style.display = 'none';
    document.getElementById('patientFormView').style.display = 'none';
    document.getElementById('patientDetailView').style.display = 'block';

    const p = APP.patients.find(pt => pt.patient_id === id);
    if (!p) {
        // Fetch from API
        try {
            const res = await fetch(`/api/patients/${id}`);
            if (res.ok) {
                const patient = await res.json();
                renderPatientDetail(patient);
            }
        } catch (e) {
            showToast('Could not load patient', 'error');
        }
        return;
    }

    renderPatientDetail(p);

    // Load visits and medications in parallel
    loadPatientVisits(id);
    loadPatientMedications(id);
}

function renderPatientDetail(p) {
    const container = document.getElementById('patientProfile');
    if (!container) return;

    const age = calcAge(p.date_of_birth);
    const initials = ((p.first_name || '')[0] || '') + ((p.last_name || '')[0] || '');
    const allergies = (p.allergies || []).join(', ') || 'None reported';
    const conditions = (p.chronic_conditions || []).join(', ') || 'None reported';
    const registered = p.registered_date ? new Date(p.registered_date).toLocaleDateString() : '--';

    container.innerHTML = `
        <div class="profile-top">
            <div class="profile-avatar">${initials.toUpperCase()}</div>
            <div class="profile-info">
                <h2>${escapeHtml(p.first_name || '')} ${escapeHtml(p.last_name || '')}</h2>
                <div class="profile-meta">
                    <span>Age: ${age}</span>
                    <span>Sex: ${capitalize(p.sex || '--')}</span>
                    <span>Blood: ${p.blood_type || 'Unknown'}</span>
                    <span>ID: ${(p.patient_id || '').substring(0, 8)}</span>
                </div>
            </div>
        </div>
        <div class="profile-grid">
            <div class="profile-field">
                <span class="profile-field-label">Address</span>
                <span class="profile-field-value">${escapeHtml(p.village_or_address || '--')}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Registered</span>
                <span class="profile-field-value">${registered}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Allergies</span>
                <span class="profile-field-value">${escapeHtml(allergies)}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Chronic Conditions</span>
                <span class="profile-field-value">${escapeHtml(conditions)}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Emergency Contact</span>
                <span class="profile-field-value">${escapeHtml(p.emergency_contact_name || '--')} ${p.emergency_contact_phone || ''}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Notes</span>
                <span class="profile-field-value">${escapeHtml(p.notes || 'None')}</span>
            </div>
        </div>
    `;
}

function closePatientDetail() {
    APP.currentPatientId = null;
    showPatientList();
}

async function loadPatientVisits(patientId) {
    const tbody = document.getElementById('patientVisitsBody');
    if (!tbody) return;

    try {
        const res = await fetch(`/api/visits?patient_id=${patientId}`);
        if (!res.ok) throw new Error();
        const visits = await res.json();

        if (!visits.length) {
            tbody.innerHTML = '<tr><td colspan="4" class="table-empty">No visits recorded</td></tr>';
            return;
        }

        tbody.innerHTML = visits.map(v => {
            const date = v.visit_date ? new Date(v.visit_date).toLocaleDateString() : '--';
            return `<tr>
                <td>${date}</td>
                <td>${escapeHtml(v.chief_complaint || v.symptoms || '--')}</td>
                <td>${escapeHtml(v.diagnosis || '--')}</td>
                <td>${escapeHtml(v.treatment_plan || '--')}</td>
            </tr>`;
        }).join('');

        // Also populate AI history from visits with ai_assessment
        renderAiHistoryFromVisits(visits);

    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="4" class="table-empty">Could not load visits</td></tr>';
    }
}

async function loadPatientMedications(patientId) {
    const tbody = document.getElementById('patientMedsBody');
    if (!tbody) return;

    try {
        const res = await fetch(`/api/medications?patient_id=${patientId}`);
        if (!res.ok) throw new Error();
        const meds = await res.json();

        if (!meds.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="table-empty">No medications recorded</td></tr>';
            return;
        }

        tbody.innerHTML = meds.map(m => {
            const status = m.end_date ? `<span class="text-muted">Ended ${m.end_date}</span>` : '<span class="text-success">Active</span>';
            return `<tr>
                <td><strong>${escapeHtml(m.medication_name || '--')}</strong></td>
                <td>${escapeHtml(m.dosage || '--')}</td>
                <td>${escapeHtml(m.frequency || '--')}</td>
                <td>${m.start_date || '--'}</td>
                <td>${status}</td>
            </tr>`;
        }).join('');
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Could not load medications</td></tr>';
    }
}

function renderAiHistoryFromVisits(visits) {
    const container = document.getElementById('patientAiHistory');
    if (!container) return;

    const withAi = visits.filter(v => v.ai_assessment && Object.keys(v.ai_assessment).length > 0);

    if (!withAi.length) {
        container.innerHTML = '<p class="table-empty">No AI assessments recorded</p>';
        return;
    }

    container.innerHTML = withAi.map(v => {
        const date = v.visit_date ? new Date(v.visit_date).toLocaleString() : '--';
        const src = v.ai_assessment.source || 'AI';
        const srcLabel = src.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        let body = '';
        if (v.ai_assessment.result && typeof v.ai_assessment.result === 'string') {
            body = v.ai_assessment.result.replace(/\\n/g, '<br>').replace(/\n/g, '<br>');
        } else if (typeof v.ai_assessment === 'string') {
            body = v.ai_assessment.replace(/\\n/g, '<br>').replace(/\n/g, '<br>');
        } else {
            body = formatAiText(JSON.stringify(v.ai_assessment, null, 2));
        }
        return `<div class="ai-history-card">
            <div class="ai-history-card-header">
                <span class="ai-history-card-date">${date}</span>
                <span class="ai-history-card-type">${escapeHtml(srcLabel)}</span>
            </div>
            <div class="ai-history-card-body" style="white-space:pre-wrap;line-height:1.6;">${body}</div>
        </div>`;
    }).join('');
}

function switchPatientTab(tab) {
    document.querySelectorAll('.ptab').forEach(el => {
        el.classList.toggle('active', el.dataset.ptab === tab);
    });
    document.querySelectorAll('.ptab-content').forEach(el => {
        el.classList.toggle('active', el.id === 'ptab-' + tab);
    });
}

// Run AI assessment from patient detail
function runAiAssessmentForPatient() {
    if (!APP.currentPatientId) return;
    const p = APP.patients.find(pt => pt.patient_id === APP.currentPatientId);
    if (p) {
        // Switch to clinic page with patient pre-selected
        switchPage('clinic');
        setTimeout(() => {
            const sel = document.getElementById('clinicPatientSelect');
            if (sel) {
                sel.value = p.patient_id;
                onClinicPatientSelect(p.patient_id);
            }
        }, 100);
    }
}

// ============================================
// PATIENT SELECTORS (for CDSS tools)
// ============================================
async function populatePatientSelectors() {
    // Ensure we have patients loaded
    if (!APP.patients.length) {
        try {
            const res = await fetch('/api/patients');
            if (res.ok) {
                APP.patients = await res.json();
            }
        } catch (e) { /* silent */ }
    }

    const selectors = ['clinicPatientSelect', 'drugPatientSelect', 'maternalPatientSelect'];
    selectors.forEach(selId => {
        const sel = document.getElementById(selId);
        if (!sel) return;
        const current = sel.value;
        sel.innerHTML = '<option value="">-- No patient linked --</option>';
        APP.patients.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.patient_id;
            opt.textContent = `${p.first_name || ''} ${p.last_name || ''} (${(p.patient_id || '').substring(0, 8)})`;
            sel.appendChild(opt);
        });
        if (current) sel.value = current;
    });
}

function getSelectedPatient(selectId) {
    const sel = document.getElementById(selectId);
    if (!sel || !sel.value) return null;
    return APP.patients.find(p => p.patient_id === sel.value) || null;
}

function onClinicPatientSelect(patientId) {
    if (!patientId) return;
    const p = APP.patients.find(pt => pt.patient_id === patientId);
    if (!p) return;

    // Auto-fill age and sex
    const ageGroup = dobToAgeGroup(p.date_of_birth);
    if (ageGroup) document.getElementById('clinicAge').value = ageGroup;
    if (p.sex) document.getElementById('clinicSex').value = p.sex;

    // Add context to symptoms
    const conditions = (p.chronic_conditions || []).join(', ');
    const allergies = (p.allergies || []).join(', ');
    let context = '';
    if (conditions) context += `Known conditions: ${conditions}. `;
    if (allergies) context += `Allergies: ${allergies}. `;

    const symptoms = document.getElementById('clinicSymptoms');
    if (symptoms && context && !symptoms.value.includes('Known conditions')) {
        symptoms.value = context + '\n' + symptoms.value;
    }
}

async function onDrugPatientSelect(patientId) {
    if (!patientId) return;
    const p = APP.patients.find(pt => pt.patient_id === patientId);
    if (!p) return;

    // Auto-fill conditions
    const conditionsField = document.getElementById('drugConditions');
    if (conditionsField && p.chronic_conditions && p.chronic_conditions.length) {
        conditionsField.value = p.chronic_conditions.join(', ');
    }

    // Load active medications
    try {
        const res = await fetch(`/api/medications?patient_id=${patientId}&active=true`);
        if (res.ok) {
            const meds = await res.json();
            if (meds.length) {
                const medsField = document.getElementById('drugMedications');
                if (medsField) {
                    medsField.value = meds.map(m => {
                        let line = m.medication_name || '';
                        if (m.dosage) line += ' ' + m.dosage;
                        return line;
                    }).join('\n');
                }
            }
        }
    } catch (e) { /* silent */ }
}

function onMaternalPatientSelect(patientId) {
    if (!patientId) return;
    const p = APP.patients.find(pt => pt.patient_id === patientId);
    if (!p) return;

    // Fill in history
    const historyField = document.getElementById('maternalHistory');
    if (historyField) {
        let history = '';
        if (p.chronic_conditions && p.chronic_conditions.length) {
            history += 'Conditions: ' + p.chronic_conditions.join(', ') + '. ';
        }
        if (p.allergies && p.allergies.length) {
            history += 'Allergies: ' + p.allergies.join(', ') + '.';
        }
        if (history) historyField.value = history;
    }
}

// ============================================
// CLINIC COPILOT
// ============================================
async function runClinic() {
    const symptoms = document.getElementById('clinicSymptoms').value.trim();
    const age = document.getElementById('clinicAge').value;
    const sex = document.getElementById('clinicSex').value;

    if (!symptoms) {
        showToast('Please describe the symptoms', 'warning');
        return;
    }

    const btn = document.getElementById('clinicBtn');
    const resultPanel = document.getElementById('clinicResult');

    setBtnLoading(btn, true, 'Analyzing...');
    resultPanel.innerHTML = `
        <div class="ai-loading-container">
            <div class="ai-progress-bar"><div class="ai-progress-bar-fill"></div></div>
            <div class="ai-loading-title">Analyzing with Gemma 4...</div>
            <div class="ai-loading-subtitle">The AI is reasoning through the symptoms locally on your device.</div>
        </div>`;

    try {
        const res = await fetch('/api/clinic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symptoms,
                patient_age: age,
                patient_sex: sex,
                image: APP.clinicImageBase64,
                language: APP.settings.language,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Analysis failed');
        }

        const data = await res.json();
        APP.aiConsultationCount++;
        renderClinicResult(resultPanel, data);

    } catch (e) {
        resultPanel.innerHTML = `<div class="result-empty"><h3 class="text-danger">Error</h3><p>${escapeHtml(e.message)}</p></div>`;
    } finally {
        setBtnLoading(btn, false, '<i data-lucide="stethoscope"></i> Analyze with Gemma 4');
    }
}

function renderClinicResult(container, data) {
    const selectedPatient = getSelectedPatient('clinicPatientSelect');

    let html = `
        <div class="result-header">
            <h3>Clinic Copilot Analysis</h3>
            <span class="ai-inline-badge">Powered by Gemma 4</span>
        </div>
    `;

    // Structured response rendering
    if (data.possible_conditions && Array.isArray(data.possible_conditions)) {
        // Referral urgency banner
        const urgency = (data.referral_urgency || 'routine').toLowerCase();
        const urgencyColors = { emergency: 'var(--severity-emergency)', urgent: 'var(--severity-high)', routine: 'var(--severity-moderate)', 'self-care': 'var(--severity-low)' };
        const urgencyColor = urgencyColors[urgency] || 'var(--severity-moderate)';
        html += `<div class="severity-banner" style="background:${urgencyColor};color:white;padding:12px 16px;border-radius:8px;margin-bottom:16px;font-weight:700;text-transform:uppercase;">Referral: ${escapeHtml(data.referral_urgency || 'Routine')}</div>`;

        // Possible conditions
        html += `<div class="result-section"><div class="result-section-title">Possible Conditions</div>`;
        data.possible_conditions.forEach(c => {
            const lk = (c.likelihood || 'moderate').toLowerCase();
            const badge = lk === 'high' ? 'severity-emergency' : lk === 'moderate' ? 'severity-moderate' : 'severity-low';
            html += `<div class="clinical-card" style="margin-bottom:8px;padding:12px 16px;border-left:4px solid ${lk === 'high' ? 'var(--severity-emergency)' : lk === 'moderate' ? 'var(--severity-moderate)' : 'var(--severity-low)'};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <strong>${escapeHtml(c.name || '')}</strong>
                    <span class="severity-badge ${badge}">${escapeHtml(c.likelihood || '')}</span>
                </div>
                <div style="font-size:0.9rem;color:var(--text-secondary);">${escapeHtml(c.description || '')}</div>
            </div>`;
        });
        html += `</div>`;

        // Red flags
        if (data.red_flags && data.red_flags.length > 0) {
            html += `<div class="result-section"><div class="result-section-title">Red Flags</div>`;
            data.red_flags.forEach(f => {
                html += `<div style="display:flex;align-items:flex-start;gap:8px;padding:8px 12px;background:var(--severity-emergency-bg, #fef2f2);border:1px solid #fecaca;border-radius:6px;margin-bottom:6px;font-size:0.9rem;color:#991b1b;">
                    <span style="flex-shrink:0;">&#9888;</span> ${escapeHtml(f)}
                </div>`;
            });
            html += `</div>`;
        }

        // Recommended actions
        if (data.recommended_actions && data.recommended_actions.length > 0) {
            html += `<div class="result-section"><div class="result-section-title">Recommended Actions</div>`;
            data.recommended_actions.forEach((a, i) => {
                html += `<div style="display:flex;align-items:flex-start;gap:8px;padding:8px 12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;margin-bottom:6px;font-size:0.9rem;">
                    <span style="flex-shrink:0;font-weight:700;color:var(--brand-primary);">${i + 1}.</span> ${escapeHtml(a)}
                </div>`;
            });
            html += `</div>`;
        }

        // Notes
        if (data.notes) {
            html += `<div class="result-section"><div class="result-section-title">Clinical Notes</div>
                <div class="clinical-card" style="padding:12px 16px;font-size:0.9rem;">${escapeHtml(data.notes)}</div>
            </div>`;
        }
    } else if (typeof data === 'string') {
        html += `<div class="result-section"><div class="result-text">${formatAiText(data)}</div></div>`;
    } else {
        html += `<div class="result-section"><div class="result-text">${formatAiText(JSON.stringify(data, null, 2))}</div></div>`;
    }

    // Save to record button
    if (selectedPatient) {
        html += `<button class="save-to-record-btn" onclick="saveClinicToRecord()">
            <i data-lucide="save"></i> Save to Patient Record
        </button>`;
    }

    html += `
        <div class="medical-disclaimer mt-4">
            <i data-lucide="alert-triangle"></i>
            <span>These results were generated by Gemma 4 AI. Always verify with clinical judgment.</span>
        </div>
    `;

    container.innerHTML = html;
    if (window.lucide) lucide.createIcons();
}

async function saveClinicToRecord() {
    const patient = getSelectedPatient('clinicPatientSelect');
    if (!patient) {
        showToast('Select a patient first', 'warning');
        return;
    }

    const symptoms = document.getElementById('clinicSymptoms').value.trim();
    const resultText = document.getElementById('clinicResult').innerText;

    try {
        const res = await fetch('/api/visits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_id: patient.patient_id,
                chief_complaint: symptoms.substring(0, 200),
                symptoms: symptoms,
                diagnosis: 'AI-assisted assessment (see AI assessment)',
                ai_assessment: { source: 'clinic_copilot', result: resultText },
                attending_worker: APP.settings.workerName || 'Health Worker',
            }),
        });

        if (!res.ok) throw new Error('Failed to save visit');
        showToast('Assessment saved to patient record', 'success');
    } catch (e) {
        showToast('Error saving: ' + e.message, 'error');
    }
}

function clearClinic() {
    document.getElementById('clinicSymptoms').value = '';
    document.getElementById('clinicAge').value = '';
    document.getElementById('clinicSex').value = '';
    document.getElementById('clinicPatientSelect').value = '';
    clearClinicImage();
    document.getElementById('clinicResult').innerHTML = `
        <div class="result-empty">
            <i data-lucide="stethoscope"></i>
            <h3>Diagnosis Results</h3>
            <p>Enter symptoms and click "Analyze with Gemma 4" to receive a differential diagnosis.</p>
        </div>`;
    if (window.lucide) lucide.createIcons();
}

// Image handling
function handleClinicImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        APP.clinicImageBase64 = e.target.result.split(',')[1] || '';
        const preview = document.getElementById('clinicImagePreview');
        const img = document.getElementById('clinicPreviewImg');
        if (preview) preview.style.display = 'flex';
        if (img) img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function clearClinicImage() {
    APP.clinicImageBase64 = '';
    const preview = document.getElementById('clinicImagePreview');
    if (preview) preview.style.display = 'none';
    document.getElementById('clinicImage').value = '';
    document.getElementById('clinicCamera').value = '';
}

// ============================================
// DRUG CHECKER
// ============================================
async function runDrugCheck() {
    const medications = document.getElementById('drugMedications').value.trim();
    const conditions = document.getElementById('drugConditions').value.trim();

    if (!medications && !APP.drugImageBase64) {
        showToast('Enter medications or upload an image', 'warning');
        return;
    }

    const btn = document.getElementById('drugBtn');
    const resultPanel = document.getElementById('drugResult');

    setBtnLoading(btn, true, 'Checking...');
    resultPanel.innerHTML = `<div class="ai-loading-container"><div class="ai-progress-bar"><div class="ai-progress-bar-fill"></div></div><div class="ai-loading-title">Checking interactions with Gemma 4...</div><div class="ai-loading-subtitle">Scanning medication database locally on your device.</div></div>`;

    try {
        const res = await fetch('/api/drugs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                medications,
                patient_conditions: conditions,
                image: APP.drugImageBase64,
                language: APP.settings.language,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Drug check failed');
        }

        const data = await res.json();
        APP.aiConsultationCount++;
        renderDrugResult(resultPanel, data);

    } catch (e) {
        resultPanel.innerHTML = `<div class="result-empty"><h3 class="text-danger">Error</h3><p>${escapeHtml(e.message)}</p></div>`;
    } finally {
        setBtnLoading(btn, false, '<i data-lucide="shield-alert"></i> Check with Gemma 4');
    }
}

function renderDrugResult(container, data) {
    const selectedPatient = getSelectedPatient('drugPatientSelect');

    let html = `
        <div class="result-header">
            <h3>Drug Interaction Results</h3>
            <span class="ai-inline-badge">Powered by Gemma 4</span>
        </div>
    `;

    if (data.interactions && Array.isArray(data.interactions)) {
        if (data.interactions.length > 0) {
            html += `<div class="result-section"><div class="result-section-title">Drug Interactions Found</div>`;
            data.interactions.forEach(ix => {
                const sev = (ix.severity || 'moderate').toLowerCase();
                const sevColors = { critical: '#dc2626', major: '#ea580c', moderate: '#f59e0b', minor: '#3b82f6' };
                const color = sevColors[sev] || '#f59e0b';
                html += `<div class="clinical-card" style="margin-bottom:8px;padding:12px 16px;border-left:4px solid ${color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <strong>${escapeHtml(ix.drug_pair || '')}</strong>
                        <span class="severity-badge" style="background:${color};color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:700;text-transform:uppercase;">${escapeHtml(ix.severity || '')}</span>
                    </div>
                    <div style="font-size:0.9rem;color:var(--text-secondary);margin-bottom:4px;">${escapeHtml(ix.description || '')}</div>
                    <div style="font-size:0.85rem;color:var(--brand-primary);font-weight:500;">${escapeHtml(ix.recommendation || '')}</div>
                </div>`;
            });
            html += `</div>`;
        } else {
            html += `<div class="result-section"><div class="clinical-card" style="border-left:4px solid var(--severity-low);padding:12px 16px;">No dangerous interactions detected between these medications.</div></div>`;
        }
        if (data.warnings && data.warnings.length > 0) {
            html += `<div class="result-section"><div class="result-section-title">Warnings</div>`;
            data.warnings.forEach(w => { html += `<div style="padding:6px 12px;background:#fffbeb;border:1px solid #fed7aa;border-radius:6px;margin-bottom:4px;font-size:0.9rem;">${escapeHtml(w)}</div>`; });
            html += `</div>`;
        }
        if (data.notes) { html += `<div class="result-section"><div class="clinical-card" style="padding:12px 16px;font-size:0.9rem;">${escapeHtml(data.notes)}</div></div>`; }
    } else {
        html += `<div class="result-section"><div class="result-text">${formatAiText(typeof data === 'string' ? data : JSON.stringify(data, null, 2))}</div></div>`;
    }

    html += `
        <div class="medical-disclaimer mt-4">
            <i data-lucide="alert-triangle"></i>
            <span>These interactions were flagged by Gemma 4 AI. Always verify with a pharmacist or clinical reference.</span>
        </div>
    `;

    if (selectedPatient) {
        html += `<button class="save-to-record-btn" onclick="saveDrugCheckToRecord()">
            <i data-lucide="save"></i> Save to Patient Record
        </button>`;
    }

    container.innerHTML = html;
    if (window.lucide) lucide.createIcons();
}

async function saveDrugCheckToRecord() {
    const patient = getSelectedPatient('drugPatientSelect');
    if (!patient) {
        showToast('Select a patient first', 'warning');
        return;
    }

    const meds = document.getElementById('drugMedications').value.trim();
    const resultText = document.getElementById('drugResult').innerText;

    try {
        const res = await fetch('/api/visits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_id: patient.patient_id,
                chief_complaint: 'Drug interaction check',
                symptoms: 'Medications: ' + meds,
                diagnosis: 'Drug interaction analysis (AI-assisted)',
                ai_assessment: { source: 'drug_checker', result: resultText },
                attending_worker: APP.settings.workerName || 'Health Worker',
            }),
        });

        if (!res.ok) throw new Error('Failed to save');
        showToast('Drug check saved to patient record', 'success');
    } catch (e) {
        showToast('Error: ' + e.message, 'error');
    }
}

function clearDrugs() {
    document.getElementById('drugMedications').value = '';
    document.getElementById('drugConditions').value = '';
    document.getElementById('drugPatientSelect').value = '';
    clearDrugImage();
    document.getElementById('drugResult').innerHTML = `
        <div class="result-empty">
            <i data-lucide="pill"></i>
            <h3>Interaction Results</h3>
            <p>Enter medications and click "Check with Gemma 4" to identify dangerous interactions.</p>
        </div>`;
    if (window.lucide) lucide.createIcons();
}

function handleDrugImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        APP.drugImageBase64 = e.target.result.split(',')[1] || '';
        const preview = document.getElementById('drugImagePreview');
        const img = document.getElementById('drugPreviewImg');
        if (preview) preview.style.display = 'flex';
        if (img) img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function clearDrugImage() {
    APP.drugImageBase64 = '';
    const preview = document.getElementById('drugImagePreview');
    if (preview) preview.style.display = 'none';
    document.getElementById('drugImage').value = '';
    document.getElementById('drugCamera').value = '';
}

// ============================================
// MATERNAL HEALTH
// ============================================
async function runMaternal() {
    const weeks = parseInt(document.getElementById('maternalWeeks').value);
    const symptoms = document.getElementById('maternalSymptoms').value.trim();
    const vitals = document.getElementById('maternalVitals').value.trim();
    const history = document.getElementById('maternalHistory').value.trim();

    if (!symptoms) {
        showToast('Please describe the symptoms', 'warning');
        return;
    }
    if (!weeks || weeks < 1 || weeks > 42) {
        showToast('Enter gestational weeks (1-42)', 'warning');
        return;
    }

    const btn = document.getElementById('maternalBtn');
    const resultPanel = document.getElementById('maternalResult');

    setBtnLoading(btn, true, 'Assessing...');
    resultPanel.innerHTML = `<div class="ai-loading-container"><div class="ai-progress-bar"><div class="ai-progress-bar-fill"></div></div><div class="ai-loading-title">Assessing maternal risk with Gemma 4...</div><div class="ai-loading-subtitle">Evaluating risk factors following WHO guidelines.</div></div>`;

    try {
        const res = await fetch('/api/maternal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                gestational_weeks: weeks,
                symptoms,
                vitals,
                history,
                language: APP.settings.language,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Assessment failed');
        }

        const data = await res.json();
        APP.aiConsultationCount++;
        renderMaternalResult(resultPanel, data);

    } catch (e) {
        resultPanel.innerHTML = `<div class="result-empty"><h3 class="text-danger">Error</h3><p>${escapeHtml(e.message)}</p></div>`;
    } finally {
        setBtnLoading(btn, false, '<i data-lucide="heart-pulse"></i> Assess with Gemma 4');
    }
}

function renderMaternalResult(container, data) {
    const selectedPatient = getSelectedPatient('maternalPatientSelect');

    let html = `
        <div class="result-header">
            <h3>Maternal Health Assessment</h3>
            <span class="ai-inline-badge">Powered by Gemma 4</span>
        </div>
    `;

    // Try to detect risk level from response for color-coded banner
    const content = data.response || data.assessment || data.analysis || data;
    const contentStr = typeof content === 'string' ? content : JSON.stringify(content);
    const lower = contentStr.toLowerCase();

    let riskClass = 'severity-banner-moderate';
    let riskLabel = 'Risk Assessment';
    if (lower.includes('emergency') || lower.includes('critical') || lower.includes('immediate')) {
        riskClass = 'severity-banner-emergency';
        riskLabel = 'EMERGENCY -- Immediate Action Required';
    } else if (lower.includes('high risk') || lower.includes('high-risk') || lower.includes('severe')) {
        riskClass = 'severity-banner-high';
        riskLabel = 'HIGH RISK -- Urgent Referral Needed';
    } else if (lower.includes('moderate') || lower.includes('medium')) {
        riskClass = 'severity-banner-moderate';
        riskLabel = 'MODERATE RISK -- Close Monitoring Required';
    } else if (lower.includes('low risk') || lower.includes('low-risk') || lower.includes('normal')) {
        riskClass = 'severity-banner-low';
        riskLabel = 'LOW RISK -- Continue Standard Care';
    }

    // Use structured data if available
    if (data.risk_level) {
        const rl = data.risk_level.toLowerCase();
        const rlColors = { emergency: '#dc2626', high: '#ea580c', moderate: '#f59e0b', low: '#16a34a' };
        const rlColor = rlColors[rl] || '#f59e0b';
        html += `<div style="background:${rlColor};color:white;padding:16px;border-radius:8px;margin-bottom:16px;text-align:center;font-size:1.3rem;font-weight:800;text-transform:uppercase;">${escapeHtml(data.risk_level)} RISK</div>`;
    } else {
        html += `<div class="severity-banner ${riskClass}">${riskLabel}</div>`;
    }

    if (data.risk_factors && Array.isArray(data.risk_factors)) {
        html += `<div class="result-section"><div class="result-section-title">Risk Factors</div>`;
        data.risk_factors.forEach(rf => {
            html += `<div class="clinical-card" style="margin-bottom:8px;padding:12px 16px;border-left:4px solid #ea580c;">
                <strong>${escapeHtml(rf.factor || '')}</strong>
                <div style="font-size:0.9rem;color:var(--text-secondary);">${escapeHtml(rf.explanation || '')}</div>
            </div>`;
        });
        html += `</div>`;
    }

    if (data.immediate_actions && data.immediate_actions.length > 0) {
        html += `<div class="result-section"><div class="result-section-title">Immediate Actions</div>`;
        data.immediate_actions.forEach((a, i) => {
            html += `<div style="display:flex;gap:8px;padding:8px 12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;margin-bottom:6px;font-size:0.9rem;">
                <span style="font-weight:700;color:var(--brand-primary);">${i + 1}.</span> ${escapeHtml(a)}
            </div>`;
        });
        html += `</div>`;
    }

    if (data.danger_signs_to_watch && data.danger_signs_to_watch.length > 0) {
        html += `<div class="result-section"><div class="result-section-title">Danger Signs to Watch</div>`;
        data.danger_signs_to_watch.forEach(d => {
            html += `<div style="display:flex;align-items:flex-start;gap:8px;padding:8px 12px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;margin-bottom:6px;font-size:0.9rem;color:#991b1b;">&#9888; ${escapeHtml(d)}</div>`;
        });
        html += `</div>`;
    }

    if (data.monitoring_plan && data.monitoring_plan.length > 0) {
        html += `<div class="result-section"><div class="result-section-title">Monitoring Plan</div>`;
        data.monitoring_plan.forEach(m => {
            html += `<div style="padding:6px 12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;margin-bottom:4px;font-size:0.9rem;">${escapeHtml(m)}</div>`;
        });
        html += `</div>`;
    }

    if (data.notes) {
        html += `<div class="result-section"><div class="clinical-card" style="padding:12px 16px;font-size:0.9rem;">${escapeHtml(data.notes)}</div></div>`;
    }

    if (!data.risk_level && !data.risk_factors) {
        // Fallback for unstructured response
        const txt = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
        html += `<div class="result-section"><div class="result-text">${formatAiText(txt)}</div></div>`;
    }

    if (selectedPatient) {
        html += `<button class="save-to-record-btn" onclick="saveMaternalToRecord()">
            <i data-lucide="save"></i> Save Assessment to Record
        </button>`;
    }

    html += `
        <div class="medical-disclaimer mt-4">
            <i data-lucide="alert-triangle"></i>
            <span>AI-generated risk assessment. Always verify with clinical judgment and refer high-risk cases immediately.</span>
        </div>
    `;

    container.innerHTML = html;
    if (window.lucide) lucide.createIcons();
}

async function saveMaternalToRecord() {
    const patient = getSelectedPatient('maternalPatientSelect');
    if (!patient) {
        showToast('Select a patient first', 'warning');
        return;
    }

    const symptoms = document.getElementById('maternalSymptoms').value.trim();
    const weeks = document.getElementById('maternalWeeks').value;
    const resultText = document.getElementById('maternalResult').innerText;

    try {
        const res = await fetch('/api/visits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_id: patient.patient_id,
                chief_complaint: `Maternal assessment - ${weeks} weeks gestation`,
                symptoms,
                diagnosis: 'Maternal health assessment (AI-assisted)',
                ai_assessment: { source: 'maternal_health', weeks: parseInt(weeks), result: resultText },
                attending_worker: APP.settings.workerName || 'Health Worker',
            }),
        });

        if (!res.ok) throw new Error('Failed to save');
        showToast('Maternal assessment saved to patient record', 'success');
    } catch (e) {
        showToast('Error: ' + e.message, 'error');
    }
}

function clearMaternal() {
    document.getElementById('maternalWeeks').value = '';
    document.getElementById('maternalSymptoms').value = '';
    document.getElementById('maternalVitals').value = '';
    document.getElementById('maternalHistory').value = '';
    document.getElementById('maternalPatientSelect').value = '';
    document.getElementById('maternalResult').innerHTML = `
        <div class="result-empty">
            <i data-lucide="heart-pulse"></i>
            <h3>Risk Assessment</h3>
            <p>Enter pregnancy details and click "Assess with Gemma 4" to evaluate risk level.</p>
        </div>`;
    if (window.lucide) lucide.createIcons();
}

// ============================================
// MEDICAL TRANSLATOR
// ============================================
async function runMedTranslate() {
    const input = document.getElementById('translatorInput').value.trim();
    const language = document.getElementById('translatorLanguage').value;

    if (!input) {
        showToast('Enter a patient description to translate', 'warning');
        return;
    }

    const btn = document.getElementById('translatorBtn');
    const resultPanel = document.getElementById('translatorResult');

    setBtnLoading(btn, true, 'Translating...');
    resultPanel.innerHTML = `<div class="ai-loading-container"><div class="ai-progress-bar"><div class="ai-progress-bar-fill"></div></div><div class="ai-loading-title">Translating with Gemma 4...</div><div class="ai-loading-subtitle">Converting to clinical terminology locally on your device.</div></div>`;

    try {
        const res = await fetch('/api/medtranslate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_description: input,
                source_language: language,
                target_language: 'en',
                language: APP.settings.language,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Translation failed');
        }

        const data = await res.json();
        APP.aiConsultationCount++;
        renderTranslatorResult(resultPanel, data);

    } catch (e) {
        resultPanel.innerHTML = `<div class="result-empty"><h3 class="text-danger">Error</h3><p>${escapeHtml(e.message)}</p></div>`;
    } finally {
        setBtnLoading(btn, false, '<i data-lucide="languages"></i> Translate with Gemma 4');
    }
}

function renderTranslatorResult(container, data) {
    let html = `
        <div class="result-header">
            <h3>Clinical Translation</h3>
            <span class="ai-inline-badge">Powered by Gemma 4</span>
        </div>
    `;

    if (data.clinical_translation) {
        html += `<div class="result-section"><div class="result-section-title">Clinical Translation</div>
            <div class="clinical-card" style="padding:16px;font-size:1rem;border-left:4px solid var(--brand-primary);">${escapeHtml(data.clinical_translation)}</div>
        </div>`;

        if (data.medical_terms && data.medical_terms.length > 0) {
            html += `<div class="result-section"><div class="result-section-title">Medical Term Mapping</div>
                <table class="data-table" style="width:100%;"><thead><tr><th>Patient Said</th><th>Clinical Term</th><th>Explanation</th></tr></thead><tbody>`;
            data.medical_terms.forEach(t => {
                html += `<tr><td>${escapeHtml(t.patient_said || '')}</td><td><strong>${escapeHtml(t.clinical_term || '')}</strong></td><td>${escapeHtml(t.explanation || '')}</td></tr>`;
            });
            html += `</tbody></table></div>`;
        }

        if (data.suggested_questions && data.suggested_questions.length > 0) {
            html += `<div class="result-section"><div class="result-section-title">Follow-up Questions to Ask</div>`;
            data.suggested_questions.forEach((q, i) => {
                html += `<div style="padding:6px 12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;margin-bottom:4px;font-size:0.9rem;">${i + 1}. ${escapeHtml(q)}</div>`;
            });
            html += `</div>`;
        }

        if (data.possible_conditions_mentioned && data.possible_conditions_mentioned.length > 0) {
            html += `<div class="result-section"><div class="result-section-title">Conditions Mentioned</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">`;
            data.possible_conditions_mentioned.forEach(c => {
                html += `<span style="padding:4px 10px;background:var(--brand-primary);color:white;border-radius:12px;font-size:0.8rem;">${escapeHtml(c)}</span>`;
            });
            html += `</div></div>`;
        }

        if (data.notes) {
            html += `<div class="result-section"><div class="clinical-card" style="padding:12px 16px;font-size:0.9rem;">${escapeHtml(data.notes)}</div></div>`;
        }
    } else {
        const txt = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        html += `<div class="result-section"><div class="result-text">${formatAiText(txt)}</div></div>`;
    }

    html += `
        <div class="medical-disclaimer mt-4">
            <i data-lucide="alert-triangle"></i>
            <span>AI-generated translation. Always verify medical terms with a qualified interpreter or clinician.</span>
        </div>
    `;

    container.innerHTML = html;
    if (window.lucide) lucide.createIcons();
}

function clearTranslator() {
    document.getElementById('translatorInput').value = '';
    document.getElementById('translatorLanguage').value = 'auto';
    document.getElementById('translatorResult').innerHTML = `
        <div class="result-empty">
            <i data-lucide="languages"></i>
            <h3>Translation Results</h3>
            <p>Enter a description and click "Translate" to get standardized clinical terminology.</p>
        </div>`;
    if (window.lucide) lucide.createIcons();
}

// Debounced real-time translation
function initTranslatorDebounce() {
    const input = document.getElementById('translatorInput');
    if (!input) return;

    input.addEventListener('input', () => {
        const indicator = document.getElementById('translatorTypingIndicator');
        clearTimeout(APP.debounceTimers.translator);

        if (input.value.trim().length > 10) {
            if (indicator) indicator.style.display = 'flex';
            APP.debounceTimers.translator = setTimeout(async () => {
                // Only auto-translate if text is substantial
                if (input.value.trim().length > 20) {
                    await runMedTranslate();
                }
                if (indicator) indicator.style.display = 'none';
            }, 1500);
        } else {
            if (indicator) indicator.style.display = 'none';
        }
    });
}

// ============================================
// FLOATING AI ASSISTANT
// ============================================
function toggleAssistant() {
    const el = document.getElementById('aiAssistant');
    if (!el) return;

    const isCollapsed = el.classList.contains('collapsed');
    if (isCollapsed) {
        el.classList.remove('collapsed');
        el.classList.add('expanded');
        if (window.lucide) lucide.createIcons();
        const input = document.getElementById('aiInput');
        if (input) setTimeout(() => input.focus(), 150);
    } else {
        el.classList.remove('expanded');
        el.classList.add('collapsed');
        if (window.lucide) lucide.createIcons();
    }
}

async function sendAiMessage() {
    const input = document.getElementById('aiInput');
    const messagesEl = document.getElementById('aiMessages');
    const sendBtn = document.querySelector('.ai-panel-send');
    if (!input || !messagesEl) return;

    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    input.style.height = 'auto';

    // User bubble
    appendAiMsg(text, 'ai-msg-user');
    APP.aiConversationHistory.push({ role: 'user', content: text });

    // Loading
    const loadingEl = appendAiMsg('Thinking...', 'ai-msg-bot ai-msg-loading');
    if (sendBtn) sendBtn.disabled = true;

    try {
        const res = await fetch('/api/assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                history: APP.aiConversationHistory.slice(0, -1),
                language: APP.settings.language,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error (${res.status})`);
        }

        const data = await res.json();
        const reply = data.response || 'Unable to generate a response.';
        loadingEl.textContent = reply;
        loadingEl.classList.remove('ai-msg-loading');
        APP.aiConversationHistory.push({ role: 'assistant', content: reply });
        APP.aiConsultationCount++;

    } catch (e) {
        loadingEl.textContent = 'Could not reach Gemma 4. Ensure Ollama is running.';
        loadingEl.classList.remove('ai-msg-loading');
    } finally {
        if (sendBtn) sendBtn.disabled = false;
        input.focus();
    }
}

function appendAiMsg(text, className) {
    const messagesEl = document.getElementById('aiMessages');
    if (!messagesEl) return document.createElement('div');

    const bubble = document.createElement('div');
    bubble.className = 'ai-msg ' + className;
    bubble.textContent = text;
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return bubble;
}

function initAiInputHandlers() {
    // Enter to send (Shift+Enter for newline)
    document.addEventListener('keydown', (e) => {
        if (e.target && e.target.id === 'aiInput') {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendAiMessage();
            }
        }
    });

    // Auto-resize AI textarea
    document.addEventListener('input', (e) => {
        if (e.target && e.target.id === 'aiInput') {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
        }
    });

    // Initialize translator debounce
    initTranslatorDebounce();
}

// ============================================
// SETTINGS
// ============================================
function loadSettings() {
    try {
        const saved = localStorage.getItem('gemma-settings');
        if (saved) {
            Object.assign(APP.settings, JSON.parse(saved));
        }
    } catch (e) { /* silent */ }

    // Apply to form
    const clinicName = document.getElementById('settingsClinicName');
    const workerName = document.getElementById('settingsWorkerName');
    const model = document.getElementById('settingsModel');
    const language = document.getElementById('settingsLanguage');

    if (clinicName) clinicName.value = APP.settings.clinicName || '';
    if (workerName) workerName.value = APP.settings.workerName || '';
    if (model) model.value = APP.settings.model || 'gemma3:12b-it-qat';
    if (language) language.value = APP.settings.language || 'en';

    // Sync topbar language
    const topbar = document.getElementById('languageSelector');
    if (topbar) topbar.value = APP.settings.language || 'en';
}

function saveSettings() {
    APP.settings.clinicName = (document.getElementById('settingsClinicName') || {}).value || '';
    APP.settings.workerName = (document.getElementById('settingsWorkerName') || {}).value || '';
    APP.settings.model = (document.getElementById('settingsModel') || {}).value || 'gemma3:12b-it-qat';
    APP.settings.language = (document.getElementById('settingsLanguage') || {}).value || 'en';

    localStorage.setItem('gemma-settings', JSON.stringify(APP.settings));
    showToast('Settings saved', 'success');
}

async function exportAllData() {
    try {
        const [patientsRes, visitsRes, medsRes] = await Promise.allSettled([
            fetch('/api/patients').then(r => r.json()),
            fetch('/api/visits').then(r => r.json()),
            fetch('/api/medications').then(r => r.json()),
        ]);

        const exportData = {
            exported_at: new Date().toISOString(),
            clinic_name: APP.settings.clinicName,
            patients: patientsRes.status === 'fulfilled' ? patientsRes.value : [],
            visits: visitsRes.status === 'fulfilled' ? visitsRes.value : [],
            medications: medsRes.status === 'fulfilled' ? medsRes.value : [],
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gemma-medical-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('Data exported successfully', 'success');
    } catch (e) {
        showToast('Export failed: ' + e.message, 'error');
    }
}

// ============================================
// GLOBAL SEARCH
// ============================================
function handleGlobalSearch(event) {
    if (event.key === 'Enter') {
        const query = event.target.value.trim();
        if (query) {
            switchPage('patients');
            const searchField = document.getElementById('patientSearch');
            if (searchField) searchField.value = query;
            searchPatients(query);
        }
    }
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Don't intercept when typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
            return;
        }

        if (e.altKey) {
            switch (e.key) {
                case '1': e.preventDefault(); switchPage('dashboard'); break;
                case '2': e.preventDefault(); switchPage('patients'); break;
                case '3': e.preventDefault(); switchPage('clinic'); break;
                case '4': e.preventDefault(); switchPage('drugs'); break;
                case '5': e.preventDefault(); switchPage('maternal'); break;
                case '6': e.preventDefault(); switchPage('translator'); break;
                case '7': e.preventDefault(); switchPage('settings'); break;
            }
        }

        // Ctrl+K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const search = document.getElementById('globalSearch');
            if (search) search.focus();
        }
    });
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info',
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i data-lucide="${icons[type] || 'info'}"></i><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    if (window.lucide) lucide.createIcons();

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function calcAge(dob) {
    if (!dob) return '--';
    const birth = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
    return age >= 0 ? age : '--';
}

function dobToAgeGroup(dob) {
    if (!dob) return '';
    const age = calcAge(dob);
    if (age === '--') return '';
    if (age < 1) return 'infant_0_1';
    if (age < 5) return 'child_1_5';
    if (age < 12) return 'child_5_12';
    if (age < 18) return 'teen_13_17';
    if (age < 40) return 'adult_18_40';
    if (age < 60) return 'adult_40_60';
    return 'elderly_60';
}

function setBtnLoading(btn, loading, html) {
    if (!btn) return;
    btn.disabled = loading;
    if (loading) {
        btn.dataset.originalHtml = btn.innerHTML;
        btn.innerHTML = `<span class="spinner"></span> ${html || 'Loading...'}`;
    } else {
        btn.innerHTML = html || btn.dataset.originalHtml || 'Submit';
        if (window.lucide) lucide.createIcons();
    }
}

function formatAiText(text) {
    if (!text) return '';
    // Escape HTML first
    let safe = escapeHtml(text);
    // Bold: **text**
    safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Headers: lines starting with ##
    safe = safe.replace(/^##\s+(.+)$/gm, '<strong style="font-size:1.05em;display:block;margin-top:0.75em;">$1</strong>');
    safe = safe.replace(/^#\s+(.+)$/gm, '<strong style="font-size:1.1em;display:block;margin-top:1em;">$1</strong>');
    // Bullet points
    safe = safe.replace(/^[-*]\s+(.+)$/gm, '<span style="display:flex;gap:0.5em;margin-left:0.5em;"><span style="color:var(--primary);">&#8226;</span><span>$1</span></span>');
    // Numbered lists
    safe = safe.replace(/^(\d+)\.\s+(.+)$/gm, '<span style="display:flex;gap:0.5em;margin-left:0.5em;"><span style="color:var(--primary);font-weight:600;">$1.</span><span>$2</span></span>');
    return safe;
}

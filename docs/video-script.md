# Gemma Medical -- Demo Video Script

**Format:** Voiceover over screen recording (no talking head)
**Length:** 3 minutes
**Tone:** Clear, confident, human. Not salesy. Let the product speak.

---

## Scene 1: The Problem (0:00 - 0:25)

**Screen:** Dark background. Stats fade in one at a time, large white text.

**Voiceover:**

> Two billion people lack access to essential health services.

> In Sub-Saharan Africa, one doctor serves sixteen thousand patients. Brain drain pulls trained physicians away. Junior nurses hold the line alone.

> In a village with no Wi-Fi, a cloud AI is a brick. These communities need intelligence that runs where they are -- on their device, on their terms.

**Screen:** Final stat fades. Transition to Gemma Medical dashboard.

---

## Scene 2: The Dashboard (0:25 - 0:50)

**Screen:** Gemma Medical HMS dashboard loads. Show patient count, recent visits, top diagnoses chart, quick action buttons.

**Voiceover:**

> This is Gemma Medical. Not a chatbot. A complete hospital management system -- built from the ground up for clinics with no internet.

> Dashboard shows real-time clinic analytics. Patient counts. Visit history. Common diagnoses. Everything a clinic administrator needs at a glance.

> Under the hood: Gemma 4 running locally via Ollama. Every module -- records, visits, prescriptions, diagnosis -- has AI built in. Not bolted on. Built in.

**Screen:** Hover over the module navigation: Patients, Visits, Medications, CDSS tools.

---

## Scene 3: Register a Patient (0:50 - 1:15)

**Screen:** Navigate to Patient Registry. Click "New Patient."

**Voiceover:**

> A community health officer in rural Kenya sees a new patient. They open the registry and enter their details -- name, date of birth, village, allergies, chronic conditions.

**Screen:** Fill in patient form: "Amina Ochieng," village "Kisumu West," allergy "penicillin." Click save.

**Voiceover:**

> One registration. The record persists locally across every future visit. No cloud database. No server. A JSON file on this device.

**Screen:** Show the patient appearing in the registry list. Click into their profile.

---

## Scene 4: Log a Visit and Get a Diagnosis (1:15 - 1:50)

**Screen:** From the patient profile, click "New Visit." Enter vitals and symptoms.

**Voiceover:**

> Amina presents with a fever, headache, and a rash on her forearms. The health officer logs her vitals -- blood pressure, temperature, pulse, respiratory rate.

**Screen:** Enter vitals: BP 110/70, temp 38.8C, pulse 92. Chief complaint: "Fever for 3 days, headache, red raised rash on forearms."

**Voiceover:**

> They describe the symptoms and Gemma 4 auto-suggests a differential diagnosis. Fever plus rash in East Africa -- malaria, dengue, typhoid. Each ranked by likelihood with treatment guidance.

**Screen:** Show AI assessment populating with structured differential diagnosis. Highlight the ranked conditions and treatment recommendations.

**Voiceover:**

> This is the second opinion that would normally require a hospital hours away. It took two seconds. No internet.

---

## Scene 5: Drug Interaction Check (1:50 - 2:10)

**Screen:** Navigate to the patient's medication tab. Show existing medications. Add a new prescription.

**Voiceover:**

> Amina is already taking metformin and lisinopril. The officer prescribes ibuprofen for the fever.

**Screen:** Type "ibuprofen" into the new medication form. Submit. The drug checker fires automatically.

**Voiceover:**

> The system catches it immediately. Lisinopril and ibuprofen together -- increased risk of kidney damage and reduced blood pressure control. A dangerous interaction flagged before the medication is dispensed.

**Screen:** Show the interaction warning with severity level highlighted in red.

---

## Scene 6: Maternal Risk Assessment (2:10 - 2:30)

**Screen:** Navigate to Maternal Health Monitor.

**Voiceover:**

> A midwife at a rural birth center. A woman at 32 weeks with severe headaches and swollen ankles.

**Screen:** Enter gestational age: 32 weeks. Symptoms: "severe headache, swollen ankles, blurred vision, elevated blood pressure."

**Voiceover:**

> Preeclampsia risk. Flagged urgent. Specific danger signs identified with escalation protocol. This knowledge saves two lives -- and it's running on a phone with no signal.

**Screen:** Show the risk assessment. Highlight "URGENT" classification and the danger sign breakdown.

---

## Scene 7: Translator Demo (2:30 - 2:40)

**Screen:** Navigate to Medical Translator.

**Voiceover:**

> A patient describes symptoms in Swahili. The translator produces precise clinical English -- not word-for-word, but proper medical terminology.

**Screen:** Type a Swahili symptom description. Submit. Show the clinical English translation with medical terms highlighted.

---

## Scene 8: Airplane Mode (2:40 - 2:50)

**Screen:** Pull down the notification shade. Toggle airplane mode ON. Show the airplane icon.

**Voiceover:**

> Airplane mode. No Wi-Fi. No cellular. No connection of any kind.

**Screen:** Navigate back to the dashboard. Open Clinic Copilot. Submit a query. Show it responding normally.

**Voiceover:**

> Full functionality. Every module. Every AI feature. Patient data never leaves this device.

---

## Scene 9: Close (2:50 - 3:00)

**Screen:** Return to the HMS dashboard. Text fades in over the interface.

**Voiceover:**

> A complete hospital in your hands. Records. Visits. Prescriptions. Diagnosis. All powered by Gemma 4. All running locally.

> Healthcare for every community. No internet required.

**Screen:** "Gemma Medical" title. "Powered by Gemma 4 via Ollama." GitHub link. Fade to black.

---

## Production Notes

- Screen recording at 1920x1080, 60fps
- Use actual Gemma 4 responses from the live application (not staged or mocked)
- Pre-populate the patient registry with 8-10 demo patients so the dashboard has real analytics
- Background music: subtle ambient, not distracting (consider royalty-free from incompetech.com)
- Voiceover pacing: steady and measured, not rushed -- let each feature breathe
- Airplane mode toggle should be clearly visible to the viewer
- Total runtime target: 2:55 - 3:00
- Export at 1080p and 4K for Kaggle submission and social media respectively

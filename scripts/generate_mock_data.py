"""Generate realistic mock data for Gemma Medical demo.

Creates a rich dataset that makes the system look like it's been running
in a busy rural clinic in Sub-Saharan Africa for 6 months.

Generates:
- 500 patients (realistic African/South Asian names, villages, conditions)
- 3000+ visit records with vitals, diagnoses, treatments
- 1500+ medication records
- 15 patients in the queue right now
- 20 referral letters
- Realistic data distributions (seasonal malaria, maternal cases, etc.)

Usage:
    python scripts/generate_mock_data.py
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)

# ---- Name pools (East African, West African, South Asian) ----

FIRST_NAMES_MALE = [
    "Kwame", "Kofi", "Yaw", "Kwesi", "Kojo", "Ebo", "Fiifi",
    "Abdi", "Hassan", "Omar", "Mohamed", "Ibrahim", "Ali", "Yusuf",
    "Chidi", "Emeka", "Obinna", "Nnamdi", "Ikenna", "Ugochukwu",
    "Baraka", "Juma", "Hamisi", "Rashid", "Salim", "Mwangi", "Kimani",
    "Raj", "Amit", "Suresh", "Vikram", "Arjun", "Deepak", "Ramesh",
    "David", "Joseph", "Peter", "John", "Samuel", "Daniel", "James",
    "Emmanuel", "Patrick", "Francis", "George", "Michael", "Thomas",
    "Ousmane", "Mamadou", "Boubacar", "Amadou", "Moussa", "Seydou",
    "Tendai", "Tatenda", "Farai", "Tapiwa", "Kudakwashe",
]

FIRST_NAMES_FEMALE = [
    "Ama", "Akua", "Yaa", "Afia", "Adjoa", "Efua", "Abena",
    "Amina", "Fatima", "Zainab", "Halima", "Mariam", "Aisha", "Hadija",
    "Chioma", "Ngozi", "Adaeze", "Nneka", "Ifunanya", "Obiageli",
    "Rehema", "Zawadi", "Neema", "Bahati", "Furaha", "Wanjiku", "Njeri",
    "Priya", "Lakshmi", "Sunita", "Anita", "Meena", "Radha", "Kavitha",
    "Grace", "Mary", "Sarah", "Ruth", "Esther", "Elizabeth", "Hannah",
    "Comfort", "Patience", "Mercy", "Joy", "Faith", "Hope", "Peace",
    "Aminata", "Mariama", "Fatoumata", "Kadiatou", "Oumou",
    "Tendai", "Rudo", "Tsitsi", "Nyasha", "Tariro",
]

LAST_NAMES = [
    "Mensah", "Asante", "Boateng", "Owusu", "Osei", "Adu", "Yeboah",
    "Hassan", "Ali", "Mohamed", "Ibrahim", "Omar", "Ahmed", "Osman",
    "Okonkwo", "Nwosu", "Eze", "Okoro", "Igwe", "Nwachukwu",
    "Mwangi", "Kamau", "Njoroge", "Kipchoge", "Wafula", "Odhiambo",
    "Sharma", "Patel", "Singh", "Kumar", "Das", "Gupta", "Nair",
    "Banda", "Phiri", "Mulenga", "Tembo", "Lungu", "Zulu",
    "Diallo", "Traore", "Keita", "Coulibaly", "Sangare", "Toure",
    "Moyo", "Ndlovu", "Nkomo", "Sibanda", "Dube", "Ncube",
    "Kimani", "Mutua", "Kariuki", "Gatheru", "Ndungu",
]

VILLAGES = [
    "Kibera Village", "Mathare", "Kangemi", "Kawangware", "Dandora",
    "Mukuru kwa Njenga", "Korogocho", "Huruma", "Githurai", "Ruiru",
    "Kiambu Town", "Thika", "Limuru", "Gatundu", "Nyeri",
    "Mombasa Old Town", "Malindi", "Kilifi", "Kwale", "Lamu",
    "Kisumu Central", "Siaya", "Bondo", "Migori", "Homa Bay",
    "Nakuru Town", "Naivasha", "Gilgil", "Eldoret", "Kitale",
    "Machakos", "Makueni", "Kitui", "Embu", "Meru",
    "Garissa", "Wajir", "Mandera", "Isiolo", "Marsabit",
    "Kampala-Kawempe", "Jinja", "Mbale", "Gulu", "Lira",
    "Dar es Salaam-Kinondoni", "Mwanza", "Arusha", "Dodoma", "Mbeya",
]

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

COMMON_ALLERGIES = [
    [], [], [], [], [], [], [],  # Most people have none
    ["Penicillin"], ["Sulfonamides"], ["Aspirin"],
    ["Penicillin", "Sulfonamides"], ["Chloroquine"],
    ["NSAIDs"], ["Tetracycline"], ["Iodine"],
]

CHRONIC_CONDITIONS = [
    [], [], [], [], [],  # Many have none
    ["Hypertension"], ["Type 2 Diabetes"], ["HIV/AIDS"],
    ["Hypertension", "Type 2 Diabetes"], ["Asthma"],
    ["Sickle Cell Disease"], ["Tuberculosis"], ["Epilepsy"],
    ["HIV/AIDS", "Tuberculosis"], ["Chronic Kidney Disease"],
    ["Rheumatic Heart Disease"], ["Hepatitis B"],
]

# ---- Clinical data pools ----

CHIEF_COMPLAINTS = [
    "Fever for 3 days", "Fever and headache", "Fever and body aches",
    "Cough for 1 week", "Cough with blood", "Persistent cough",
    "Diarrhea and vomiting", "Bloody diarrhea", "Watery diarrhea for 2 days",
    "Abdominal pain", "Severe abdominal pain", "Epigastric pain",
    "Headache", "Severe headache with neck stiffness", "Headache and dizziness",
    "Difficulty breathing", "Wheezing", "Chest pain",
    "Skin rash", "Itchy skin rash for 5 days", "Wound not healing",
    "Joint pain", "Back pain", "Leg swelling",
    "Eye redness", "Eye pain and discharge", "Blurred vision",
    "Ear pain", "Sore throat", "Toothache",
    "Fatigue and weight loss", "Night sweats", "Loss of appetite",
    "Urinary burning", "Blood in urine", "Frequent urination",
    "Vaginal bleeding", "Missed period", "Pregnancy checkup",
    "Child not eating", "Child with convulsions", "Child not growing well",
    "Dog bite", "Snake bite", "Burn injury",
    "Road traffic injury", "Fall from height", "Assault injury",
    "Follow-up visit", "Medication refill", "Routine checkup",
]

DIAGNOSES = {
    "fever": ["Malaria (confirmed RDT+)", "Malaria (clinical)", "Dengue Fever",
              "Typhoid Fever", "Upper Respiratory Infection", "Pneumonia",
              "Urinary Tract Infection", "Viral Fever (non-specific)"],
    "cough": ["Pneumonia", "Tuberculosis", "Bronchitis", "Asthma Exacerbation",
              "Upper Respiratory Infection", "COVID-19 (suspected)"],
    "diarrhea": ["Acute Gastroenteritis", "Cholera (suspected)", "Dysentery",
                 "Food Poisoning", "Intestinal Parasites"],
    "abdominal": ["Peptic Ulcer Disease", "Appendicitis (suspected)", "Gastritis",
                  "Intestinal Obstruction", "Hepatitis"],
    "skin": ["Fungal Skin Infection", "Scabies", "Eczema", "Cellulitis",
             "Herpes Zoster", "Impetigo"],
    "respiratory": ["Asthma", "COPD Exacerbation", "Pneumonia", "Pleural Effusion"],
    "maternal": ["Normal Pregnancy", "Preeclampsia", "Gestational Diabetes",
                 "Anemia in Pregnancy", "Threatened Abortion", "Placenta Previa"],
    "injury": ["Laceration", "Fracture (suspected)", "Burn (2nd degree)",
               "Concussion", "Sprain", "Wound Infection"],
    "other": ["Hypertension (uncontrolled)", "Diabetes (uncontrolled)",
              "HIV Follow-up", "TB Follow-up", "Epilepsy Follow-up",
              "Anemia", "Malnutrition (moderate)", "Malnutrition (severe)"],
}

TREATMENTS = {
    "Malaria": "Artemether-Lumefantrine (AL) 20/120mg, 4 tablets BID x 3 days. Paracetamol 1g TID for fever.",
    "Pneumonia": "Amoxicillin 500mg TID x 7 days. Paracetamol for fever. Encourage fluids.",
    "Typhoid Fever": "Ciprofloxacin 500mg BID x 7 days. Paracetamol. IV fluids if dehydrated.",
    "Gastroenteritis": "ORS packets, Zinc 20mg daily x 10 days. Clear fluids. Monitor hydration.",
    "Dysentery": "Metronidazole 400mg TID x 5 days. ORS. Monitor for dehydration.",
    "UTI": "Nitrofurantoin 100mg BID x 5 days. Encourage water intake.",
    "Hypertension": "Amlodipine 5mg daily. Low salt diet. Follow-up in 2 weeks.",
    "Diabetes": "Metformin 500mg BID. Dietary counseling. Blood glucose monitoring.",
    "Asthma": "Salbutamol inhaler 2 puffs PRN. Prednisolone 40mg daily x 5 days if acute.",
    "Anemia": "Ferrous Sulfate 200mg TID + Folic Acid 5mg daily. Dietary counseling.",
    "TB": "RHZE (Rifampicin/Isoniazid/Pyrazinamide/Ethambutol) intensive phase. DOT supervision.",
    "HIV": "TLD (Tenofovir/Lamivudine/Dolutegravir) 1 tablet daily. Viral load monitoring.",
    "Wound": "Wound cleaning and debridement. Tetanus toxoid if indicated. Amoxicillin if infected.",
    "Default": "Symptomatic treatment. Paracetamol for pain/fever. Follow-up if symptoms persist.",
}

MEDICATIONS = [
    ("Artemether-Lumefantrine", "20/120mg", "2 tablets BID"),
    ("Amoxicillin", "500mg", "TID"),
    ("Amoxicillin", "250mg", "TID"),
    ("Metronidazole", "400mg", "TID"),
    ("Paracetamol", "1g", "TID PRN"),
    ("Ibuprofen", "400mg", "TID"),
    ("Ciprofloxacin", "500mg", "BID"),
    ("Doxycycline", "100mg", "BID"),
    ("Cotrimoxazole", "960mg", "BID"),
    ("ORS", "1 packet", "After each stool"),
    ("Zinc", "20mg", "Daily"),
    ("Ferrous Sulfate", "200mg", "TID"),
    ("Folic Acid", "5mg", "Daily"),
    ("Amlodipine", "5mg", "Daily"),
    ("Metformin", "500mg", "BID"),
    ("Salbutamol Inhaler", "100mcg", "2 puffs PRN"),
    ("Prednisolone", "5mg", "As directed"),
    ("Omeprazole", "20mg", "Daily"),
    ("Misoprostol", "200mcg", "As directed"),
    ("Oxytocin", "10 IU", "IM"),
    ("Magnesium Sulfate", "4g", "IV loading dose"),
    ("Diazepam", "5mg", "PRN"),
    ("Phenobarbital", "60mg", "Daily"),
    ("Insulin (Soluble)", "As per sliding scale", "SC"),
    ("Hydrocortisone", "100mg", "IV"),
    ("Epinephrine", "0.5mg", "IM"),
]

WORKERS = [
    "Nurse Amina Hassan", "Nurse Grace Mwangi", "CHO Ibrahim Osman",
    "Dr. Kwame Mensah", "Nurse Fatima Ali", "CHW Baraka Juma",
    "Nurse Priya Sharma", "Dr. Joseph Kamau", "Nurse Patience Okonkwo",
    "CHO Halima Diallo", "Midwife Rehema Salim", "Nurse David Banda",
]


def generate_dob(age_min, age_max):
    """Generate a date of birth for a given age range."""
    age = random.randint(age_min, age_max)
    base = datetime(2026, 4, 1)
    dob = base - timedelta(days=age * 365 + random.randint(0, 364))
    return dob.strftime("%Y-%m-%d")


def generate_vitals(age_category="adult", condition=None):
    """Generate realistic vital signs."""
    if age_category == "child":
        bp_sys = random.randint(85, 110) if random.random() > 0.1 else random.randint(70, 130)
        bp_dia = random.randint(50, 70) if random.random() > 0.1 else random.randint(40, 85)
        pulse = random.randint(80, 120) if random.random() > 0.1 else random.randint(60, 160)
        temp = round(random.uniform(36.2, 37.2) if random.random() > 0.3 else random.uniform(37.5, 40.2), 1)
        rr = random.randint(18, 30) if random.random() > 0.1 else random.randint(12, 45)
        weight = round(random.uniform(8, 35), 1)
        height = round(random.uniform(70, 140), 1)
    elif age_category == "infant":
        bp_sys = None
        bp_dia = None
        pulse = random.randint(100, 160)
        temp = round(random.uniform(36.5, 37.5) if random.random() > 0.25 else random.uniform(37.8, 40.5), 1)
        rr = random.randint(25, 50)
        weight = round(random.uniform(2.5, 12), 1)
        height = round(random.uniform(45, 80), 1)
    else:  # adult
        bp_sys = random.randint(110, 135) if random.random() > 0.2 else random.randint(90, 185)
        bp_dia = random.randint(65, 85) if random.random() > 0.2 else random.randint(55, 110)
        pulse = random.randint(60, 90) if random.random() > 0.15 else random.randint(45, 135)
        temp = round(random.uniform(36.2, 37.2) if random.random() > 0.25 else random.uniform(37.5, 40.0), 1)
        rr = random.randint(14, 20) if random.random() > 0.1 else random.randint(10, 32)
        weight = round(random.uniform(45, 90), 1)
        height = round(random.uniform(150, 185), 1)

    # Make some vitals None randomly (not always recorded)
    vitals = {
        "bp_systolic": bp_sys,
        "bp_diastolic": bp_dia,
        "temperature_c": temp if random.random() > 0.1 else None,
        "pulse_rate": pulse if random.random() > 0.05 else None,
        "respiratory_rate": rr if random.random() > 0.3 else None,
        "weight_kg": weight if random.random() > 0.2 else None,
        "height_cm": height if random.random() > 0.5 else None,
    }
    return vitals


def get_diagnosis_for_complaint(complaint):
    """Pick a realistic diagnosis based on the chief complaint."""
    c = complaint.lower()
    if "fever" in c:
        return random.choice(DIAGNOSES["fever"])
    elif "cough" in c:
        return random.choice(DIAGNOSES["cough"])
    elif "diarrhea" in c or "vomiting" in c:
        return random.choice(DIAGNOSES["diarrhea"])
    elif "abdominal" in c or "epigastric" in c:
        return random.choice(DIAGNOSES["abdominal"])
    elif "skin" in c or "rash" in c or "wound" in c:
        return random.choice(DIAGNOSES["skin"])
    elif "breath" in c or "wheez" in c or "chest" in c:
        return random.choice(DIAGNOSES["respiratory"])
    elif "pregnan" in c or "vaginal" in c or "missed period" in c:
        return random.choice(DIAGNOSES["maternal"])
    elif "bite" in c or "burn" in c or "injur" in c or "fall" in c:
        return random.choice(DIAGNOSES["injury"])
    else:
        return random.choice(DIAGNOSES["other"])


def get_treatment(diagnosis):
    """Get treatment plan for a diagnosis."""
    for key, treatment in TREATMENTS.items():
        if key.lower() in diagnosis.lower():
            return treatment
    return TREATMENTS["Default"]


def generate_patients(n=500):
    """Generate n patient records."""
    patients = []
    for i in range(n):
        sex = random.choice(["male", "female"])
        if sex == "male":
            first = random.choice(FIRST_NAMES_MALE)
        else:
            first = random.choice(FIRST_NAMES_FEMALE)

        # Age distribution: more children and young adults
        age_weights = [(0, 1, 0.08), (1, 5, 0.12), (5, 17, 0.15),
                       (18, 40, 0.35), (40, 60, 0.20), (60, 85, 0.10)]
        r = random.random()
        cumulative = 0
        for age_min, age_max, weight in age_weights:
            cumulative += weight
            if r <= cumulative:
                dob = generate_dob(age_min, age_max)
                break

        registered = datetime(2025, 10, 1) + timedelta(days=random.randint(0, 180))

        patient = {
            "patient_id": str(uuid.uuid4()),
            "first_name": first,
            "last_name": random.choice(LAST_NAMES),
            "date_of_birth": dob,
            "sex": sex,
            "blood_type": random.choice(BLOOD_TYPES) if random.random() > 0.4 else "",
            "allergies": random.choice(COMMON_ALLERGIES),
            "chronic_conditions": random.choice(CHRONIC_CONDITIONS),
            "emergency_contact_name": random.choice(FIRST_NAMES_MALE if random.random() > 0.5 else FIRST_NAMES_FEMALE) + " " + random.choice(LAST_NAMES),
            "emergency_contact_phone": f"+254{random.randint(700000000, 799999999)}",
            "village_or_address": random.choice(VILLAGES),
            "registered_date": registered.isoformat(),
            "last_visit": "",
            "notes": "",
        }
        patients.append(patient)

    return patients


def generate_visits(patients, avg_visits_per_patient=6):
    """Generate visit records for all patients."""
    visits = []
    for patient in patients:
        age = 2026 - int(patient["date_of_birth"][:4])
        age_cat = "infant" if age < 2 else "child" if age < 13 else "adult"

        n_visits = max(1, int(random.gauss(avg_visits_per_patient, 3)))
        n_visits = min(n_visits, 20)

        reg_date = datetime.fromisoformat(patient["registered_date"])
        last_visit_date = None

        for v in range(n_visits):
            visit_date = reg_date + timedelta(days=random.randint(v * 7, v * 30 + 30))
            if visit_date > datetime(2026, 4, 7):
                break

            complaint = random.choice(CHIEF_COMPLAINTS)
            diagnosis = get_diagnosis_for_complaint(complaint)
            treatment = get_treatment(diagnosis)

            # Maternal visits for women of childbearing age
            if patient["sex"] == "female" and 15 <= age <= 45 and random.random() < 0.15:
                complaint = random.choice(["Pregnancy checkup", "Missed period", "Vaginal bleeding"])
                diagnosis = random.choice(DIAGNOSES["maternal"])
                treatment = "Antenatal care. Iron/folate supplementation. Next visit in 4 weeks."

            visit = {
                "visit_id": str(uuid.uuid4()),
                "patient_id": patient["patient_id"],
                "visit_date": visit_date.isoformat(),
                "chief_complaint": complaint,
                "symptoms": complaint + ". " + random.choice([
                    "Patient reports symptoms for " + str(random.randint(1, 14)) + " days.",
                    "Gradual onset. No improvement with home remedies.",
                    "Sudden onset. First episode.",
                    "Recurrent episode. Similar symptoms 2 months ago.",
                    "Associated with loss of appetite and fatigue.",
                    "No associated symptoms.",
                ]),
                "vitals": generate_vitals(age_cat),
                "diagnosis": diagnosis,
                "treatment_plan": treatment,
                "medications_prescribed": [],
                "follow_up_date": (visit_date + timedelta(days=random.choice([7, 14, 28, 0]))).strftime("%Y-%m-%d") if random.random() > 0.3 else "",
                "ai_assessment": {},
                "notes": random.choice([
                    "", "", "",
                    "Patient counseled on medication adherence.",
                    "Referred for further investigation.",
                    "Patient to return if symptoms worsen.",
                    "Malaria RDT performed.",
                    "Blood glucose checked.",
                    "Patient stable. Continue current management.",
                ]),
                "attending_worker": random.choice(WORKERS),
            }
            visits.append(visit)
            last_visit_date = visit_date

        if last_visit_date:
            patient["last_visit"] = last_visit_date.isoformat()

    return visits


def generate_medications(patients, visits):
    """Generate medication records from visits."""
    meds = []
    for visit in visits:
        if random.random() < 0.7:  # 70% of visits result in prescriptions
            n_meds = random.randint(1, 3)
            for _ in range(n_meds):
                med_name, dosage, freq = random.choice(MEDICATIONS)
                duration = random.choice([3, 5, 7, 10, 14, 28, 90])
                start = datetime.fromisoformat(visit["visit_date"])
                end = start + timedelta(days=duration)

                med = {
                    "med_id": str(uuid.uuid4()),
                    "patient_id": visit["patient_id"],
                    "medication_name": med_name,
                    "dosage": dosage,
                    "frequency": freq,
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d") if end < datetime(2026, 4, 7) else "",
                    "prescribed_by": visit["attending_worker"],
                    "notes": "",
                }
                meds.append(med)

                # Add to visit's prescribed meds
                visit["medications_prescribed"].append(f"{med_name} {dosage} {freq}")

    return meds


def generate_queue(patients):
    """Generate a current waiting room queue."""
    queue = []
    waiting_patients = random.sample([p for p in patients if p["last_visit"]], min(15, len(patients)))

    for i, patient in enumerate(waiting_patients):
        arrival = datetime(2026, 4, 8, 7, 30) + timedelta(minutes=random.randint(0, 180))
        priority = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 30, 35, 20])[0]

        complaints = {
            1: ["Severe difficulty breathing", "Unconscious patient", "Severe bleeding", "Seizures"],
            2: ["High fever with confusion", "Chest pain", "Severe abdominal pain", "Severe dehydration"],
            3: ["Fever for 3 days", "Persistent cough", "Infected wound", "Moderate pain"],
            4: ["Routine pregnancy checkup", "Medication refill", "Mild cough", "Skin rash"],
            5: ["Routine checkup", "Follow-up visit", "Health certificate", "Vaccination"],
        }

        status = "waiting" if i >= 2 else random.choice(["waiting", "in-progress"])

        queue.append({
            "queue_id": str(uuid.uuid4()),
            "patient_id": patient["patient_id"],
            "patient_name": f"{patient['first_name']} {patient['last_name']}",
            "priority": priority,
            "chief_complaint": random.choice(complaints[priority]),
            "arrival_time": arrival.isoformat(),
            "status": status,
        })

    queue.sort(key=lambda x: (x["priority"], x["arrival_time"]))
    return queue


def generate_referrals(patients, visits):
    """Generate some referral records."""
    referrals = []
    serious_visits = [v for v in visits if any(k in v["diagnosis"].lower()
                      for k in ["pneumonia", "tb", "appendicitis", "preeclampsia",
                                "fracture", "severe", "cholera", "meningitis"])]

    for visit in random.sample(serious_visits, min(20, len(serious_visits))):
        patient = next((p for p in patients if p["patient_id"] == visit["patient_id"]), None)
        if not patient:
            continue

        referrals.append({
            "referral_id": str(uuid.uuid4()),
            "patient_id": visit["patient_id"],
            "visit_id": visit["visit_id"],
            "referral_date": visit["visit_date"],
            "referring_facility": "Kibera Community Health Center",
            "receiving_facility": random.choice([
                "Kenyatta National Hospital", "Mbagathi District Hospital",
                "Mama Lucy Kibaki Hospital", "Pumwani Maternity Hospital",
                "Kiambu Level 5 Hospital", "Thika Level 5 Hospital",
            ]),
            "urgency": random.choice(["emergency", "urgent", "routine"]),
            "reason": f"Referral for further evaluation of {visit['diagnosis']}. "
                      f"Patient presenting with {visit['chief_complaint']}.",
            "letter": f"REFERRAL LETTER\n\nDate: {visit['visit_date'][:10]}\n"
                      f"From: Kibera Community Health Center\n"
                      f"Patient: {patient['first_name']} {patient['last_name']}\n"
                      f"DOB: {patient['date_of_birth']}\n"
                      f"Sex: {patient['sex'].upper()}\n\n"
                      f"PRESENTING COMPLAINT:\n{visit['chief_complaint']}\n\n"
                      f"EXAMINATION FINDINGS:\n{visit['symptoms']}\n\n"
                      f"VITALS:\nBP: {visit['vitals'].get('bp_systolic', '--')}/{visit['vitals'].get('bp_diastolic', '--')} mmHg\n"
                      f"Temp: {visit['vitals'].get('temperature_c', '--')} C\n"
                      f"Pulse: {visit['vitals'].get('pulse_rate', '--')} bpm\n\n"
                      f"WORKING DIAGNOSIS:\n{visit['diagnosis']}\n\n"
                      f"TREATMENT GIVEN:\n{visit['treatment_plan']}\n\n"
                      f"REASON FOR REFERRAL:\nPatient requires further evaluation and management "
                      f"beyond the capacity of this facility.\n\n"
                      f"Attending: {visit['attending_worker']}",
            "status": random.choice(["sent", "accepted", "completed"]),
        })

    return referrals


def main():
    print("=" * 55)
    print("  Generating Gemma Medical Demo Data")
    print("  Simulating 6 months of a busy rural clinic")
    print("=" * 55)
    print()

    print("[1/5] Generating 500 patients...")
    patients = generate_patients(500)
    print(f"       {len(patients)} patients created")
    print(f"       Villages: {len(set(p['village_or_address'] for p in patients))}")

    print("[2/5] Generating visit records...")
    visits = generate_visits(patients)
    print(f"       {len(visits)} visits created")
    print(f"       Diagnoses: {len(set(v['diagnosis'] for v in visits))} unique")

    print("[3/5] Generating medication records...")
    meds = generate_medications(patients, visits)
    print(f"       {len(meds)} prescriptions created")

    print("[4/5] Generating patient queue...")
    queue = generate_queue(patients)
    print(f"       {len(queue)} patients in queue")

    print("[5/5] Generating referral letters...")
    referrals = generate_referrals(patients, visits)
    print(f"       {len(referrals)} referrals created")

    # Write all files
    print()
    print("Writing data files...")

    for name, data in [
        ("patients.json", patients),
        ("visits.json", visits),
        ("medications.json", meds),
        ("queue.json", queue),
        ("referrals.json", referrals),
    ]:
        path = DATA_DIR / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        size_mb = path.stat().st_size / 1e6
        print(f"  {name}: {len(data)} records ({size_mb:.1f} MB)")

    total_size = sum((DATA_DIR / f).stat().st_size for f in
                     ["patients.json", "visits.json", "medications.json", "queue.json", "referrals.json"])

    print()
    print(f"Total data: {total_size / 1e6:.1f} MB")
    print(f"Total records: {len(patients) + len(visits) + len(meds) + len(queue) + len(referrals)}")
    print()
    print("Demo data ready. Start the app and see a fully populated clinic.")


if __name__ == "__main__":
    main()

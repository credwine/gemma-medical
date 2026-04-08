# Gemma Medical

**AI-Powered Hospital Management System for Underserved Communities**

A complete offline-first Hospital Management System with embedded Clinical Decision Support (CDSS), Electronic Medical Records (EMR), and Electronic Health Records (EHR). Powered by [Gemma 4](https://ai.google.dev/gemma) running locally via [Ollama](https://ollama.com). No cloud. No internet required. All patient data stays on-device.

Built for the [Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon) on Kaggle.

---

## The Problem

Over **2 billion people** lack access to essential health services. Sub-Saharan Africa carries 24% of the global disease burden with only 3% of the global health workforce. Brain drain pulls trained doctors to wealthier countries, leaving junior nurses and community health officers (CHOs) as the only medical professionals for entire regions.

In a village with no Wi-Fi, a cloud AI is a brick. Existing telemedicine tools require reliable internet and send patient data to remote servers. In the communities that need help most, neither connectivity nor digital trust exists.

## The Solution

Gemma Medical is a full hospital management platform built for community clinics and health workers in developing countries. Gemma 4 is not a sidebar feature -- it is the intelligence layer embedded in every workflow, from patient registration to diagnosis to medication safety.

### Platform Modules

| Module | What It Does |
|--------|-------------|
| **HMS Dashboard** | Analytics overview: patient counts, visit statistics, common diagnoses, recent activity, quick actions |
| **EMR -- Patient Registry** | Full CRUD patient management with search, village/address tracking, allergies, chronic conditions |
| **EHR -- Visit Records** | Clinical visit logging with vitals (BP, temperature, pulse, respiratory rate, weight, height), diagnosis, treatment plan |
| **Medication Tracker** | Active medication log, prescription history, auto drug interaction checking per patient |

### CDSS Tools (Gemma 4-Powered)

| Tool | What It Does |
|------|-------------|
| **Clinic Copilot** | Photo + symptoms to differential diagnosis. Covers tropical diseases, WHO IMNCI protocols |
| **Drug Interaction Checker** | Flag dangerous medication combinations against WHO Essential Medicines List |
| **Maternal Health Monitor** | Pregnancy risk assessment: preeclampsia, hemorrhage, sepsis detection |
| **Medical Translator** | Local language (Swahili, Hindi, Hausa, Yoruba, Amharic, Bengali, Tagalog) to clinical English |
| **Gemma AI Assistant** | General-purpose medical chat embedded across every workflow |

---

## Key Features

| Feature | Details |
|---------|---------|
| 100% Offline | Works with zero internet after initial model download. Data never leaves the device |
| Multimodal Vision | Analyze photos of skin conditions, medication labels, wound presentations |
| 10+ Languages | English, Swahili, Hindi, Hausa, Yoruba, Amharic, Bengali, Tagalog, Spanish, French, Arabic, and more |
| PWA Installable | Install on any device as a progressive web app |
| Local JSON Storage | All patient/visit/medication data stored in local JSON files -- no database server needed |
| Structured Output | JSON-formatted responses via Gemma 4 function calling |
| Dark Mode | Reduce eye strain during night shifts and low-light fieldwork |
| Sub-2s Inference | Local Gemma 4 responds faster than a satellite ping |

---

## Privacy by Architecture

- All AI inference runs locally via Ollama. No API calls leave the device.
- All patient records stored in local JSON files. No external database.
- Zero patient data is transmitted, stored remotely, or logged externally.
- No telemetry. No analytics beacons. No tracking.
- No HIPAA compliance hurdles -- data never leaves the machine.
- The model weights and all data live on your device. You own the entire stack.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/coreyredwine/gemma-medical.git
cd gemma-medical

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (if you haven't already)
# https://ollama.com/download

# Pull the Gemma 4 model (~9.6 GB one-time download)
ollama pull gemma4:e4b

# Start the server
python run.py
```

Open **http://localhost:8000** in your browser.

### Docker Alternative

```bash
docker compose up
```

Starts both Gemma Medical (port 8000) and Ollama (port 11434) with GPU passthrough.

---

## Architecture

```
+-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |
|  Browser (PWA)    | <---> |  FastAPI Backend   | <---> |  Ollama (Gemma 4) |
|                   |       |                   |       |                   |
|  HMS Dashboard    |       |  22 API Endpoints  |       |  Local LLM        |
|  Patient Registry |       |  Prompt Engine     |       |  Multimodal       |
|  Visit Records    |       |  Vision Pipeline   |       |  Function Calling  |
|  Medication Log   |       |  JSON File Storage |       |  Offline           |
|  CDSS Tools (5)   |       |  Analytics Engine  |       |                   |
|  AI Assistant     |       |                   |       |                   |
|                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+
     Port 8000                   Python 3.10+              Port 11434
```

All three layers run on the same device. Nothing leaves the machine.

### API Routes (22 endpoints)

| Group | Method | Endpoint | Purpose |
|-------|--------|----------|---------|
| Patients | GET | `/api/patients` | List/search patients |
| | GET | `/api/patients/{id}` | Get patient record |
| | POST | `/api/patients` | Register new patient |
| | PUT | `/api/patients/{id}` | Update patient record |
| | DELETE | `/api/patients/{id}` | Remove patient |
| Visits | GET | `/api/visits` | List visits by patient |
| | GET | `/api/visits/{id}` | Get visit record |
| | POST | `/api/visits` | Record new visit |
| | PUT | `/api/visits/{id}` | Update visit record |
| Medications | GET | `/api/medications` | List medications by patient |
| | GET | `/api/medications/active` | Active medications only |
| | POST | `/api/medications` | Prescribe medication |
| Analytics | GET | `/api/analytics/summary` | Dashboard statistics |
| CDSS | POST | `/api/clinic` | Differential diagnosis |
| | POST | `/api/drugs` | Drug interaction check |
| | POST | `/api/maternal` | Maternal risk assessment |
| | POST | `/api/medtranslate` | Medical translation |
| | POST | `/api/assistant` | AI medical chat |
| System | GET | `/` | Serve application |
| | GET | `/health` | Health check + model status |
| | GET | `/manifest.json` | PWA manifest |
| | GET | `/sw.js` | Service worker |

---

## Model Variants

| Ollama Tag | Download | VRAM (Q4) | Active Params | Best For |
|------------|----------|-----------|---------------|----------|
| `gemma4:e2b` | 7.2 GB | 4 GB | 2.3B | Phones, low-end hardware, 2-bit quantization |
| `gemma4:e4b` | 9.6 GB | 6 GB | 4.5B | **Default** -- best balance of speed and quality |
| `gemma4:26b` | 18 GB | 18 GB | 3.8B (MoE) | Higher accuracy, dedicated GPU |
| `gemma4:31b` | 20 GB | 20 GB | 30.7B | Maximum quality, research workstations |

Switch models:

```bash
GEMMA_MODEL=gemma4:e2b python run.py
```

---

## Hackathon Tracks

| Track | Fit |
|-------|-----|
| **Health & Sciences** | Primary target -- complete HMS with CDSS for underserved communities |
| **Main Track** | General social good through accessible healthcare infrastructure |
| **Ollama Special Tech** | Runs entirely on Ollama with local inference |

---

## Project Structure

```
gemma-medical/
├── run.py                  # Quick-start entry point
├── requirements.txt        # Python dependencies
├── backend/
│   ├── main.py             # FastAPI app with all 22 routes
│   ├── config.py           # Model and runtime configuration
│   ├── ollama_client.py    # Ollama API integration
│   ├── prompts/            # System prompts for each CDSS tool
│   ├── routers/
│   │   ├── patients.py     # Patient registry CRUD
│   │   ├── visits.py       # Visit record management
│   │   ├── medications.py  # Medication tracking
│   │   ├── analytics.py    # Dashboard statistics
│   │   ├── clinic.py       # Clinic Copilot (diagnosis)
│   │   ├── drugs.py        # Drug interaction checker
│   │   ├── maternal.py     # Maternal health monitor
│   │   ├── medtranslate.py # Medical translator
│   │   └── assistant.py    # General AI assistant
│   └── services/           # Business logic layer
├── frontend/
│   ├── index.html          # Single-page application
│   ├── assets/             # Images and icons
│   ├── css/                # Stylesheets
│   └── js/                 # Client-side JavaScript
├── data/                   # Local JSON storage (patients, visits, medications)
├── docs/
│   ├── kaggle-writeup.md   # Competition submission writeup
│   └── video-script.md     # Demo video script
├── ENVIRONMENT.md          # Full environment and reproducibility guide
└── LICENSE                 # MIT (code) + CC-BY 4.0 (docs)
```

---

## License

Dual licensed:

- **Code**: [MIT License](LICENSE)
- **Documentation and written content**: [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

Built by **Corey Redwine** for the Gemma 4 Good Hackathon.

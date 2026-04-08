# Gemma Medical -- Environment & Reproducibility Guide

## Runtime Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.10+ | Tested on 3.11.9 |
| Ollama | 0.20.0+ | Required for Gemma 4 support |
| OS | Windows 11, Linux, macOS | Cross-platform |
| RAM | 8 GB minimum | 16 GB recommended for smooth inference |
| GPU | Optional | NVIDIA GPU with 6+ GB VRAM improves speed; CPU inference works but slower |

## Quick Start

### One-Click Install (Recommended)

```bash
python install.py
```

This automatically installs Ollama, pulls Gemma 4, installs Python dependencies, and creates launcher scripts. Use `--silent` for zero-prompt mode.

### Manual Install

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install and start Ollama
# https://ollama.com/download

# Pull Gemma 4 model (one-time, ~9.6 GB download)
ollama pull gemma4:e4b

# Start Gemma Medical
python run.py
```

Open http://localhost:8000 in your browser.

## Setup Script

The run.py script includes a setup mode that verifies Ollama is running and pulls the model:

```bash
# Verify Ollama + pull model in one step
python run.py --setup

# Then start the server
python run.py
```

## Standalone Executable

Build a distributable .exe with PyInstaller:

```bash
python build_exe.py
```

Output: `dist/GemmaMedical/GemmaMedical.exe`. Zip the folder and distribute. Users still need Ollama installed separately on the target machine.

## Docker Deployment

```bash
docker compose up
```

Starts both Gemma Medical (port 8000) and Ollama (port 11434) with GPU passthrough.

The `docker-compose.yml` includes:
- **gemma-medical** service: the web application on port 8000
- **ollama** service: local AI inference on port 11434 with NVIDIA GPU passthrough and persistent volume

## Python Dependencies

All dependencies are pinned in `requirements.txt`:

- fastapi 0.115.0
- uvicorn 0.30.6
- httpx 0.27.2
- pydantic 2.9.2
- python-multipart 0.0.12
- jinja2 3.1.4
- aiofiles 24.1.0

## Model Variants

| Ollama Tag | Download | VRAM (Q4) | Active Params | Best For |
|------------|----------|-----------|---------------|----------|
| `gemma4:e2b` | 7.2 GB | 4 GB | 2.3B | Phones, low-end hardware |
| `gemma4:e4b` | 9.6 GB | 6 GB | 4.5B | **Default** -- best balance of speed and quality |
| `gemma4:26b` | 18 GB | 18 GB | 3.8B (MoE) | Higher accuracy, needs dedicated GPU |
| `gemma4:31b` | 20 GB | 20 GB | 30.7B | Maximum quality, research workstations |

Default model: `gemma4:e4b` (configurable via `GEMMA_MODEL` environment variable).

### Switching Models

```bash
# Use the smallest model (phones/low-end devices)
GEMMA_MODEL=gemma4:e2b python run.py

# Use the largest model (research workstations)
ollama pull gemma4:31b
GEMMA_MODEL=gemma4:31b python run.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `GEMMA_MODEL` | `gemma4:e4b` | Which Gemma 4 variant to use |
| `MAX_TOKENS` | `4096` | Maximum response length |
| `TEMPERATURE` | `0.3` | Model temperature (lower = more deterministic) |

## Tested Platforms

- Windows 11 Pro (NVIDIA RTX GPU)
- Ubuntu 22.04 (NVIDIA T4, Kaggle environment)
- macOS 14+ (Apple Silicon, CPU inference)
- Docker (NVIDIA Container Toolkit)

## Troubleshooting

**Ollama not found:** Install from https://ollama.com/download and ensure `ollama` is on your PATH.

**Model not downloaded:** Run `ollama pull gemma4:e4b` (or whichever variant you want). First pull downloads ~9.6 GB.

**Slow inference on CPU:** This is expected. Use a smaller model (`gemma4:e2b`) or add a GPU. Even a mid-range NVIDIA card with 6 GB VRAM will significantly improve response times.

**Port 8000 already in use:** Another service is using that port. Either stop it or start Gemma Medical on a different port: `uvicorn backend.main:app --port 8080`.

## Hardware Recommendations for Developing Countries

Gemma Medical is designed to run on the hardware commonly available in clinics across developing regions.

| Setup | Hardware | Model | Notes |
|-------|----------|-------|-------|
| **Minimum** | Any laptop, 8 GB RAM, no GPU | `gemma4:e2b` | CPU inference, slower but functional |
| **Recommended** | Desktop/laptop, 16 GB RAM, any NVIDIA GPU (4+ GB VRAM) | `gemma4:e4b` | Good balance of speed and accuracy |
| **Shared clinic server** | 32 GB RAM, NVIDIA GPU 8+ GB VRAM | `gemma4:e4b` | Serves multiple concurrent users over LAN |
| **District hospital** | 64 GB RAM, NVIDIA GPU 16+ GB VRAM | `gemma4:26b` | Higher accuracy for complex cases |

**Key considerations for low-resource settings:**

- **Offline-first:** The PWA caches the full UI for offline use. Only AI features require Ollama running.
- **No internet required after install:** Once Ollama and the model are downloaded, everything runs locally.
- **Low bandwidth:** The E2B model is only 7.2 GB total. Download once, copy via USB to other machines.
- **Power outages:** The app starts in seconds and resumes where it left off. Patient data persists locally.
- **USB deployment:** Copy the entire folder (with Ollama installer and model file) to a USB drive for air-gapped clinics.

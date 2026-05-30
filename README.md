# 🌍 ENVIRONMENTAL MONITOR / AI — EcoVision

> **Satellite Analysis · Vegetation Tracking · AI Insights**

A web application that uses satellite imagery and artificial intelligence to detect
and measure environmental change — from forest loss to urban sprawl — across the
Philippines and beyond, powered by a local Ollama AI model running on your GPU.

---

## 📋 FEATURES

- 🗺️ Interactive map with polygon and rectangle drawing tools
- 📅 Historical satellite image comparison (2013–2020)
- 🤖 AI-powered environmental analysis via local **Phi-3** model
- 🌿 NDVI vegetation tracking and forest coverage estimation
- ⚡ GPU-accelerated inference with **CUDA 12.6** support
- 💬 Real-time AI chat assistant with streamed responses
- 🖥️ GPU health monitoring via dedicated CLI tool (EcoVision GPU Monitor)

---

## 🖥️ SYSTEM REQUIREMENTS

- Python **3.10+**
- NVIDIA GPU with **CUDA 12.6** support
- [Ollama](https://ollama.com) installed and running locally
- ~6 GB VRAM recommended (for Phi-3)
- VS Code (recommended for split-terminal workflow)

---

## ⚙️ ENVIRONMENT SETUP

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ecovision.git
```

---

### 2. Install PyTorch with CUDA 12.6

> ⚠️ Run this BEFORE installing requirements.txt to ensure the CUDA build is used.

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set Up Ollama with Phi-3

Make sure [Ollama](https://ollama.com) is installed on your machine, then pull the Phi-3 model:

```bash
ollama pull phi3
```

Start the Ollama server:

```bash
ollama serve
```

> ✅ The app connects to Ollama at `http://localhost:11434` by default.
> Keep this running in the background while using the application.

---

## 🚀 RUNNING THE APPLICATION

### Terminal 1 — Start the Flask Web Server

```bash
python app.py
```

Then open your browser and navigate to:

```
http://localhost:5000
```

---

### Terminal 2 — GPU Health Monitor (EcoVision GPU Monitor)

Open a **second terminal** in VS Code and run:

```bash
python gpu_monitor_cli.py
```

> 💡 In VS Code: use **Ctrl + Shift + `** to open a new terminal,
> or click the **Split Terminal** icon to view both side by side.

#### Optional Flags

| Flag                  | Description                                          | Default      |
|-----------------------|------------------------------------------------------|--------------|
| `--interval <secs>`   | Refresh rate in seconds                              | `1`          |
| `--gpu <index>`       | GPU device index to monitor                          | `0`          |
| `--log`               | Also write metrics to `gpu_log.csv`                  | off          |
| `--no-color`          | Plain text output (useful for piping or CI)          | off          |

#### Examples

```bash
# Default live dashboard, refresh every 1 second
python gpu_monitor_cli.py

# Refresh every 2 seconds
python gpu_monitor_cli.py --interval 2

# Also log metrics to gpu_log.csv
python gpu_monitor_cli.py --log

# Plain text output (no colour)
python gpu_monitor_cli.py --no-color

# Monitor a specific GPU (e.g. second GPU at index 1)
python gpu_monitor_cli.py --gpu 1
```

#### What It Displays

| Metric              | Description                                    |
|---------------------|------------------------------------------------|
| Core Util           | GPU core utilisation (%)                       |
| Mem B/W             | Memory bandwidth utilisation (%)               |
| VRAM                | Used / total VRAM in MB + percentage           |
| Temperature         | GPU core temperature (°C) — green/yellow/red   |
| Power               | Current draw (W) vs power limit (W)            |
| SM Clock            | Shader / streaming multiprocessor clock (MHz)  |
| Mem Clock           | Memory clock speed (MHz)                       |
| Fan                 | Fan speed (%) if available                     |
| GPU Processes       | Active compute PIDs and their VRAM usage       |

> Metrics are colour-coded: 🟢 Normal · 🟡 Moderate · 🔴 High

---

## 📦 REQUIREMENTS.TXT

```bash
anyio==4.13.0
anywidget==0.11.0
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
arrow==1.4.0
asttokens==3.0.1
async-lru==2.3.0
attrs==26.1.0
babel==2.18.0
beautifulsoup4==4.14.3
bleach==6.3.0
blessings==1.7
blinker==1.9.0
bqplot==0.13.1
bqscales==0.3.7
branca==0.8.2
certifi==2026.4.22
cffi==2.0.0
charset-normalizer==3.4.7
click==8.3.3
colorama==0.4.6
comm==0.2.3
contourpy==1.3.3
cryptography==48.0.0
cycler==0.12.1
debugpy==1.8.20
decorator==5.2.1
defusedxml==0.7.1
earthengine-api==1.7.25
ee==0.2
eerepr==0.1.2
executing==2.2.1
fastjsonschema==2.21.2
filelock==3.29.0
Flask==3.1.3
folium==0.20.0
fonttools==4.62.1
fqdn==1.5.1
fsspec==2026.4.0
future==1.0.0
geemap==0.37.2
geocoder==1.38.1
geographiclib==2.1
geopy==2.4.1
google-api-core==2.30.3
google-api-python-client==2.196.0
google-auth==2.52.0
google-auth-httplib2==0.4.0
google-cloud-core==2.6.0
google-cloud-storage==3.10.1
google-crc32c==1.8.0
google-resumable-media==2.9.0
googleapis-common-protos==1.75.0
h11==0.16.0
httpcore==1.0.9
httplib2==0.31.2
httpx==0.28.1
idna==3.13
ipyevents==2.0.4
ipyfilechooser==0.6.0
ipykernel==7.2.0
ipyleaflet==0.20.0
ipython==9.13.0
ipython_pygments_lexers==1.1.1
ipywidgets==8.1.8
isoduration==20.11.0
itsdangerous==2.2.0
jedi==0.20.0
Jinja2==3.1.6
json5==0.14.0
jsonpointer==3.1.1
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
jupyter==1.1.1
jupyter-console==6.6.3
jupyter-events==0.12.1
jupyter-leaflet==0.20.0
jupyter-lsp==2.3.1
jupyter_client==8.8.0
jupyter_core==5.9.1
jupyter_server==2.18.2
jupyter_server_terminals==0.5.4
jupyterlab==4.5.7
jupyterlab_pygments==0.3.0
jupyterlab_server==2.28.0
jupyterlab_widgets==3.0.16
kiwisolver==1.5.0
lark==1.3.1
MarkupSafe==3.0.3
matplotlib==3.10.9
matplotlib-inline==0.2.2
mistune==3.2.1
mpmath==1.3.0
narwhals==2.21.0
nbclient==0.10.4
nbconvert==7.17.1
nbformat==5.10.4
nest-asyncio==1.6.0
networkx==3.6.1
notebook==7.5.6
notebook_shim==0.2.4
numpy==2.4.4
packaging==26.2
pandas==3.0.2
pandocfilters==1.5.1
parso==0.8.7
pillow==12.2.0
platformdirs==4.9.6
plotly==6.7.0
prometheus_client==0.25.0
prompt_toolkit==3.0.52
proto-plus==1.28.0
protobuf==7.34.1
psutil==7.2.2
psycopg2==2.9.12
psygnal==0.15.1
pure_eval==0.2.3
pyasn1==0.6.3
pyasn1_modules==0.4.2
pycparser==3.0
Pygments==2.20.0
pyparsing==3.3.2
pyperclip==1.11.0
pyshp==3.0.3
python-box==7.4.1
python-dateutil==2.9.0.post0
python-json-logger==4.1.0
pywinpty==3.0.3
PyYAML==6.0.3
pyzmq==27.1.0
ratelim==0.1.6
referencing==0.37.0
requests==2.33.1
rfc3339-validator==0.1.4
rfc3986-validator==0.1.1
rfc3987-syntax==1.1.0
rpds-py==0.30.0
scooby==0.11.2
Send2Trash==2.1.0
setuptools==81.0.0
six==1.17.0
soupsieve==2.8.3
stack-data==0.6.3
sympy==1.14.0
terminado==0.18.1
tinycss2==1.4.0
tornado==6.5.5
traitlets==5.15.0
traittypes==0.2.3
typing_extensions==4.15.0
tzdata==2026.2
uri-template==1.3.0
uritemplate==4.2.0
urllib3==2.7.0
wcwidth==0.7.0
webcolors==25.10.0
webencodings==0.5.1
websocket-client==1.9.0
Werkzeug==3.1.8
widgetsnbextension==4.0.15
xyzservices==2026.3.0

```

> ⚠️ Do **NOT** add `torch` or `torchvision` to `requirements.txt`.
> They must be installed separately using the CUDA wheel URL in Step 2
> to avoid pip replacing them with the CPU-only build.

---

## 📁 PROJECT STRUCTURE

```
ecovision/
│
├── app.py                  # Flask backend / main entry point
├── gpu_monitor_cli.py      # EcoVision GPU Monitor CLI (run in second terminal)
├── requirements.txt        # Python dependencies (no torch here)
│
├── templates/
│   └── index.html          # Main frontend (Leaflet map + AI chat)
│
└── static/
    ├── style.css           # Stylesheet
    └── images/
        ├── logo.png        # App logo / favicon
        └── bot_profile.png # AI chat avatar
```

---

## 🔧 TROUBLESHOOTING

| Problem                          | Fix                                                                          |
|----------------------------------|------------------------------------------------------------------------------|
| Ollama not responding            | Run `ollama serve` in a separate terminal                                    |
| CUDA not detected                | Run `python -c "import torch; print(torch.cuda.is_available())"`             |
| Phi-3 model not found            | Run `ollama pull phi3`                                                       |
| Port 5000 already in use         | Change the port in `app.py` or kill the existing process                     |
| torch installed without CUDA     | Reinstall using the CUDA wheel URL in Step 2                                 |
| GPU monitor shows no data        | Ensure `pynvml` is installed: `pip install pynvml`                           |
| GPU monitor has no colours/bars  | Ensure `rich` is installed: `pip install rich`                               |
| gpu_log.csv not created          | Add the `--log` flag: `python gpu_monitor_cli.py --log`                      |

---

## ✅ QUICK START CHECKLIST

```
[ ] GPU drivers and CUDA 12.6 installed
[ ] Python 3.10+ installed
[ ] Ollama installed
[ ] ollama pull phi3
[ ] ollama serve  (running in background)
[ ] pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
[ ] pip install -r requirements.txt
[ ] python app.py                  ← Terminal 1
[ ] python gpu_monitor_cli.py      ← Terminal 2 in VS Code
[ ] Open http://localhost:5000 in browser
```

---

## 🧠 HOW IT WORKS

1. **Choose a Country & Year** — Select a country and historical baseline year (back to 2013)
2. **Draw on the Map** — Use the polygon or rectangle tool to outline any region
3. **Compare Satellite Images** — A historical snapshot is placed side-by-side with current imagery
4. **Read the AI Analysis** — Phi-3 estimates forest coverage change, population shifts,
   and environmental degradation as percentages and interactive charts
5. **Chat with the AI** — Ask follow-up questions via the built-in chat panel

---

## 📄 LICENSE

MIT License — feel free to use, modify, and distribute.

---

## 🙏 ACKNOWLEDGEMENTS

- [Leaflet.js](https://leafletjs.com/) — Interactive maps
- [Ollama](https://ollama.com/) — Local LLM inference engine
- [Microsoft Phi-3](https://azure.microsoft.com/en-us/products/phi-3) — AI language model
- [PyTorch](https://pytorch.org/) — CUDA-accelerated ML framework
- [Chart.js](https://www.chartjs.org/) — Data visualization
- [Rich](https://github.com/Textualize/rich) — Terminal UI for GPU monitor
- [pynvml](https://github.com/gpuopenanalytics/pynvml) — NVIDIA GPU metrics

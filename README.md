# 🌍 ENVIRONMENTAL MONITOR / AI

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
- 🖥️ GPU health monitoring via dedicated CLI tool

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
git clone https://github.com/yourusername/environmental-monitor-ai.git
cd environmental-monitor-ai
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

### Terminal 2 — GPU Health Monitor

Open a **second terminal** in VS Code and run:

```bash
python gpu_monitor_cli.py
```

> 💡 In VS Code: use **Ctrl + Shift + `** to open a new terminal,
> or click the **Split Terminal** icon to view both side by side.

This displays real-time GPU stats including:

| Metric          | Description                  |
|-----------------|------------------------------|
| GPU Utilization | Processing load (%)          |
| VRAM Usage      | Memory used / total (MB)     |
| Temperature     | GPU core temperature (°C)    |
| Power Draw      | Current power consumption (W)|

---

## 📦 REQUIREMENTS.TXT

```bash
flask
flask-cors
requests
numpy
Pillow
pynvml
```

> ⚠️ Do **NOT** add `torch` or `torchvision` to `requirements.txt`.
> They must be installed separately using the CUDA wheel URL in Step 2
> to avoid pip replacing them with the CPU-only build.

---


---

## 🔧 TROUBLESHOOTING

| Problem                          | Fix                                                                 |
|----------------------------------|---------------------------------------------------------------------|
| Ollama not responding            | Run `ollama serve` in a separate terminal                           |
| CUDA not detected                | Run `python -c "import torch; print(torch.cuda.is_available())"`   |
| Phi-3 model not found            | Run `ollama pull phi3`                                              |
| Port 5000 already in use         | Change the port in `app.py` or kill the existing process           |
| torch installed without CUDA     | Reinstall using the CUDA wheel URL in Step 2                        |
| GPU monitor shows no data        | Ensure `pynvml` is installed and an NVIDIA GPU is present          |

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
[ ] python app.py  (Terminal 1)
[ ] python gpu_monitor_cli.py  (Terminal 2 in VS Code)
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


## 🙏 ACKNOWLEDGEMENTS

- [Leaflet.js](https://leafletjs.com/) — Interactive maps
- [Ollama](https://ollama.com/) — Local LLM inference engine
- [Microsoft Phi-3](https://azure.microsoft.com/en-us/products/phi-3) — AI language model
- [PyTorch](https://pytorch.org/) — CUDA-accelerated ML framework
- [Chart.js](https://www.chartjs.org/) — Data visualization

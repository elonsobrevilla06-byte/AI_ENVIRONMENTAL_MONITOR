"""
gpu_bp.py  ──  GPU metrics API blueprint
----------------------------------------
Mount this in your Flask app:

    from gpu_bp import gpu_bp
    app.register_blueprint(gpu_bp)

Then poll  GET /api/gpu/stats  from the UI dashboard.
No existing logic is touched; this is purely additive.

Requirements:
    pip install pynvml
"""

from flask import Blueprint, jsonify
from datetime import datetime
import torch
import os

gpu_bp = Blueprint("gpu_bp", __name__)

# ── pynvml setup ───────────────────────────────────────────────────────────────
try:
    import pynvml
    pynvml.nvmlInit()
    _NVML     = True
    _GPU_COUNT = pynvml.nvmlDeviceGetCount()
except Exception:
    _NVML      = False
    _GPU_COUNT = 0


def _collect(idx: int = 0) -> dict:
    stats = {
        "timestamp":      datetime.now().isoformat(timespec="seconds"),
        "gpu_index":      idx,
        "gpu_count":      _GPU_COUNT,
        "nvml_available": _NVML,
        "gpu_name":       "N/A",
        "util_gpu":       0,
        "util_mem_bw":    0,
        "mem_used_mb":    0,
        "mem_total_mb":   0,
        "mem_pct":        0.0,
        "temp_c":         0,
        "power_w":        0.0,
        "power_limit_w":  0.0,
        "clock_sm_mhz":   0,
        "clock_mem_mhz":  0,
        "fan_pct":        None,
        "process_count":  0,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version":   torch.version.cuda or "N/A",
        "torch_version":  torch.__version__,
    }

    if not _NVML:
        return stats

    try:
        h = pynvml.nvmlDeviceGetHandleByIndex(idx)

        name = pynvml.nvmlDeviceGetName(h)
        stats["gpu_name"] = name.decode() if isinstance(name, bytes) else name

        util                   = pynvml.nvmlDeviceGetUtilizationRates(h)
        stats["util_gpu"]      = util.gpu
        stats["util_mem_bw"]   = util.memory

        mem                    = pynvml.nvmlDeviceGetMemoryInfo(h)
        stats["mem_used_mb"]   = mem.used  // (1024 ** 2)
        stats["mem_total_mb"]  = mem.total // (1024 ** 2)
        stats["mem_pct"]       = round(mem.used / mem.total * 100, 1) if mem.total else 0

        stats["temp_c"]        = pynvml.nvmlDeviceGetTemperature(
                                     h, pynvml.NVML_TEMPERATURE_GPU)

        try:
            stats["power_w"]       = round(pynvml.nvmlDeviceGetPowerUsage(h) / 1000, 1)
            stats["power_limit_w"] = round(pynvml.nvmlDeviceGetEnforcedPowerLimit(h) / 1000, 0)
        except pynvml.NVMLError:
            pass

        try:
            stats["clock_sm_mhz"]  = pynvml.nvmlDeviceGetClockInfo(h, pynvml.NVML_CLOCK_SM)
            stats["clock_mem_mhz"] = pynvml.nvmlDeviceGetClockInfo(h, pynvml.NVML_CLOCK_MEM)
        except pynvml.NVMLError:
            pass

        try:
            stats["fan_pct"]       = pynvml.nvmlDeviceGetFanSpeed(h)
        except pynvml.NVMLError:
            pass

        try:
            procs                  = pynvml.nvmlDeviceGetComputeRunningProcesses(h)
            stats["process_count"] = len(procs)
        except pynvml.NVMLError:
            pass

    except Exception as e:
        stats["error"] = str(e)

    return stats


@gpu_bp.route("/api/gpu/stats", methods=["GET"])
def gpu_stats():
    """Return current GPU metrics as JSON. Polled by the UI dashboard."""
    all_gpus = [_collect(i) for i in range(max(1, _GPU_COUNT))]
    return jsonify({"gpus": all_gpus, "count": len(all_gpus)})
"""
gpu_monitor_cli.py
------------------
Real-time GPU / CUDA performance monitor for the EcoVision analysis pipeline.
Tracks utilisation, memory, temperature, and power — both during analysis and at idle.

Usage:
    python gpu_monitor_cli.py              # live dashboard, refresh every 1 s
    python gpu_monitor_cli.py --interval 2 # refresh every 2 s
    python gpu_monitor_cli.py --log        # also write CSV to gpu_log.csv
    python gpu_monitor_cli.py --no-color   # plain text (for piping / CI)

Requirements:
    pip install pynvml rich
    (pynvml ships with NVIDIA drivers; rich is the TUI renderer)
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime

# ── optional colour / TUI support ──────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, TextColumn
    from rich.table import Table
    from rich.text import Text
    RICH = True
except ImportError:
    RICH = False
    print("[WARN] `rich` not installed – falling back to plain output. "
          "Install with: pip install rich", file=sys.stderr)

# ── GPU backend ────────────────────────────────────────────────────────────────
try:
    import pynvml
    pynvml.nvmlInit()
    NVML = True
    GPU_COUNT = pynvml.nvmlDeviceGetCount()
except Exception:
    NVML = False
    GPU_COUNT = 0

try:
    import torch
    TORCH = True
except ImportError:
    TORCH = False


# ══════════════════════════════════════════════════════════════════════════════
# Data collection
# ══════════════════════════════════════════════════════════════════════════════

def _nvml_handle(idx: int = 0):
    return pynvml.nvmlDeviceGetHandleByIndex(idx)


def collect_gpu_stats(idx: int = 0) -> dict:
    """Return a dict of GPU metrics for device *idx*."""
    stats = {
        "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gpu_index":      idx,
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
        "fan_pct":        "N/A",
        "processes":      [],
        "cuda_available": torch.cuda.is_available() if TORCH else False,
        "cuda_version":   torch.version.cuda if TORCH else "N/A",
        "torch_version":  torch.__version__ if TORCH else "N/A",
    }

    if not NVML:
        return stats

    try:
        h = _nvml_handle(idx)

        stats["gpu_name"]      = pynvml.nvmlDeviceGetName(h)
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
            stats["power_w"]       = pynvml.nvmlDeviceGetPowerUsage(h) / 1000
            stats["power_limit_w"] = pynvml.nvmlDeviceGetEnforcedPowerLimit(h) / 1000
        except pynvml.NVMLError:
            pass

        try:
            stats["clock_sm_mhz"]  = pynvml.nvmlDeviceGetClockInfo(
                                         h, pynvml.NVML_CLOCK_SM)
            stats["clock_mem_mhz"] = pynvml.nvmlDeviceGetClockInfo(
                                         h, pynvml.NVML_CLOCK_MEM)
        except pynvml.NVMLError:
            pass

        try:
            stats["fan_pct"]       = pynvml.nvmlDeviceGetFanSpeed(h)
        except pynvml.NVMLError:
            pass

        try:
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(h)
            stats["processes"] = [
                {"pid": p.pid, "mem_mb": (p.usedGpuMemory or 0) // (1024 ** 2)}
                for p in procs
            ]
        except pynvml.NVMLError:
            pass

    except Exception as exc:
        stats["error"] = str(exc)

    return stats


def _bar(value: int, maximum: int = 100, width: int = 20) -> str:
    """ASCII progress bar."""
    filled = int(width * value / maximum) if maximum else 0
    return "[" + "█" * filled + "░" * (width - filled) + f"] {value:3d}%"


def _colour(value: int, low: int = 30, high: int = 70) -> str:
    """ANSI colour code based on thresholds (plain-text fallback)."""
    if value >= high:
        return "\033[91m"   # red
    if value >= low:
        return "\033[93m"   # yellow
    return "\033[92m"       # green


RESET = "\033[0m"


# ══════════════════════════════════════════════════════════════════════════════
# Plain-text renderer
# ══════════════════════════════════════════════════════════════════════════════

def render_plain(stats: dict, use_color: bool = True) -> str:
    c  = _colour if use_color else (lambda *a, **kw: "")
    rs = RESET if use_color else ""

    lines = [
        "=" * 62,
        f"  EcoVision GPU Monitor  │  {stats['timestamp']}",
        "=" * 62,
    ]

    if not NVML:
        lines.append("  [!] pynvml not available – install with: pip install pynvml")
    else:
        gpu_c = c(stats["util_gpu"])
        mem_c = c(int(stats["mem_pct"]))
        tmp_c = c(stats["temp_c"], 60, 80)

        lines += [
            f"  GPU  : {stats['gpu_name']}  (index {stats['gpu_index']})",
            f"  CUDA : {stats['cuda_version']}  │  PyTorch {stats['torch_version']}",
            "",
            f"  Core util : {gpu_c}{_bar(stats['util_gpu'])}{rs}",
            f"  Mem  BW   : {mem_c}{_bar(stats['util_mem_bw'])}{rs}",
            (f"  VRAM      : {mem_c}{stats['mem_used_mb']:,} / "
             f"{stats['mem_total_mb']:,} MB  ({stats['mem_pct']}%){rs}"),
            f"  Temp      : {tmp_c}{stats['temp_c']} °C{rs}",
            (f"  Power     : {stats['power_w']:.1f} W  "
             f"/ {stats['power_limit_w']:.0f} W limit"),
            f"  SM clock  : {stats['clock_sm_mhz']} MHz",
            f"  Mem clock : {stats['clock_mem_mhz']} MHz",
            (f"  Fan       : {stats['fan_pct']}%"
             if isinstance(stats['fan_pct'], int) else "  Fan       : N/A"),
            "",
            f"  Active GPU processes: {len(stats['processes'])}",
        ]

        for p in stats["processes"]:
            lines.append(f"    PID {p['pid']:>6}  │  {p['mem_mb']:>5} MB VRAM")

    lines.append("=" * 62)
    lines.append("  Press Ctrl-C to quit")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# Rich renderer
# ══════════════════════════════════════════════════════════════════════════════

def _rich_bar_colour(value: int) -> str:
    if value >= 70:
        return "red"
    if value >= 30:
        return "yellow"
    return "green"


def render_rich(stats: dict) -> Panel:
    """Build a Rich renderable for the live display."""

    # ── header info ───────────────────────────────────────────────────────────
    header = Table.grid(expand=True)
    header.add_column(ratio=1)
    header.add_column(ratio=1)
    header.add_row(
        Text(f"  {stats.get('gpu_name', 'No GPU')}  (index {stats['gpu_index']})",
             style="bold cyan"),
        Text(f"CUDA {stats['cuda_version']}  ·  PyTorch {stats['torch_version']}",
             style="dim", justify="right"),
    )

    # ── utilisation bars ──────────────────────────────────────────────────────
    prog = Progress(
        TextColumn("[bold]{task.description:<16}"),
        BarColumn(bar_width=32),
        TextColumn("[bold]{task.percentage:>5.1f}%"),
        expand=False,
    )
    t_gpu  = prog.add_task("Core Util",   total=100, completed=stats["util_gpu"])
    t_bw   = prog.add_task("Mem B/W",     total=100, completed=stats["util_mem_bw"])
    t_vram = prog.add_task("VRAM",        total=100, completed=stats["mem_pct"])
    # colour overrides
    prog.columns[1].style         = _rich_bar_colour(stats["util_gpu"])
    # (colour per task not natively supported in rich Progress bar column the easy
    #  way, but the dominant colour still reads well)

    # ── stats table ───────────────────────────────────────────────────────────
    tbl = Table(show_header=False, box=None, padding=(0, 2))
    tbl.add_column(style="dim", min_width=14)
    tbl.add_column(style="bold")

    temp_style = "red" if stats["temp_c"] >= 80 else \
                 "yellow" if stats["temp_c"] >= 60 else "green"

    tbl.add_row("VRAM",
                f"{stats['mem_used_mb']:,} / {stats['mem_total_mb']:,} MB")
    tbl.add_row("Temperature",
                Text(f"{stats['temp_c']} °C", style=temp_style))
    tbl.add_row("Power",
                f"{stats['power_w']:.1f} W  / {stats['power_limit_w']:.0f} W")
    tbl.add_row("SM Clock",    f"{stats['clock_sm_mhz']} MHz")
    tbl.add_row("Mem Clock",   f"{stats['clock_mem_mhz']} MHz")
    fan = stats["fan_pct"]
    tbl.add_row("Fan",         f"{fan}%" if isinstance(fan, int) else "N/A")
    tbl.add_row("GPU procs",   str(len(stats["processes"])))

    # ── process list ─────────────────────────────────────────────────────────
    proc_lines = Text()
    if stats["processes"]:
        for p in stats["processes"]:
            proc_lines.append(f"  PID {p['pid']:>6}  ", style="dim")
            proc_lines.append(f"{p['mem_mb']:>5} MB VRAM\n", style="cyan")
    else:
        proc_lines.append("  (no active GPU compute processes)\n", style="dim italic")

    # ── assemble layout ───────────────────────────────────────────────────────
    layout = Layout()
    layout.split_column(
        Layout(header,     name="head",  size=2),
        Layout(name="mid", size=8),
        Layout(proc_lines, name="procs", size=max(2, len(stats["processes"]) + 1)),
    )
    layout["mid"].split_row(
        Layout(prog, name="bars", ratio=2),
        Layout(tbl,  name="nums", ratio=2),
    )

    timestamp = stats["timestamp"]
    idle_hint = ""
    if stats["util_gpu"] < 5 and not stats["processes"]:
        idle_hint = "  [dim]● idle[/dim]"

    return Panel(
        layout,
        title=f"[bold white]EcoVision GPU Monitor[/bold white]{idle_hint}",
        subtitle=f"[dim]{timestamp}  ·  Ctrl-C to quit[/dim]",
        border_style="bright_blue",
        padding=(0, 1),
    )


# ══════════════════════════════════════════════════════════════════════════════
# CSV logger
# ══════════════════════════════════════════════════════════════════════════════

CSV_FIELDS = [
    "timestamp", "gpu_index", "util_gpu", "util_mem_bw",
    "mem_used_mb", "mem_total_mb", "mem_pct",
    "temp_c", "power_w", "clock_sm_mhz", "clock_mem_mhz",
]

def log_csv(stats: dict, path: str = "gpu_log.csv"):
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        if write_header:
            w.writeheader()
        w.writerow({k: stats.get(k, "") for k in CSV_FIELDS})


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Real-time GPU monitor for EcoVision analysis pipeline.")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Refresh interval in seconds (default: 1)")
    parser.add_argument("--gpu",      type=int,   default=0,
                        help="GPU device index to monitor (default: 0)")
    parser.add_argument("--log",      action="store_true",
                        help="Write metrics to gpu_log.csv")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI color in plain-text mode")
    args = parser.parse_args()

    if not NVML:
        print("[ERROR] pynvml is required:  pip install pynvml")
        print("        Showing stub output …\n")

    if RICH:
        console = Console()
        with Live(console=console, refresh_per_second=max(1, int(1 / args.interval)),
                  screen=True) as live:
            while True:
                stats = collect_gpu_stats(args.gpu)
                if args.log:
                    log_csv(stats)
                live.update(render_rich(stats))
                time.sleep(args.interval)
    else:
        use_color = not args.no_color and sys.stdout.isatty()
        try:
            while True:
                stats = collect_gpu_stats(args.gpu)
                if args.log:
                    log_csv(stats)
                os.system("cls" if os.name == "nt" else "clear")
                print(render_plain(stats, use_color=use_color))
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nBye.")


if __name__ == "__main__":
    main()
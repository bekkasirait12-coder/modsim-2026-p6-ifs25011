"""
simulation.py
Modul inti simulasi Pembagian Lembar Jawaban Ujian
Modsim 2026 - Praktikum 6: Verification & Validation
"""

import random
import numpy as np
import pandas as pd


def run_simulation(
    n_students: int = 30,
    min_duration: float = 1.0,
    max_duration: float = 3.0,
    seed: int | None = None,
) -> dict:
    """
    Menjalankan simulasi pembagian lembar jawaban ujian (single-server FIFO).

    Parameters
    ----------
    n_students   : Jumlah mahasiswa
    min_duration : Durasi minimum pelayanan (menit)
    max_duration : Durasi maksimum pelayanan (menit)
    seed         : Random seed (None = acak)

    Returns
    -------
    dict berisi:
        events       : list of dict per mahasiswa
        total_time   : total waktu seluruh pembagian (menit)
        avg_wait     : rata-rata waktu tunggu mahasiswa
        service_times: list durasi pelayanan
        utilization  : utilisasi meja pengajar (%)
    """
    if seed is not None:
        random.seed(seed)

    events = []
    current_time = 0.0
    service_times = []

    for i in range(1, n_students + 1):
        duration = random.uniform(min_duration, max_duration)
        service_times.append(duration)

        start_service = current_time          # langsung dilayani (FIFO, 1 server)
        end_service = start_service + duration
        wait_time = 0.0                       # tidak ada tumpang tindih

        events.append({
            "mahasiswa": i,
            "mulai_dilayani": round(start_service, 4),
            "selesai_dilayani": round(end_service, 4),
            "durasi_pelayanan": round(duration, 4),
            "waktu_tunggu": round(wait_time, 4),
        })

        current_time = end_service

    total_time = current_time
    avg_wait = 0.0  # single-server FIFO tanpa kebersamaan = tunggu kumulatif = 0 for each
    # Hitung waktu tunggu sebenarnya (waktu sejak mulai antri = mulai pelayanan mahasiswa ke-i)
    # Mahasiswa 1 tunggu 0, mahasiswa 2 tunggu durasi mhs-1, dst
    wait_times = [events[i]["mulai_dilayani"] for i in range(n_students)]
    avg_wait = np.mean(wait_times)

    utilization = (total_time / total_time) * 100 if total_time > 0 else 0  # server always busy

    return {
        "events": events,
        "total_time": round(total_time, 4),
        "avg_wait": round(avg_wait, 4),
        "service_times": service_times,
        "utilization": utilization,
        "n_students": n_students,
        "min_duration": min_duration,
        "max_duration": max_duration,
    }


# ──────────────────────────────────────────────
# VERIFICATION FUNCTIONS
# ──────────────────────────────────────────────

def verify_logical_flow(result: dict) -> dict:
    """a. Logical Flow Check — tidak ada tumpang tindih waktu pelayanan."""
    events = result["events"]
    overlaps = []
    for i in range(1, len(events)):
        if events[i]["mulai_dilayani"] < events[i - 1]["selesai_dilayani"] - 1e-9:
            overlaps.append((events[i - 1]["mahasiswa"], events[i]["mahasiswa"]))
    passed = len(overlaps) == 0
    return {"passed": passed, "overlaps": overlaps,
            "message": "✅ Tidak ada tumpang tindih — alur FIFO benar." if passed
                       else f"❌ Ditemukan {len(overlaps)} tumpang tindih!"}


def verify_event_tracing(result: dict, n: int = 5) -> pd.DataFrame:
    """b. Event Tracing — tampilkan n mahasiswa pertama."""
    df = pd.DataFrame(result["events"][:n])
    return df[["mahasiswa", "mulai_dilayani", "selesai_dilayani", "durasi_pelayanan"]]


def verify_extreme_conditions(n_students: int = 10) -> pd.DataFrame:
    """c. Extreme Condition Test."""
    rows = []

    # N=1
    r = run_simulation(1, 1, 3, seed=42)
    rows.append({
        "Skenario": "N = 1",
        "Diharapkan": f"~Uniform(1,3) menit",
        "Hasil": f"{r['total_time']:.2f} menit",
        "Status": "✅ Sesuai" if 1 <= r["total_time"] <= 3 else "❌ Tidak Sesuai",
    })

    # Durasi tetap = 1 (set min=max=1)
    r2 = run_simulation(n_students, 1, 1, seed=0)
    expected2 = n_students * 1
    rows.append({
        "Skenario": f"Durasi tetap 1 menit (N={n_students})",
        "Diharapkan": f"{expected2} menit",
        "Hasil": f"{r2['total_time']:.2f} menit",
        "Status": "✅ Sesuai" if abs(r2["total_time"] - expected2) < 0.01 else "❌ Tidak Sesuai",
    })

    # Durasi tetap = 3
    r3 = run_simulation(n_students, 3, 3, seed=0)
    expected3 = n_students * 3
    rows.append({
        "Skenario": f"Durasi tetap 3 menit (N={n_students})",
        "Diharapkan": f"{expected3} menit",
        "Hasil": f"{r3['total_time']:.2f} menit",
        "Status": "✅ Sesuai" if abs(r3["total_time"] - expected3) < 0.01 else "❌ Tidak Sesuai",
    })

    return pd.DataFrame(rows)


def verify_distribution(result: dict) -> dict:
    """d. Distribution Check — semua durasi dalam [min, max]."""
    st = result["service_times"]
    mn, mx = result["min_duration"], result["max_duration"]
    in_range = all(mn <= s <= mx for s in st)
    return {
        "passed": in_range,
        "min_simulated": round(min(st), 4),
        "max_simulated": round(max(st), 4),
        "expected_range": (mn, mx),
        "message": f"✅ Semua durasi dalam [{mn}, {mx}] menit." if in_range
                   else "❌ Ada durasi di luar rentang!",
    }


def verify_reproducibility(n_students: int = 30, seed: int = 42) -> dict:
    """e. Reproducibility Check — seed sama → hasil sama."""
    r1 = run_simulation(n_students, seed=seed)
    r2 = run_simulation(n_students, seed=seed)
    passed = r1["total_time"] == r2["total_time"]
    return {
        "passed": passed,
        "run1_total": r1["total_time"],
        "run2_total": r2["total_time"],
        "message": "✅ Hasil identik — reproducibility terpenuhi." if passed
                   else "❌ Hasil berbeda!",
    }


# ──────────────────────────────────────────────
# VALIDATION FUNCTIONS
# ──────────────────────────────────────────────

def validate_theoretical(result: dict) -> dict:
    """b. Perbandingan dengan perhitungan teoritis."""
    n = result["n_students"]
    mn, mx = result["min_duration"], result["max_duration"]
    e_t = (mn + mx) / 2                  # E[Uniform(a,b)] = (a+b)/2
    theoretical = n * e_t
    simulated = result["total_time"]
    diff_pct = abs(simulated - theoretical) / theoretical * 100
    return {
        "theoretical": round(theoretical, 4),
        "simulated": simulated,
        "e_t": e_t,
        "diff_pct": round(diff_pct, 2),
        "acceptable": diff_pct < 15,      # toleransi 15%
    }


def validate_behavior(n_list=(10, 20, 30, 40), seed=99) -> pd.DataFrame:
    """c. Behavior Validation — N meningkat → total waktu meningkat."""
    rows = []
    prev = None
    for n in n_list:
        r = run_simulation(n, seed=seed)
        increasing = (prev is None) or (r["total_time"] > prev)
        rows.append({
            "N Mahasiswa": n,
            "Total Waktu (menit)": r["total_time"],
            "Meningkat dari sebelumnya": "—" if prev is None else ("✅ Ya" if increasing else "❌ Tidak"),
        })
        prev = r["total_time"]
    return pd.DataFrame(rows)


def validate_sensitivity(n_students=30, seed=42) -> dict:
    """d. Sensitivity Analysis — Uniform(1,3) vs Uniform(2,4)."""
    r1 = run_simulation(n_students, 1, 3, seed=seed)
    r2 = run_simulation(n_students, 2, 4, seed=seed)
    diff = r2["total_time"] - r1["total_time"]
    pct = diff / r1["total_time"] * 100
    return {
        "uniform_1_3": r1["total_time"],
        "uniform_2_4": r2["total_time"],
        "diff": round(diff, 4),
        "pct_increase": round(pct, 2),
        "sensitive": pct > 5,
    }


def run_monte_carlo(
    n_students: int = 30,
    min_duration: float = 1.0,
    max_duration: float = 3.0,
    n_runs: int = 100,
) -> dict:
    """Jalankan banyak replikasi untuk distribusi total waktu."""
    totals = []
    for i in range(n_runs):
        r = run_simulation(n_students, min_duration, max_duration, seed=i)
        totals.append(r["total_time"])
    return {
        "totals": totals,
        "mean": round(np.mean(totals), 4),
        "std": round(np.std(totals), 4),
        "min": round(min(totals), 4),
        "max": round(max(totals), 4),
        "ci_95_low": round(np.percentile(totals, 2.5), 4),
        "ci_95_high": round(np.percentile(totals, 97.5), 4),
    }

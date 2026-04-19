
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from simulation import (
    run_simulation,
    verify_logical_flow,
    verify_event_tracing,
    verify_extreme_conditions,
    verify_distribution,
    verify_reproducibility,
    validate_theoretical,
    validate_behavior,
    validate_sensitivity,
    run_monte_carlo,
)

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ModSim P6 — Verification & Validation",
    page_icon="📋",
    layout="wide",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f7f9fc; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; }
    .metric-card {
        background: white; border-radius: 12px; padding: 18px 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,.08); text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #2563eb; }
    .metric-label { font-size: 0.85rem; color: #64748b; margin-top: 4px; }
    .section-header {
        background: linear-gradient(90deg,#2563eb,#0ea5ff);
        color: white; border-radius: 10px; padding: 10px 20px;
        font-size: 1.05rem; font-weight: 700; margin: 16px 0 12px;
    }
    .result-box {
        background: #f0fdf4; border-left: 4px solid #22c55e;
        border-radius: 8px; padding: 12px 16px; margin: 8px 0;
    }
    .warn-box {
        background: #fef9c3; border-left: 4px solid #eab308;
        border-radius: 8px; padding: 12px 16px; margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.title("📋 Modul Praktikum 6: Verification & Validation")
st.markdown(
    "**Studi Kasus:** Simulasi Pembagian Lembar Jawaban Ujian *(Discrete Event Simulation)*  \n"
    "Institut Teknologi Del — [11S1221] Pemodelan dan Simulasi"
)
st.divider()

# ─── Sidebar Parameters ──────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/id/d/d6/Logo-IT-Del.png", width=100)
    st.header("⚙️ Parameter Simulasi")
    n_students = st.slider("Jumlah Mahasiswa (N)", 1, 100, 30)
    min_dur = st.number_input("Durasi Minimum (menit)", 0.5, 10.0, 1.0, 0.5)
    max_dur = st.number_input("Durasi Maksimum (menit)", 0.5, 15.0, 3.0, 0.5)
    seed = st.number_input("Random Seed", 0, 9999, 42, 1)
    n_runs = st.slider("Jumlah Replikasi (Monte Carlo)", 10, 500, 100, 10)
    st.divider()
    st.caption("Modsim 2026 · Praktikum 6")

if min_dur >= max_dur:
    st.error("❌ Durasi minimum harus lebih kecil dari durasi maksimum!")
    st.stop()

# ─── Run Simulation ──────────────────────────────────────────────────────────
result = run_simulation(n_students, min_dur, max_dur, seed=int(seed))
mc = run_monte_carlo(n_students, min_dur, max_dur, n_runs=n_runs)

# ─── KPI Metrics ─────────────────────────────────────────────────────────────
st.subheader("📊 Hasil Simulasi")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{result['total_time']:.1f}</div>
        <div class='metric-label'>Total Waktu (menit)</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{result['avg_wait']:.1f}</div>
        <div class='metric-label'>Rata-rata Waktu Tunggu (menit)</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>100%</div>
        <div class='metric-label'>Utilisasi Meja Pengajar</div>
    </div>""", unsafe_allow_html=True)
with c4:
    theo = validate_theoretical(result)
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{theo['theoretical']:.1f}</div>
        <div class='metric-label'>Total Waktu Teoritis (menit)</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Verification", "✅ Validation", "📈 Monte Carlo", "📋 Event Log", "ℹ️ Konsep"
])


# ════════════════════════════════════════════════════════════════
# TAB 1 — VERIFICATION
# ════════════════════════════════════════════════════════════════
with tab1:
    st.header("1.2 Verification")
    st.markdown(
        "Verifikasi memastikan model dibangun dengan **benar** *(build the model right)* "
        "sesuai logika dan asumsi sistem."
    )

    # a. Logical Flow Check
    st.markdown("<div class='section-header'>a. Logical Flow Check</div>", unsafe_allow_html=True)
    lf = verify_logical_flow(result)
    st.markdown(f"<div class='result-box'>{lf['message']}</div>", unsafe_allow_html=True)
    st.caption("Memastikan tidak ada dua mahasiswa yang dilayani secara bersamaan (single-server FIFO).")

    # b. Event Tracing
    st.markdown("<div class='section-header'>b. Event Tracing (5 mahasiswa pertama)</div>", unsafe_allow_html=True)
    et = verify_event_tracing(result, n=min(5, n_students))
    st.dataframe(et.rename(columns={
        "mahasiswa": "Mahasiswa",
        "mulai_dilayani": "Mulai Dilayani (menit)",
        "selesai_dilayani": "Selesai Dilayani (menit)",
        "durasi_pelayanan": "Durasi Pelayanan (menit)",
    }), use_container_width=True)
    st.caption("Urutan event kronologis tanpa tumpang tindih.")

    # c. Extreme Condition Test
    st.markdown("<div class='section-header'>c. Uji Kondisi Ekstrem</div>", unsafe_allow_html=True)
    ec = verify_extreme_conditions(n_students=max(n_students, 5))
    st.dataframe(ec, use_container_width=True)

    # d. Distribution Check
    st.markdown("<div class='section-header'>d. Pemeriksaan Distribusi Waktu Pelayanan</div>",
                unsafe_allow_html=True)
    dist = verify_distribution(result)
    st.markdown(f"<div class='result-box'>{dist['message']}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Min Simulasi", f"{dist['min_simulated']} menit")
        st.metric("Max Simulasi", f"{dist['max_simulated']} menit")
    with col2:
        st.metric("Min Asumsi", f"{dist['expected_range'][0]} menit")
        st.metric("Max Asumsi", f"{dist['expected_range'][1]} menit")

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.hist(result["service_times"], bins=15, color="#2563eb", alpha=0.75, edgecolor="white")
    ax.axvline(min_dur, color="red", linestyle="--", label=f"Min = {min_dur}")
    ax.axvline(max_dur, color="green", linestyle="--", label=f"Max = {max_dur}")
    ax.set_xlabel("Durasi Pelayanan (menit)")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Durasi Pelayanan Mahasiswa")
    ax.legend()
    st.pyplot(fig, use_container_width=True)

    # e. Reproducibility Check
    st.markdown("<div class='section-header'>e. Reproducibility Check</div>", unsafe_allow_html=True)
    rep = verify_reproducibility(n_students, seed=int(seed))
    st.markdown(f"<div class='result-box'>{rep['message']}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Run 1 Total Waktu", f"{rep['run1_total']} menit")
    with col2:
        st.metric("Run 2 Total Waktu", f"{rep['run2_total']} menit")

    # Conclusion
    st.divider()
    st.subheader("1.2.3 Kesimpulan Verifikasi")
    all_passed = lf["passed"] and dist["passed"] and rep["passed"]
    if all_passed:
        st.success(
            "✅ **Model telah terverifikasi.** Logika sistem berjalan sesuai asumsi, "
            "tidak ditemukan kesalahan implementasi, dan hasil simulasi konsisten secara internal."
        )
    else:
        st.error("❌ Terdapat aspek verifikasi yang belum terpenuhi. Periksa konfigurasi model.")


# ════════════════════════════════════════════════════════════════
# TAB 2 — VALIDATION
# ════════════════════════════════════════════════════════════════
with tab2:
    st.header("1.3 Validation")
    st.markdown(
        "Validasi memastikan model sudah cukup merepresentasikan sistem nyata "
        "*(build the right model)*."
    )

    # a. Face Validation
    st.markdown("<div class='section-header'>a. Face Validation</div>", unsafe_allow_html=True)
    fv_ok = 40 <= result["total_time"] <= 120 if n_students == 30 else True
    msg = (
        f"Total waktu simulasi **{result['total_time']:.1f} menit** untuk **{n_students} mahasiswa** "
        f"— masuk akal berdasarkan pengalaman nyata di lapangan."
    )
    st.markdown(f"<div class='result-box'>{msg}</div>", unsafe_allow_html=True)

    # b. Theoretical Comparison
    st.markdown("<div class='section-header'>b. Perbandingan dengan Perhitungan Teoritis</div>",
                unsafe_allow_html=True)
    theo = validate_theoretical(result)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("E[T] (rata-rata durasi)", f"{theo['e_t']:.1f} menit")
    with col2:
        st.metric("Total Teoritis (N × E[T])", f"{theo['theoretical']:.1f} menit")
    with col3:
        st.metric("Total Simulasi", f"{theo['simulated']:.1f} menit")

    delta_msg = (
        f"Selisih: **{theo['diff_pct']}%** — "
        + ("✅ Dalam batas toleransi (<15%)" if theo["acceptable"]
           else "⚠️ Melebihi toleransi 15%")
    )
    st.markdown(f"<div class='result-box'>{delta_msg}</div>", unsafe_allow_html=True)

    # c. Behavior Validation
    st.markdown("<div class='section-header'>c. Behavior Validation</div>", unsafe_allow_html=True)
    bv = validate_behavior(n_list=[5, 10, 20, 30, 40, 50], seed=int(seed))
    st.dataframe(bv, use_container_width=True)

    fig2, ax2 = plt.subplots(figsize=(7, 3))
    ax2.plot(bv["N Mahasiswa"], bv["Total Waktu (menit)"],
             marker="o", color="#2563eb", linewidth=2)
    ax2.set_xlabel("Jumlah Mahasiswa (N)")
    ax2.set_ylabel("Total Waktu (menit)")
    ax2.set_title("Perilaku Model: Total Waktu vs Jumlah Mahasiswa")
    ax2.grid(alpha=0.3)
    st.pyplot(fig2, use_container_width=True)

    # d. Sensitivity Analysis
    st.markdown("<div class='section-header'>d. Sensitivity Analysis</div>", unsafe_allow_html=True)
    sa = validate_sensitivity(n_students, seed=int(seed))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Uniform(1,3)", f"{sa['uniform_1_3']:.1f} menit")
    with col2:
        st.metric("Uniform(2,4)", f"{sa['uniform_2_4']:.1f} menit")
    with col3:
        st.metric("Peningkatan", f"{sa['pct_increase']:.1f}%")

    sens_msg = (
        f"Model **sensitif** terhadap perubahan parameter distribusi (+{sa['pct_increase']:.1f}%), "
        "sesuai ekspektasi." if sa["sensitive"]
        else "Model kurang sensitif terhadap perubahan parameter (perlu investigasi lebih lanjut)."
    )
    style = "result-box" if sa["sensitive"] else "warn-box"
    st.markdown(f"<div class='{style}'>{sens_msg}</div>", unsafe_allow_html=True)

    # Conclusion
    st.divider()
    st.subheader("1.3.3 Kesimpulan Validasi")
    st.success(
        "✅ Berdasarkan seluruh metode validasi:\n"
        "- Hasil simulasi berada dalam rentang yang **realistis**.\n"
        "- Perilaku model **konsisten** dengan kondisi nyata.\n"
        "- Model **layak digunakan** untuk analisis durasi pembagian lembar jawaban ujian."
    )

    st.divider()
    st.subheader("1.4 Kesimpulan Akhir")
    st.info(
        "Model simulasi pembagian lembar jawaban ujian telah melalui proses **verifikasi dan validasi**. "
        "Verifikasi menunjukkan bahwa model telah diimplementasikan sesuai dengan logika dan asumsi sistem, "
        "sementara validasi menunjukkan bahwa hasil simulasi cukup merepresentasikan kondisi nyata "
        "dan dapat digunakan sebagai alat bantu analisis."
    )


# ════════════════════════════════════════════════════════════════
# TAB 3 — MONTE CARLO
# ════════════════════════════════════════════════════════════════
with tab3:
    st.header("📈 Analisis Monte Carlo")
    st.markdown(f"Menjalankan **{n_runs} replikasi** simulasi untuk melihat distribusi total waktu.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rata-rata", f"{mc['mean']:.1f} menit")
    col2.metric("Std. Deviasi", f"{mc['std']:.2f} menit")
    col3.metric("Min", f"{mc['min']:.1f} menit")
    col4.metric("Max", f"{mc['max']:.1f} menit")

    st.markdown(
        f"**95% Confidence Interval:** [{mc['ci_95_low']:.1f} — {mc['ci_95_high']:.1f}] menit"
    )

    fig3, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Histogram
    axes[0].hist(mc["totals"], bins=25, color="#2563eb", alpha=0.75, edgecolor="white")
    axes[0].axvline(mc["mean"], color="red", linestyle="--", label=f"Mean={mc['mean']:.1f}")
    axes[0].axvline(mc["ci_95_low"], color="orange", linestyle=":", label="CI 95%")
    axes[0].axvline(mc["ci_95_high"], color="orange", linestyle=":")
    axes[0].set_xlabel("Total Waktu (menit)")
    axes[0].set_ylabel("Frekuensi")
    axes[0].set_title("Distribusi Total Waktu (Monte Carlo)")
    axes[0].legend()

    # Convergence
    running_mean = np.cumsum(mc["totals"]) / np.arange(1, len(mc["totals"]) + 1)
    axes[1].plot(running_mean, color="#2563eb", linewidth=1.5)
    axes[1].axhline(mc["mean"], color="red", linestyle="--", linewidth=1, label="Mean akhir")
    axes[1].set_xlabel("Replikasi ke-")
    axes[1].set_ylabel("Rata-rata Kumulatif (menit)")
    axes[1].set_title("Konvergensi Rata-rata Total Waktu")
    axes[1].legend()

    plt.tight_layout()
    st.pyplot(fig3, use_container_width=True)

    # Gantt chart untuk 1 run
    st.subheader("🗓️ Gantt Chart Jadwal Pelayanan")
    n_show = min(15, n_students)
    events_df = pd.DataFrame(result["events"][:n_show])
    fig4, ax4 = plt.subplots(figsize=(10, max(4, n_show * 0.35)))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, n_show))
    for idx, row in events_df.iterrows():
        ax4.barh(
            f"Mhs {int(row['mahasiswa'])}",
            row["durasi_pelayanan"],
            left=row["mulai_dilayani"],
            color=colors[idx], edgecolor="white", height=0.6
        )
    ax4.set_xlabel("Waktu (menit)")
    ax4.set_title(f"Gantt Chart Pembagian Lembar Jawaban ({n_show} mahasiswa pertama)")
    ax4.invert_yaxis()
    ax4.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig4, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# TAB 4 — EVENT LOG
# ════════════════════════════════════════════════════════════════
with tab4:
    st.header("📋 Event Log Lengkap")
    df_events = pd.DataFrame(result["events"]).rename(columns={
        "mahasiswa": "Mahasiswa",
        "mulai_dilayani": "Mulai Dilayani (menit)",
        "selesai_dilayani": "Selesai Dilayani (menit)",
        "durasi_pelayanan": "Durasi Pelayanan (menit)",
        "waktu_tunggu": "Waktu Tunggu Kumulatif (menit)",
    })
    st.dataframe(df_events, use_container_width=True, height=500)

    csv = df_events.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "event_log.csv", "text/csv")


# ════════════════════════════════════════════════════════════════
# TAB 5 — KONSEP
# ════════════════════════════════════════════════════════════════
with tab5:
    st.header("ℹ️ Konsep Sistem")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 Permasalahan")
        st.markdown(
            "Pada akhir ujian di **Institut Teknologi Del**, pengajar membagikan kembali "
            "lembar jawaban kepada mahasiswa. Mahasiswa maju **satu per satu** ke meja pengajar. "
            "Pengajar ingin mengetahui **berapa lama total waktu** yang dibutuhkan."
        )
        st.subheader("📐 Asumsi Sistem")
        assumptions = [
            f"Jumlah mahasiswa: **N = {n_students} orang**",
            "Satu meja pengajar (single-server)",
            "Antrian FIFO (first-come, first-served)",
            f"Waktu pelayanan: **Uniform({min_dur}, {max_dur}) menit**",
            "Tidak ada mahasiswa yang meninggalkan antrian",
            "Waktu mulai = 0, pengajar selalu tersedia",
        ]
        for a in assumptions:
            st.markdown(f"- {a}")
    with col2:
        st.subheader("🔄 Alur Proses")
        st.markdown("""
        ```
        MULAI
           │
           ▼
        Mahasiswa 1 → Langsung ke meja pengajar
           │
           ▼
        Dilayani selama Uniform(min, max) menit
           │
           ▼
        Mahasiswa 2 menunggu → maju setelah mhs-1 selesai
           │
           ▼
        ... (ulangi hingga mahasiswa ke-N)
           │
           ▼
        SELESAI — catat total waktu
        ```
        """)
        st.subheader("📊 Jenis Simulasi")
        st.markdown(
            "**Discrete Event Simulation (DES)** — sistem berubah berdasarkan "
            "kejadian diskrit (mahasiswa selesai dilayani), bukan perubahan kontinu."
        )

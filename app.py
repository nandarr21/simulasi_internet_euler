"""
Simulator Pertumbuhan Pengguna Internet di Indonesia
Model Pertumbuhan Logistik + Metode Euler (Modul 7 - Dynamic System Simulation)

Jalankan lokal:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ------------------------------------------------------------------
# Konfigurasi halaman
# ------------------------------------------------------------------
st.set_page_config(page_title="Simulator Pengguna Internet Indonesia", layout="wide")

PATH_DATA = "data/internet_indonesia_2000_2024.csv"


# ------------------------------------------------------------------
# Fungsi model (sama dengan notebook)
# ------------------------------------------------------------------
def laju_logistik(P, r, K):
    """Laju perubahan dP/dt = r*P*(1 - P/K)."""
    return r * P * (1 - P / K)


def euler_logistik(P0, r, K, t0, t_akhir, h):
    """Simulasi Metode Euler. Mengembalikan array waktu dan nilai P."""
    n_langkah = int(round((t_akhir - t0) / h))
    t = t0 + h * np.arange(n_langkah + 1)
    P = np.zeros(n_langkah + 1)
    P[0] = P0
    for i in range(n_langkah):
        P[i + 1] = P[i] + h * laju_logistik(P[i], r, K)
    return t, P


def ambil_tahunan(t, P, h):
    """Ambil nilai pada tahun bulat agar bisa dibandingkan dengan data tahunan."""
    lompat = int(round(1 / h))
    return t[::lompat].round().astype(int), P[::lompat]


def evaluasi(asli, simulasi):
    galat = simulasi - asli
    rmse = np.sqrt(np.mean(galat ** 2))
    mae = np.mean(np.abs(galat))
    mape = np.mean(np.abs(galat / asli)) * 100
    return rmse, mae, mape


# ------------------------------------------------------------------
# Data dan kalibrasi (disimpan di cache agar tidak dihitung ulang)
# ------------------------------------------------------------------
@st.cache_data
def muat_data():
    return pd.read_csv(PATH_DATA)


@st.cache_data
def kalibrasi(tahun, data_asli):
    """Grid search r dan K dengan Euler h = 1 (sama dengan notebook bagian 12)."""
    P0 = data_asli[0]
    r_grid = np.arange(0.050, 0.6005, 0.001)
    K_grid = np.arange(np.ceil(data_asli.max()), 100.0001, 0.1)
    R, KK = np.meshgrid(r_grid, K_grid)
    P_grid = np.full(R.shape, P0)
    total = np.zeros(R.shape)
    for i in range(1, len(data_asli)):
        P_grid = P_grid + R * P_grid * (1 - P_grid / KK)
        total += (P_grid - data_asli[i]) ** 2
    rmse = np.sqrt(total / len(data_asli))
    idx = np.unravel_index(np.argmin(rmse), rmse.shape)
    return float(round(R[idx], 3)), float(round(KK[idx], 1))


df = muat_data()
tahun = df["Tahun"].values
data_asli = df["Persen"].values
P0 = float(data_asli[0])
T0, T_DATA = int(tahun[0]), int(tahun[-1])
R_OPT, K_OPT = kalibrasi(tahun, data_asli)

# ------------------------------------------------------------------
# Judul dan deskripsi
# ------------------------------------------------------------------
st.title("Simulator Pertumbuhan Pengguna Internet di Indonesia")
st.markdown(
    f"""
Simulator ini memodelkan **persentase penduduk Indonesia yang menggunakan internet**
dengan **Model Pertumbuhan Logistik** yang diselesaikan memakai **Metode Euler**,
lalu membandingkannya dengan data riil tahun {T0}–{T_DATA}.

**Sumber data:** World Bank – World Development Indicators, indikator
*Individuals using the Internet (% of population)* (`IT.NET.USER.ZS`), sumber asli ITU, lisensi CC BY-4.0.
[Lihat data](https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=ID)
"""
)

# ------------------------------------------------------------------
# Sidebar: parameter simulasi
# ------------------------------------------------------------------
st.sidebar.header("Parameter Simulasi")
st.sidebar.caption(f"Hasil kalibrasi (RMSE terkecil, h = 1): r = {R_OPT}, K = {K_OPT}")

r = st.sidebar.slider("Laju pertumbuhan r (per tahun)", 0.05, 0.60, R_OPT, 0.001, format="%.3f")
K = st.sidebar.slider("Kapasitas maksimum K (%)", 50.0, 100.0, K_OPT, 0.1)
h = st.sidebar.select_slider("Step size h (tahun)", options=[1.0, 0.5, 0.25, 0.1], value=1.0)
t_proyeksi = st.sidebar.slider("Simulasi sampai tahun", T_DATA, 2050, 2040)

st.sidebar.markdown("---")
st.sidebar.markdown(f"Nilai awal **P₀ = {P0:.4f}%** (tahun {T0})")

# ------------------------------------------------------------------
# Tab
# ------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Simulasi vs Data Asli", "Eksperimen What-If", "Penjelasan Model"])

# ===================== TAB 1: SIMULASI =====================
with tab1:
    t_halus, P_halus = euler_logistik(P0, r, K, T0, t_proyeksi, h)
    t_thn, P_thn = ambil_tahunan(t_halus, P_halus, h)

    P_banding = P_thn[: len(data_asli)]
    rmse, mae, mape = evaluasi(data_asli, P_banding)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("RMSE", f"{rmse:.3f} poin %")
    c2.metric("MAE", f"{mae:.3f} poin %")
    c3.metric("MAPE", f"{mape:.2f} %")
    c4.metric(f"Prediksi {t_proyeksi}", f"{P_thn[-1]:.2f} %")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(tahun, data_asli, color="black", zorder=5, label=f"Data asli {T0}–{T_DATA}")
    ax.plot(t_halus, P_halus, color="red", linewidth=2, label=f"Simulasi Euler (r={r:.3f}, K={K:.1f}, h={h})")
    ax.axhline(K, color="gray", linestyle="--", linewidth=1, label="Kapasitas maksimum K")
    if t_proyeksi > T_DATA:
        ax.axvspan(T_DATA, t_proyeksi, color="gray", alpha=0.1, label="Periode proyeksi")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Pengguna internet (% penduduk)")
    ax.set_title("Perbandingan Data Asli dan Simulasi Model Logistik")
    ax.grid(True)
    ax.legend(loc="upper left")
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Geser slider r dan K di sidebar untuk melihat bagaimana parameter mendekatkan atau "
        "menjauhkan garis simulasi dari data asli. Kembalikan ke nilai kalibrasi untuk RMSE terkecil."
    )

    hasil = pd.DataFrame({"Tahun": t_thn, "Simulasi (%)": P_thn})
    hasil = hasil.merge(df.rename(columns={"Persen": "Data asli (%)"}), on="Tahun", how="left")
    hasil["Selisih"] = hasil["Simulasi (%)"] - hasil["Data asli (%)"]
    hasil["Laju dP/dt"] = laju_logistik(hasil["Simulasi (%)"], r, K)

    with st.expander("Lihat tabel hasil simulasi"):
        st.dataframe(hasil.round(3), hide_index=True)
        st.download_button("Unduh CSV", hasil.to_csv(index=False), "hasil_simulasi.csv", "text/csv")

# ===================== TAB 2: WHAT-IF =====================
with tab2:
    st.subheader("Eksperimen What-If")
    st.markdown(
        f"Baseline memakai parameter hasil kalibrasi (**r = {R_OPT}, K = {K_OPT}**). "
        "Atur skenario di bawah untuk melihat dampak perubahan parameter."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        K_sk1 = st.slider("Skenario 1 – Kapasitas maksimum K (%)", 50.0, 100.0, 80.0, 0.5)
    with col_b:
        persen_r = st.slider("Skenario 2 – Perubahan laju r (%)", -80, 100, -50, 5)
    r_sk2 = R_OPT * (1 + persen_r / 100)

    skenario = {
        "Baseline": (R_OPT, K_OPT, "red"),
        f"Skenario 1: K = {K_sk1:.1f}%": (R_OPT, K_sk1, "purple"),
        f"Skenario 2: r {persen_r:+d}%": (r_sk2, K_OPT, "green"),
    }

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.scatter(tahun, data_asli, color="black", zorder=5, label="Data asli")
    ringkasan = []
    for nama, (r_s, K_s, warna) in skenario.items():
        t_s, P_s = euler_logistik(P0, r_s, K_s, T0, t_proyeksi, 1.0)
        ax2.plot(t_s, P_s, color=warna, linewidth=2, label=f"{nama} (r={r_s:.3f}, K={K_s:.1f})")
        laju = laju_logistik(P_s, r_s, K_s)
        capai50 = t_s[P_s >= 50]
        ringkasan.append({
            "Skenario": nama,
            "r": round(r_s, 3),
            "K (%)": round(K_s, 1),
            f"P {T_DATA} (%)": round(P_s[t_s == T_DATA][0], 2),
            f"P {t_proyeksi} (%)": round(P_s[-1], 2),
            "Tahun capai 50%": int(capai50[0]) if len(capai50) else "belum",
            "Laju puncak (poin/thn)": round(laju.max(), 2),
            "RMSE vs data": round(evaluasi(data_asli, P_s[: len(data_asli)])[0], 3),
        })
    if t_proyeksi > T_DATA:
        ax2.axvspan(T_DATA, t_proyeksi, color="gray", alpha=0.1)
    ax2.set_xlabel("Tahun")
    ax2.set_ylabel("Pengguna internet (% penduduk)")
    ax2.set_title("Baseline vs Skenario What-If")
    ax2.grid(True)
    ax2.legend(loc="upper left")
    st.pyplot(fig2)
    plt.close(fig2)

    st.dataframe(pd.DataFrame(ringkasan), hide_index=True)

    st.markdown(
        """
**Cara membaca:**
- Mengubah **K** mengubah *setinggi apa* kurva berhenti (loop penyeimbang). Saat P masih kecil,
  kurvanya hampir sama dengan baseline karena faktor (1 − P/K) masih mendekati 1.
- Mengubah **r** mengubah *secepat apa* kurva naik (loop penguat): kurva bergeser ke kiri atau kanan.
- Proyeksi setelah 2024 adalah **skenario**, bukan ramalan pasti, karena data belum cukup
  untuk memastikan nilai K.
"""
    )

# ===================== TAB 3: MODEL =====================
with tab3:
    st.subheader("Model Pertumbuhan Logistik")
    st.latex(r"\frac{dP}{dt} = r\,P\left(1-\frac{P}{K}\right)")
    st.markdown("**Metode Euler** (iterasi dengan step size h):")
    st.latex(r"P_{n+1} = P_n + h \cdot r\,P_n\left(1-\frac{P_n}{K}\right)")
    st.markdown(
        """
| Simbol | Arti | Satuan |
|---|---|---|
| P | Persentase penduduk pengguna internet (**Stock**) | % |
| rP(1 − P/K) | Pengguna baru per tahun (**Flow**) | % per tahun |
| r | Laju pertumbuhan (adopsi) | per tahun |
| K | Kapasitas maksimum | % |
| h | Step size Euler | tahun |

**Feedback loop:**
- **Loop penguat (R):** makin banyak pengguna → makin banyak pengguna baru → pertumbuhan makin cepat.
- **Loop penyeimbang (B):** makin dekat P ke K → ruang sisa (1 − P/K) mengecil → pertumbuhan melambat.

Perpindahan dominasi dari loop R ke loop B menghasilkan **kurva S**, dengan titik belok saat P ≈ K/2.

**Keterbatasan:** model hanya memakai dua parameter tetap; faktor luar (kebijakan, pandemi,
harga gawai) tidak dimodelkan. Data 2009 sempat turun, kemungkinan karena perubahan metode survei.
"""
    )

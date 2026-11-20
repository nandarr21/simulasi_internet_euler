# Simulator Pertumbuhan Pengguna Internet di Indonesia (Metode Euler)

Tugas Akhir Praktikum **Pemodelan dan Simulasi – Dynamic System Simulation**

- **Nama:** Asep Sunandar
- **NIM:** 301240039
- **Aplikasi online:** [tautan Streamlit setelah deploy]

## Deskripsi

Proyek ini memodelkan persentase penduduk Indonesia yang menggunakan internet (2000–2024) dengan
**Model Pertumbuhan Logistik**, diselesaikan secara numerik memakai **Metode Euler**, lalu
dibandingkan dengan data riil. Proyek juga memuat eksperimen **What-If** untuk melihat dampak
perubahan parameter terhadap sistem.

## Model

$$\frac{dP}{dt} = r\,P\left(1-\frac{P}{K}\right) \qquad P_{n+1} = P_n + h\cdot r\,P_n\left(1-\frac{P_n}{K}\right)$$

| Simbol | Arti |
|---|---|
| P | Persentase penduduk pengguna internet (Stock) |
| r | Laju pertumbuhan / adopsi (per tahun) |
| K | Kapasitas maksimum (%) |
| h | Step size Euler (tahun) |

Hasil kalibrasi (grid search, Euler h = 1): **r = 0,261 per tahun, K = 96,9%, RMSE = 1,726 poin persen**.

## Dataset

World Bank – World Development Indicators, indikator *Individuals using the Internet (% of population)*
(`IT.NET.USER.ZS`), sumber asli International Telecommunication Union (ITU), lisensi CC BY-4.0.
https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=ID

## Struktur Repositori

```
├── TA_Simulasi_Euler_Internet.ipynb   # Notebook: EDA, simulasi Euler, kalibrasi, What-If
├── app.py                             # Aplikasi web Streamlit
├── requirements.txt                   # Daftar library
├── data/
│   ├── API_IT.NET.USER.ZS_DS2_en_csv_v2_62387.csv   # Data mentah World Bank
│   ├── internet_indonesia_2000_2024.csv             # Data bersih (dipakai aplikasi)
│   ├── hasil_simulasi_baseline.csv                  # Output notebook
│   └── hasil_whatif.csv                             # Output notebook
└── README.md
```

## Cara Menjalankan

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt

# Notebook: buka TA_Simulasi_Euler_Internet.ipynb di VSCode/Jupyter, pilih kernel venv, Run All

# Aplikasi web:
streamlit run app.py
```

## Fitur Aplikasi

1. **Simulasi vs Data Asli** – atur r, K, h, dan tahun proyeksi; tampil RMSE/MAE/MAPE, grafik, dan tabel hasil.
2. **Eksperimen What-If** – bandingkan baseline dengan skenario perubahan K dan r dalam satu grafik.
3. **Penjelasan Model** – persamaan, struktur Stock-Flow, feedback loop, dan keterbatasan.

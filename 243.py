import streamlit as st
import pandas as pd
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from pathlib import Path
import itertools
from fuzzy_rules import RULES

st.set_page_config(
    page_title="SPK Saham Fuzzy Mamdani",
    layout="wide"
)

st.sidebar.title("Navigasi SPK")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["Profil Kelompok", "Halaman Data", "Hitung SPK"]
)

BASE_DIR = Path(__file__).parent
csv_path = BASE_DIR / "financial_ratios.csv"

@st.cache_data
def load_data():
    try:
        # Membaca dataset mentah
        df = pd.read_csv(csv_path)

        # Mengambil data tahun 2023
        df_pivot = df.pivot(
            index='symbol',
            columns='ratio',
            values='2023'
        ).reset_index()

        # Memilih kolom yang digunakan
        df_awal = df_pivot[['symbol', 'ROE', 'DER', 'Current Ratio', 'NPM', 'GPM']].dropna()

        # Normalisasi menggunakan Persentil (0 - 100)
        df_bersih = pd.DataFrame()
        df_bersih['Kode Saham'] = df_awal['symbol']
        
        # Benefit Attributes (Makin besar makin bagus)
        df_bersih['Return'] = df_awal['ROE'].rank(pct=True) * 100
        df_bersih['Likuiditas'] = df_awal['Current Ratio'].rank(pct=True) * 100
        df_bersih['Net Margin'] = df_awal['NPM'].rank(pct=True) * 100
        df_bersih['Gross Margin'] = df_awal['GPM'].rank(pct=True) * 100

        # Cost Attribute (Semakin kecil DER semakin bagus, dibalik dengan 1 - pct)
        df_bersih['Kesehatan Utang'] = (1 - df_awal['DER'].rank(pct=True)) * 100

        return df_bersih
    except FileNotFoundError:
        return None

df_saham = load_data()

if df_saham is None:
    st.error(f"File '{csv_path.name}' tidak ditemukan di direktori {BASE_DIR}!")
    st.stop()

if menu == "Profil Kelompok":
    st.title("Profil Kelompok")
    st.write("Sistem Pendukung Keputusan Pemilihan Saham Menggunakan Fuzzy Mamdani")
    
    st.markdown("""
    ### Anggota Kelompok
    1. **Abyaz Affanzaky Shanahan**  
    2. **Fiernaz Ingga Pratama**  
    3. **Dewi Rahmawati**
    """)

elif menu == "Halaman Data":
    st.title("Dataset Fundamental Saham")
    st.write(f"Jumlah data saham aktif: **{len(df_saham)}** perusahaan.")
    st.info("Seluruh data rasio keuangan telah dikonversi ke skala persentil 0 - 100 untuk keseragaman.")
    
    st.dataframe(df_saham, use_container_width=True)

elif menu == "Hitung SPK":
    st.title("SPK Kelayakan Investasi Saham")
    st.write("Analisis kelayakan investasi saham pilihan Anda secara objektif dengan parameter dinamis.")

    # Pilihan Saham
    pilihan_saham = st.multiselect(
        "Pilih Alternatif Saham:",
        options=df_saham['Kode Saham'].tolist(),
        default=["AALI", "ABMM", "ACES", "TLKM"]
    )

    # Parameter Input Dinamis via Slider
    st.markdown("### Pengaturan Parameter Batas Tinggi")
    col1, col2 = st.columns(2)

    with col1:
        param_return = st.slider("Batas Return Tinggi", 40, 70, 50)
        param_utang = st.slider("Batas Kesehatan Utang Tinggi", 40, 70, 50)
        param_likuiditas = st.slider("Batas Likuiditas Tinggi", 40, 70, 50)

    with col2:
        param_net = st.slider("Batas Net Margin Tinggi", 40, 70, 50)
        param_gross = st.slider("Batas Gross Margin Tinggi", 40, 70, 50)
        urutan = st.selectbox("Urutkan Hasil Berdasarkan Skor", ["Tertinggi ke Terendah", "Terendah ke Tertinggi"])

    st.markdown("### Fuzzifikasi")
    st.caption("proses pengubahan nilai tegas yang ada ke dalam fungsi keanggotaan")
   
    x = np.arange(0, 101, 1)

    # Kalkulasi batas sedang untuk tiap parameter (dipakai di plot & di mesin fuzzy)
    b_ret, a_ret = max(0, param_return - 25), min(100, param_return + 25)
    b_utg, a_utg = max(0, param_utang - 25), min(100, param_utang + 25)
    b_lik, a_lik = max(0, param_likuiditas - 25), min(100, param_likuiditas + 25)
    b_net, a_net = max(0, param_net - 25), min(100, param_net + 25)
    b_grs, a_grs = max(0, param_gross - 25), min(100, param_gross + 25)

    # Definisi semua variabel untuk di-plot (5 input + 1 output)
    variabel_plot = [
        {
            "judul": "Return (ROE)",
            "labels": ["Rendah", "Sedang", "Tinggi"],
            "mf": [
                fuzz.trimf(x, [0, 0, param_return]),
                fuzz.trimf(x, [b_ret, param_return, a_ret]),
                fuzz.trimf(x, [param_return, 100, 100]),
            ],
        },
        {
            "judul": "Kesehatan Utang (DER)",
            "labels": ["Rendah", "Sedang", "Tinggi"],
            "mf": [
                fuzz.trimf(x, [0, 0, param_utang]),
                fuzz.trimf(x, [b_utg, param_utang, a_utg]),
                fuzz.trimf(x, [param_utang, 100, 100]),
            ],
        },
        {
            "judul": "Likuiditas (Current Ratio)",
            "labels": ["Rendah", "Sedang", "Tinggi"],
            "mf": [
                fuzz.trimf(x, [0, 0, param_likuiditas]),
                fuzz.trimf(x, [b_lik, param_likuiditas, a_lik]),
                fuzz.trimf(x, [param_likuiditas, 100, 100]),
            ],
        },
        {
            "judul": "Net Margin (NPM)",
            "labels": ["Rendah", "Sedang", "Tinggi"],
            "mf": [
                fuzz.trimf(x, [0, 0, param_net]),
                fuzz.trimf(x, [b_net, param_net, a_net]),
                fuzz.trimf(x, [param_net, 100, 100]),
            ],
        },
        {
            "judul": "Gross Margin (GPM)",
            "labels": ["Rendah", "Sedang", "Tinggi"],
            "mf": [
                fuzz.trimf(x, [0, 0, param_gross]),
                fuzz.trimf(x, [b_grs, param_gross, a_grs]),
                fuzz.trimf(x, [param_gross, 100, 100]),
            ],
        },
        {
            "judul": "Output: Kelayakan Investasi",
            "labels": ["Buruk", "Cukup", "Baik"],
            "mf": [
                fuzz.trimf(x, [0, 0, 40]),
                fuzz.trimf(x, [30, 50, 70]),
                fuzz.trimf(x, [60, 100, 100]),
            ],
        },
    ]

    warna_mf = ["#e74c3c", "#f39c12", "#2ecc71"]

    # Plot grid 3x2 (5 input + 1 output)
    fig_mf, axes_mf = plt.subplots(3, 2, figsize=(14, 11))
    axes_mf = axes_mf.flatten()

    for i, var in enumerate(variabel_plot):
        ax = axes_mf[i]
        for mf_val, label, warna in zip(var["mf"], var["labels"], warna_mf):
            ax.plot(x, mf_val, label=label, color=warna, linewidth=2)
            ax.fill_between(x, mf_val, alpha=0.08, color=warna)
        ax.set_title(var["judul"], fontsize=10, fontweight='bold')
        ax.set_xlabel("Nilai Persentil (0–100)")
        ax.set_ylabel("Derajat Keanggotaan")
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    fig_mf.suptitle("Fungsi Keanggotaan Fuzzy Mamdani — Semua Variabel", fontsize=13, fontweight='bold', y=1.01)
    fig_mf.tight_layout()
    st.pyplot(fig_mf)
    plt.close(fig_mf)

    @st.cache_resource(show_spinner="Membangun Matriks 243 Aturan...")
    def bangun_mesin_fuzzy(p_ret, p_utg, p_lik, p_net, p_grs):
        b_ret, a_ret = max(0, p_ret - 25), min(100, p_ret + 25)
        b_utg, a_utg = max(0, p_utg - 25), min(100, p_utg + 25)
        b_lik, a_lik = max(0, p_lik - 25), min(100, p_lik + 25)
        b_net, a_net = max(0, p_net - 25), min(100, p_net + 25)
        b_grs, a_grs = max(0, p_grs - 25), min(100, p_grs + 25)

        ret = ctrl.Antecedent(np.arange(0, 101, 1), 'return')
        utg = ctrl.Antecedent(np.arange(0, 101, 1), 'kesehatan_utang')
        lik = ctrl.Antecedent(np.arange(0, 101, 1), 'likuiditas')
        nm  = ctrl.Antecedent(np.arange(0, 101, 1), 'net_margin')
        gm  = ctrl.Antecedent(np.arange(0, 101, 1), 'gross_margin')
        kly = ctrl.Consequent(np.arange(0, 101, 1), 'kelayakan')

        ret['rendah'] = fuzz.trimf(ret.universe, [0, 0, p_ret])
        ret['sedang'] = fuzz.trimf(ret.universe, [b_ret, p_ret, a_ret])
        ret['tinggi'] = fuzz.trimf(ret.universe, [p_ret, 100, 100])

        utg['rendah'] = fuzz.trimf(utg.universe, [0, 0, p_utg])
        utg['sedang'] = fuzz.trimf(utg.universe, [b_utg, p_utg, a_utg])
        utg['tinggi'] = fuzz.trimf(utg.universe, [p_utg, 100, 100])

        lik['rendah'] = fuzz.trimf(lik.universe, [0, 0, p_lik])
        lik['sedang'] = fuzz.trimf(lik.universe, [b_lik, p_lik, a_lik])
        lik['tinggi'] = fuzz.trimf(lik.universe, [p_lik, 100, 100])

        nm['rendah'] = fuzz.trimf(nm.universe, [0, 0, p_net])
        nm['sedang'] = fuzz.trimf(nm.universe, [b_net, p_net, a_net])
        nm['tinggi'] = fuzz.trimf(nm.universe, [p_net, 100, 100])

        gm['rendah'] = fuzz.trimf(gm.universe, [0, 0, p_grs])
        gm['sedang'] = fuzz.trimf(gm.universe, [b_grs, p_grs, a_grs])
        gm['tinggi'] = fuzz.trimf(gm.universe, [p_grs, 100, 100])

        kly['buruk'] = fuzz.trimf(kly.universe, [0, 0, 40])
        kly['cukup'] = fuzz.trimf(kly.universe, [30, 50, 70])
        kly['baik']  = fuzz.trimf(kly.universe, [60, 100, 100])

        rules_list = []

        for kondisi, keputusan_txt in RULES.items():
            r, u, l, n, g = kondisi
            if keputusan_txt == 'baik':
                keputusan = kly['baik']
            elif keputusan_txt == 'cukup':
                keputusan = kly['cukup']
            else:
                keputusan = kly['buruk']

            rules_list.append(
                ctrl.Rule(
                    ret[r] & utg[u] & lik[l] & nm[n] & gm[g],
                    keputusan
                )
            )

        return ctrl.ControlSystem(rules_list), kly, ret, utg, lik, nm, gm

    # Panggil Fungsi Cache
    sistem_ctrl, kelayakan_obj, var_ret, var_utg, var_lik, var_nm, var_gm = bangun_mesin_fuzzy(
        param_return, param_utang, param_likuiditas, param_net, param_gross
    )

    if st.button("Proses Perhitungan SPK", type="primary"):

        df_evaluasi = df_saham[df_saham['Kode Saham'].isin(pilihan_saham)]

        if len(df_evaluasi) == 0:
            st.warning("Silakan pilih minimal 1 alternatif saham terlebih dahulu.")
        else:
            hasil_akhir    = []
            data_defuzz    = []   # Tabel defuzzifikasi
            data_firing    = []   # Tabel rule firing
            input_berhasil = None
            kode_terakhir  = ""

            progress_bar = st.progress(0)
            status_teks  = st.empty()
            total_saham  = len(df_evaluasi)

            for index, (i, row) in enumerate(df_evaluasi.iterrows()):
                persentase = int(((index + 1) / total_saham) * 100)
                progress_bar.progress(persentase)
                status_teks.text(f"Menganalisis saham {row['Kode Saham']}... ({index+1}/{total_saham})")

                simulasi = ctrl.ControlSystemSimulation(sistem_ctrl)
                simulasi.input['return']          = row['Return']
                simulasi.input['kesehatan_utang'] = row['Kesehatan Utang']
                simulasi.input['likuiditas']       = row['Likuiditas']
                simulasi.input['net_margin']       = row['Net Margin']
                simulasi.input['gross_margin']     = row['Gross Margin']

                try:
                    simulasi.compute()
                    skor = simulasi.output['kelayakan']
                    input_berhasil = {
                        'return':          row['Return'],
                        'kesehatan_utang': row['Kesehatan Utang'],
                        'likuiditas':      row['Likuiditas'],
                        'net_margin':      row['Net Margin'],
                        'gross_margin':    row['Gross Margin']
                    }
                    kode_terakhir = row['Kode Saham']
                except ValueError:
                    skor = 35.0

                if skor < 40:   status = "Kurang Layak"
                elif skor < 70: status = "Cukup Layak"
                else:           status = "Layak Investasi"

                hasil_akhir.append({
                    "Kode Saham":     row['Kode Saham'],
                    "Skor Kelayakan": round(skor, 2),
                    "Rekomendasi":    status
                })

                # Hitung derajat keanggotaan untuk tabel defuzzifikasi
                ret_v = row['Return']
                utg_v = row['Kesehatan Utang']
                net_v = row['Net Margin']
                lik_v  = row['Likuiditas']
                grs_v  = row['Gross Margin']
                def mu(universe, mf_params, nilai):
                    return round(float(fuzz.interp_membership(universe, fuzz.trimf(universe, mf_params), nilai)), 3)

                u = np.arange(0, 101, 1)
                data_defuzz.append({
                    "Kode Saham"          : row['Kode Saham'],
                    "Return (nilai)"      : round(ret_v, 2),
                    "μ Return Rendah"     : mu(u, [0, 0, param_return],              ret_v),
                    "μ Return Sedang"     : mu(u, [b_ret, param_return, a_ret],       ret_v),
                    "μ Return Tinggi"     : mu(u, [param_return, 100, 100],           ret_v),
                    "Kes. Utang (nilai)"  : round(utg_v, 2),
                    "μ Utang Rendah"      : mu(u, [0, 0, param_utang],               utg_v),
                    "μ Utang Sedang"      : mu(u, [b_utg, param_utang, a_utg],        utg_v),
                    "μ Utang Tinggi"      : mu(u, [param_utang, 100, 100],            utg_v),
                    "Net Margin (nilai)"  : round(net_v, 2),
                    "μ Net Rendah"        : mu(u, [0, 0, param_net],                 net_v),
                    "μ Net Sedang"        : mu(u, [b_net, param_net, a_net],          net_v),
                    "μ Net Tinggi"        : mu(u, [param_net, 100, 100],              net_v),
                    "Likuiditas (nilai)"   : round(lik_v, 2),
                    "μ Lik Rendah"         : mu(u, [0, 0, param_likuiditas],            lik_v),
                    "μ Lik Sedang"         : mu(u, [b_lik, param_likuiditas, a_lik],    lik_v),
                    "μ Lik Tinggi"         : mu(u, [param_likuiditas, 100, 100],        lik_v),
                    "Gross Margin (nilai)" : round(grs_v, 2),
                    "μ GM Rendah"          : mu(u, [0, 0, param_gross],                 grs_v),
                    "μ GM Sedang"          : mu(u, [b_grs, param_gross, a_grs],         grs_v),
                    "μ GM Tinggi"          : mu(u, [param_gross, 100, 100],             grs_v),
                    "Skor Output"         : round(skor, 2),
                })
                # tampilkan hanya rule yang AKTIF (α > 0) per saham.
                mu_all = {
                    ('return',          'rendah'): mu(u, [0, 0, param_return],              row['Return']),
                    ('return',          'sedang'): mu(u, [b_ret, param_return, a_ret],       row['Return']),
                    ('return',          'tinggi'): mu(u, [param_return, 100, 100],           row['Return']),
                    ('kesehatan_utang', 'rendah'): mu(u, [0, 0, param_utang],               row['Kesehatan Utang']),
                    ('kesehatan_utang', 'sedang'): mu(u, [b_utg, param_utang, a_utg],        row['Kesehatan Utang']),
                    ('kesehatan_utang', 'tinggi'): mu(u, [param_utang, 100, 100],            row['Kesehatan Utang']),
                    ('likuiditas',      'rendah'): mu(u, [0, 0, param_likuiditas],           row['Likuiditas']),
                    ('likuiditas',      'sedang'): mu(u, [b_lik, param_likuiditas, a_lik],   row['Likuiditas']),
                    ('likuiditas',      'tinggi'): mu(u, [param_likuiditas, 100, 100],        row['Likuiditas']),
                    ('net_margin',      'rendah'): mu(u, [0, 0, param_net],                  row['Net Margin']),
                    ('net_margin',      'sedang'): mu(u, [b_net, param_net, a_net],           row['Net Margin']),
                    ('net_margin',      'tinggi'): mu(u, [param_net, 100, 100],               row['Net Margin']),
                    ('gross_margin',    'rendah'): mu(u, [0, 0, param_gross],                row['Gross Margin']),
                    ('gross_margin',    'sedang'): mu(u, [b_grs, param_gross, a_grs],         row['Gross Margin']),
                    ('gross_margin',    'tinggi'): mu(u, [param_gross, 100, 100],             row['Gross Margin']),
                }

                for kondisi, konsekuen in RULES.items():
                    r, utg_h, l, n, g = kondisi
                    alpha = min(
                        mu_all[('return', r)],
                        mu_all[('kesehatan_utang', utg_h)],
                        mu_all[('likuiditas', l)],
                        mu_all[('net_margin', n)],
                        mu_all[('gross_margin', g)],
                    )
                    if alpha > 0:
                        data_firing.append({
                            "Kode Saham": row['Kode Saham'],
                            "Rule": f"Ret={r.upper()} ∧ Utg={utg_h.upper()} ∧ Lik={l.upper()} ∧ Net={n.upper()} ∧ Grs={g.upper()}",
                            "α-cut (Firing Strength)": round(alpha, 4),
                            "Konsekuen": konsekuen.upper(),
                        })

            status_teks.empty()

            # TABEL DERAJAT KEANGGOTAAN (DEFUZZIFIKASI)
            st.markdown("---")
            st.subheader("Tabel Derajat Keanggotaan & Defuzzifikasi")
            st.caption("Nilai input persentil tiap saham beserta derajat keanggotaan (μ) pada masing-masing himpunan fuzzy, serta skor output hasil defuzzifikasi (metode Centroid).")
            st.dataframe(pd.DataFrame(data_defuzz), use_container_width=True)

            # ── Tabel Rangking ──
            df_hasil = pd.DataFrame(hasil_akhir)
            ascending = True if urutan == "Terendah ke Tertinggi" else False
            df_hasil = df_hasil.sort_values(by="Skor Kelayakan", ascending=ascending).reset_index(drop=True)
            df_hasil.index = np.arange(1, len(df_hasil) + 1)

            kode_rank1 = df_hasil.iloc[0]["Kode Saham"]
            row_rank1  = df_saham[df_saham['Kode Saham'] == kode_rank1].iloc[0]
            input_rank1 = {
                'return':          row_rank1['Return'],
                'kesehatan_utang': row_rank1['Kesehatan Utang'],
                'likuiditas':      row_rank1['Likuiditas'],
                'net_margin':      row_rank1['Net Margin'],
                'gross_margin':    row_rank1['Gross Margin'],
            }

            st.markdown("---")
            st.subheader("🏆 Hasil Perankingan Saham")
            st.dataframe(df_hasil, use_container_width=True)

            # ── Bar Chart ──
            st.subheader("Grafik Skor Kelayakan")
            st.bar_chart(data=df_hasil, x="Kode Saham", y="Skor Kelayakan")

            # VISUALISASI DEFUZZIFIKASI
            if input_rank1 is not None:
                st.markdown("---")
                st.subheader(f"Visualisasi Defuzzifikasi — Saham Peringkat #1: {kode_rank1}")
                st.caption("Area biru = hasil agregasi rule aktif. Garis merah = nilai crisp hasil defuzzifikasi (metode Centroid).")

                # Rebuild simulasi bersih untuk saham peringkat #1
                sim_visual = ctrl.ControlSystemSimulation(sistem_ctrl)
                for key, val in input_rank1.items():
                    sim_visual.input[key] = val
                sim_visual.compute()
                skor_visual = sim_visual.output['kelayakan']

                # Hitung agregasi manual untuk plot eksplisit
                x_out     = np.arange(0, 101, 1)
                mf_buruk  = fuzz.trimf(x_out, [0, 0, 40])
                mf_cukup  = fuzz.trimf(x_out, [30, 50, 70])
                mf_baik   = fuzz.trimf(x_out, [60, 100, 100])

                # Ambil firing strength dari data_firing saham peringkat #1
                firing_last = [r for r in data_firing if r["Kode Saham"] == kode_rank1]
                alpha_buruk = max([r["α-cut (Firing Strength)"] for r in firing_last if r["Konsekuen"] == "BURUK"] or [0])
                alpha_cukup = max([r["α-cut (Firing Strength)"] for r in firing_last if r["Konsekuen"] == "CUKUP"] or [0])
                alpha_baik  = max([r["α-cut (Firing Strength)"] for r in firing_last if r["Konsekuen"] == "BAIK"]  or [0])

                clipped_buruk = np.fmin(alpha_buruk, mf_buruk)
                clipped_cukup = np.fmin(alpha_cukup, mf_cukup)
                clipped_baik  = np.fmin(alpha_baik,  mf_baik)
                agregasi      = np.fmax(clipped_buruk, np.fmax(clipped_cukup, clipped_baik))

                fig_defuzz, ax_defuzz = plt.subplots(figsize=(10, 4))

                ax_defuzz.fill_between(x_out, mf_buruk, alpha=0.08, color="#e74c3c")
                ax_defuzz.fill_between(x_out, mf_cukup, alpha=0.08, color="#f39c12")
                ax_defuzz.fill_between(x_out, mf_baik,  alpha=0.08, color="#2ecc71")

                ax_defuzz.plot(x_out, mf_buruk, label="Buruk", color="#e74c3c", linewidth=1.5, linestyle='--')
                ax_defuzz.plot(x_out, mf_cukup, label="Cukup", color="#f39c12", linewidth=1.5, linestyle='--')
                ax_defuzz.plot(x_out, mf_baik,  label="Baik",  color="#2ecc71", linewidth=1.5, linestyle='--')

                ax_defuzz.fill_between(x_out, agregasi, alpha=0.45, color="#3498db", label="Area Agregasi")
                ax_defuzz.plot(x_out, agregasi, color="#2980b9", linewidth=2)

                ax_defuzz.axvline(
                    x=skor_visual, color="red", linewidth=2.5, linestyle="-",
                    label=f"Defuzzifikasi (Centroid) = {skor_visual:.2f}"
                )

                ax_defuzz.set_title(f"Hasil Defuzzifikasi Mamdani — {kode_rank1} (Peringkat #1)", fontsize=12, fontweight='bold')
                ax_defuzz.set_xlabel("Skor Kelayakan (0–100)")
                ax_defuzz.set_ylabel("Derajat Keanggotaan")
                ax_defuzz.legend(loc="upper left", fontsize=9)
                ax_defuzz.grid(True, alpha=0.3)
                ax_defuzz.set_xlim([0, 100])
                ax_defuzz.set_ylim([0, 1.1])

                st.pyplot(fig_defuzz)
                plt.close(fig_defuzz)

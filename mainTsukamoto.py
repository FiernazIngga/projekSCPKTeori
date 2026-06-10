import streamlit as st
import numpy as np
import pandas as pd
import skfuzzy as fuzz
import matplotlib.pyplot as plt

st.set_page_config(page_title="SPK Saham Tsukamoto", layout="wide")

# =========================
# DATA SAHAM
# =========================
df = pd.DataFrame({
    "Kode": ["BBCA", "TLKM", "UNVR", "BBRI"],
    "Return": [80, 70, 60, 85],
    "Volatilitas": [30, 50, 40, 60],
    "Growth": [75, 65, 55, 80],
    "Debt": [30, 60, 50, 40],
    "Dividen": [70, 60, 50, 75],
})

features = ["Return", "Volatilitas", "Growth", "Debt", "Dividen"]

# =========================
# UNIVERSAL SET
# =========================
x = np.arange(0, 101, 1)

# =========================
# MEMBERSHIP FUNCTION
# =========================
mf = {
    "Return": {
        "rendah": fuzz.trapmf(x, [0, 0, 40, 70]),
        "tinggi": fuzz.trapmf(x, [40, 70, 100, 100])
    },
    "Volatilitas": {
        "rendah": fuzz.trapmf(x, [0, 0, 30, 60]),
        "tinggi": fuzz.trapmf(x, [30, 60, 100, 100])
    },
    "Growth": {
        "rendah": fuzz.trapmf(x, [0, 0, 40, 70]),
        "tinggi": fuzz.trapmf(x, [40, 70, 100, 100])
    },
    "Debt": {
        "rendah": fuzz.trapmf(x, [0, 0, 30, 60]),
        "tinggi": fuzz.trapmf(x, [30, 60, 100, 100])
    },
    "Dividen": {
        "rendah": fuzz.trapmf(x, [0, 0, 40, 70]),
        "tinggi": fuzz.trapmf(x, [40, 70, 100, 100])
    }
}

# =========================
# RULE 32 FULL (TIDAK DIUBAH)
# =========================
rules = [
("buruk", ["rendah","rendah","rendah","rendah","rendah"]),
("buruk", ["rendah","rendah","rendah","rendah","tinggi"]),
("buruk", ["rendah","rendah","rendah","tinggi","rendah"]),
("buruk", ["rendah","tinggi","rendah","rendah","rendah"]),
("buruk", ["rendah","tinggi","rendah","tinggi","rendah"]),
("buruk", ["rendah","rendah","rendah","tinggi","tinggi"]),
("buruk", ["rendah","tinggi","tinggi","rendah","rendah"]),
("buruk", ["rendah","tinggi","rendah","tinggi","tinggi"]),

("cukup", ["tinggi","tinggi","rendah","rendah","rendah"]),
("cukup", ["rendah","tinggi","tinggi","rendah","rendah"]),
("cukup", ["rendah","rendah","tinggi","tinggi","rendah"]),
("cukup", ["rendah","rendah","rendah","tinggi","tinggi"]),
("cukup", ["tinggi","rendah","rendah","tinggi","rendah"]),
("cukup", ["rendah","tinggi","rendah","rendah","tinggi"]),
("cukup", ["tinggi","tinggi","rendah","rendah","tinggi"]),
("cukup", ["tinggi","rendah","tinggi","tinggi","rendah"]),
("cukup", ["rendah","tinggi","tinggi","rendah","tinggi"]),
("cukup", ["tinggi","tinggi","tinggi","rendah","rendah"]),
("cukup", ["rendah","rendah","tinggi","tinggi","tinggi"]),
("cukup", ["tinggi","rendah","rendah","tinggi","tinggi"]),
("cukup", ["rendah","tinggi","tinggi","tinggi","rendah"]),
("cukup", ["tinggi","tinggi","tinggi","rendah","tinggi"]),

("baik", ["tinggi","rendah","tinggi","rendah","tinggi"]),
("baik", ["tinggi","rendah","tinggi","tinggi","tinggi"]),
("baik", ["tinggi","tinggi","tinggi","tinggi","rendah"]),
("baik", ["tinggi","rendah","tinggi","tinggi","rendah"]),
("baik", ["tinggi","tinggi","tinggi","rendah","tinggi"]),
("baik", ["tinggi","tinggi","tinggi","tinggi","tinggi"]),
("baik", ["tinggi","rendah","tinggi","rendah","rendah"]),
("baik", ["tinggi","tinggi","rendah","tinggi","tinggi"]),
]

# =========================
# OUTPUT TSUKAMOTO
# =========================
def z_buruk(a): return 40 - a * 40
def z_cukup(a): return 40 + a * 30
def z_baik(a):  return 70 + a * 30

def z(label, a):
    if label == "buruk":
        return z_buruk(a)
    elif label == "cukup":
        return z_cukup(a)
    else:
        return z_baik(a)

# =========================
# FUZZY VALUE
# =========================
def mu(val, feature, level):
    return fuzz.interp_membership(x, mf[feature][level], val)

# =========================
# INFERENSI TSUKAMOTO
# =========================
def infer(row):

    total_num = 0
    total_den = 0
    debug = []

    for label, rule in rules:

        mus = []

        for i, f in enumerate(features):
            level = rule[i]
            mus.append(mu(row[f], f, level))

        alpha = min(mus)

        debug.append([label, round(alpha, 3)])

        if alpha == 0:
            continue

        z_val = z(label, alpha)

        total_num += alpha * z_val
        total_den += alpha

    return (total_num / total_den if total_den != 0 else 0), debug

# =========================
# UI
# =========================
st.title("📊 SPK Saham Tsukamoto (RULE 32 FULL)")

st.dataframe(df, use_container_width=True)

# =========================
# MEMBERSHIP GRAPH (COMPACT)
# =========================
st.subheader("📈 Membership Function")

cols = st.columns(3)

for i, f in enumerate(features[:3]):
    with cols[i]:
        st.markdown(f"**{f}**")
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.plot(x, mf[f]["rendah"], label="Rendah")
        ax.plot(x, mf[f]["tinggi"], label="Tinggi")
        ax.legend(fontsize=7)
        ax.tick_params(labelsize=7)
        st.pyplot(fig)

cols2 = st.columns(2)

for i, f in enumerate(features[3:]):
    with cols2[i]:
        st.markdown(f"**{f}**")
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.plot(x, mf[f]["rendah"])
        ax.plot(x, mf[f]["tinggi"])
        st.pyplot(fig)

# =========================
# HITUNG
# =========================
st.divider()

if st.button("🔥 Hitung Ranking"):

    hasil = []
    debug_all = {}

    for _, row in df.iterrows():
        skor, debug = infer(row)
        hasil.append([row["Kode"], skor])
        debug_all[row["Kode"]] = debug

    hasil_df = pd.DataFrame(hasil, columns=["Saham", "Skor"])
    hasil_df = hasil_df.sort_values("Skor", ascending=False).reset_index(drop=True)

    st.subheader("🏆 Ranking Saham")
    st.dataframe(hasil_df, use_container_width=True)

    st.bar_chart(hasil_df.set_index("Saham"))

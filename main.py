import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

permintaan = np.arange(0, 6000, 1)
persediaan = np.arange(0, 700, 1)
produksi = np.arange(0, 9000, 1)

permintaan_sd = fuzz.trapmf(permintaan, [0, 0, 1000, 5000])
permintaan_by = fuzz.trapmf(permintaan, [1000, 5000, 6000, 6000])

persediaan_sd = fuzz.trapmf(persediaan, [0, 0, 100, 600])
persediaan_by = fuzz.trapmf(persediaan, [100, 600, 700, 700])

produksi_kr = fuzz.trapmf(produksi, [0, 0, 2000, 7000])
produksi_tb = fuzz.trapmf(produksi, [2000, 7000, 9000, 9000])

fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))

ax0.plot(permintaan, permintaan_sd, 'b', label='sedikit')
ax0.plot(permintaan, permintaan_by, 'g', label='banyak')
ax0.set_title("Permintaan")
ax0.legend()

ax1.set_title("Persediaan")
ax1.plot(persediaan, persediaan_sd, 'b', label='sedikit')
ax1.plot(persediaan, persediaan_by, 'g', label='banyak')
ax1.set_title("Persediaan")
ax1.legend()

ax2.plot(produksi, produksi_kr, 'b', label='berkurang')
ax2.plot(produksi, produksi_tb, 'g', label='bertambah')
ax2.set_title("Produksi")
ax2.legend()

for ax in (ax0, ax1, ax2):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

plt.tight_layout()
plt.show()


# Menentukan input
minta = 4000
sedia = 300

# Menetukan rule base


# Menentukan derajat keanggotaan
x=[]
x.append(fuzz.interp_membership(permintaan, permintaan_sd, minta))
x.append(fuzz.interp_membership(permintaan, permintaan_by, minta))

y=[]
y.append(fuzz.interp_membership(persediaan, persediaan_sd, sedia))
y.append(fuzz.interp_membership(persediaan, persediaan_by, sedia))

print("Derajat keanggotaan permintaan")
if x[0] > 0:
    print("Sedikit: " + str(x[0]))
if x[1] > 0:
    print("Sedikit: " + str(x[1]))

print("Derajat keanggotaan persediaan")
if y[0] > 0:
    print("Sedikit: " + str(y[0]))
if y[1] > 0:
    print("Sedikit: " + str(y[1]))

# Memodelkan rule base dan nferensi tsukamoto

apred1 = np.fmin(x[1], y[1])
print("Bertambah, nilai apred1 = ", apred1)
z1 = (apred1 * 5000) + 2000
print("Nilai z1 = ", z1)

apred2 = np.fmin(x[0], y[0])
print("Berkurang, Nilai apred2 = ", apred2)
z2 = 7000 - (apred2 * 5000)
print("Nilai z2 = ", z2)

apred3 = np.fmin(x[0], y[1])
print("Berkurang, Nilai apred3 = ", apred3)
z3 = 7000 - (apred3 * 5000)
print("Nilai z3 = ", z3)

apred4 = np.fmin(x[1], y[0])
print("Bertambah, Nilai apred4 = ", apred4)
z4 = (apred4 * 5000) + 2000
print("Nilai z4 = ", z4)

# Defuzzifikasi
z = (apred1*z1+apred2*z2+apred3*z3+apred4*z4) / (apred1+apred2+apred3+apred4)

print("Jumlah Produksi PT ABC = ", z)
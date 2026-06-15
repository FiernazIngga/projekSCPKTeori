# projekSCPKTeori

Repositori ini berisi implementasi Sistem Pendukung Keputusan (SPK) menggunakan logika fuzzy untuk analisis rasio keuangan.

## 📋 Prasyarat & Kelengkapan File

Sebelum menjalankan program, pastikan file-file berikut berada di dalam **satu folder yang sama**:
* `243.py` — Script utama program.
* `fuzzy_rules.py` — Script berisi aturan logika fuzzy.
* `financial_ratios.csv` — Dataset rasio keuangan yang akan diproses.

---

## 🚀 Cara Menjalankan Proyek

Ikuti langkah-langkah di bawah ini secara berurutan melalui Terminal atau Command Prompt:

### 1. Aktifkan Virtual Environment (Opsional)
Jika Anda menggunakan *virtual environment* (venv), aktifkan terlebih dahulu:
* **Windows:** `venv\Scripts\activate`
* **Mac/Linux:** `source venv/bin/activate`

### 2. Instal Dependensi
Instal semua pustaka (*library*) Python yang diperlukan menggunakan perintah berikut:
```bash
pip install -r requirements.txt
```

### 3. Jalankan Program
Setelah instalasi selesai dan semua file dipastikan berada di folder yang sama, jalankan perintah ini:
```bash
python 243.py
```

---

## 🛠️ Penyelesaian Masalah (Troubleshooting)

* **Error `FileNotFoundError`:** Pastikan Anda sudah berada di direktori yang benar sebelum menjalankan perintah `python 243.py`. Gunakan perintah `cd nama_folder` untuk berpindah ke folder proyek.
* **Error `ModuleNotFoundError`:** Pastikan Anda tidak melupakan huruf `-r` saat melakukan instalasi (`pip install -r requirements.txt`).

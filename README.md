# Web Perubahan Tutupan Lahan & Analisis Kesesuaian Lahan Distrik Agats, Kabupaten Asmat, Papua Selatan

## Spefikasi Sistem
- Python: Bahasa Pemrograman Utama
- Google Earth Engine: Sumber Data & Map Interaktif

Aplikasi web sederhana untuk menampilkan hasil analisis.
Fitur-fitur utama pada aplikasi:
- Peta Tutupan Lahan Tahun 2025 beserta statistik
- Grafik Perubahan Tutupan Lahan Tahun 2020-2025
- Grafik & Peta Perbandingan 2 Tahun Perubahan Tutupan Lahan
- Analisis Kesesuaian Lahan per Komoditas (Kopi Liberika, Alpukat, Durian, Jambu Mete, Kakao, Kelapa, dan Jeruk)

## Cara Menjalankan Aplikasi

# Install Dependency
1. Pengguna harus menginstall semua library yang dibutuhkan.
```bash
pip install -r requirements.txt
```

# Autentikasi Earth Engine
2. Pengguna harus memiliki akun Google Earth Engine dengan mendaftarkan menggunakan akun Google atau membuat akun baru pada link ```https://code.earthengine.google.com```. Kemudian jalankan perintah berikut di terminal.
```bash
earthengine authenticate
```

# Jalankan Aplikasi
3. Aplikasi dijalankan menggunakan perintah berikut. Aplikasi dapat diakses pada web browser pada halaman ```http://localhost:8501/```
```bash
streamlit run app.py
```
### Credits:
Tugas Akhir 
Junita Hariyati
Informatika - Data Science
Universitas Katolik Parahyangan
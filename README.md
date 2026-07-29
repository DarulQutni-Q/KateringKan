# Sistem Produksi Katering dan Manajemen Alergen (KateringKU)

Aplikasi katering berbasis desktop dengan antarmuka yang bersih (minimalis dark-mode) untuk mengelola menu, pesanan, bahan, dan validasi alergen. Dikembangkan dengan Python dan CustomTkinter.

## Kebutuhan Sistem
- Python 3.11 atau lebih baru.
- Sistem operasi: Windows / macOS / Linux.

## Cara Instalasi
1. Pastikan Python sudah terinstall.
2. Buka terminal/CMD, masuk ke folder proyek `JokiDewa/`.
3. Jalankan perintah instalasi dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Cara Menjalankan Aplikasi
Dari dalam folder `JokiDewa/`, ketik:
```bash
python main.py
```
Aplikasi akan secara otomatis membaca (atau membuatkan data dummy) ke dalam folder `data/` pada saat pertama kali dijalankan.

## Data Contoh (Dummy)
Ketika program pertama kali dijalankan, sistem akan men-generate data berikut jika file JSON di folder `data/` belum ada:
* **Pelanggan:** 
  * P001: Budi Santoso (Aman)
  * P002: Siti Aminah (Alergi B003 / Kacang Tanah)
  * P003: Andi Celiac (Alergi B006 / Tepung Terigu)
* **Bahan:** Tersedia stok awal beras, daging, sayur, kacang, telor, dll.
* **Menu:** Menu Reguler, Vegetarian, dan Bebas Gluten.

## Fitur Utama
1. **Manajemen Bahan & Menu**: Data tersimpan di JSON.
2. **Dekorator Opsi Menu**: Tambah lauk atau kemasan premium tanpa ngubah struktur menu dasar.
3. **Validasi Alergi**: Otomatis nge-blok pesanan kalau menu ngandung bahan alergen si pelanggan.
4. **Validasi Stok**: Mencegah order kalau stok bahan di gudang ga cukup.
5. **Ekspor CSV**: Generate laporan pesanan ke dalam bentuk `.csv`.

## Pengujian (Unit Tests)
Ada 8 unit test yang jalanin skenario normal dan *error handling*. Buat ngetes:
```bash
python -m unittest tests/test_katering.py
```
Atau jika pakai pytest:
```bash
pytest tests/
```

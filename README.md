# Music Player Web Application

<div align="center">
  <h3>Pemutar Musik Berbasis Web Modern</h3>
  <p>Streaming, pengelolaan, dan menikmati koleksi musik Anda melalui antarmuka yang intuitif</p>
</div>

---

## Tentang Proyek

Music Player adalah aplikasi web lengkap yang memungkinkan pengguna untuk mengelola dan memutar koleksi musik pribadi melalui antarmuka yang bersih dan modern. Dibangun menggunakan Flask dan JavaScript murni (vanilla JavaScript), aplikasi ini memberikan pengalaman yang mulus baik bagi administrator yang mengelola pustaka musik maupun pengguna yang menikmati lagu favorit mereka.

Aplikasi ini mendukung unggahan file audio dan gambar sampul secara langsung, sehingga tidak memerlukan URL eksternal. Pengguna dapat membuat playlist kustom, mengelola antrean pemutaran, menandai lagu favorit, serta mengontrol pemutaran melalui pemutar musik yang intuitif.

---

## Fitur Utama

### Untuk User

* **Pemutaran Audio**: Pemutar audio berbasis HTML5 dengan kontrol play/pause
* **Manajemen Playlist**: Membuat, melihat, dan menghapus playlist kustom
* **Sistem Antrean (Queue)**: Menambahkan lagu ke antrean dan mengatur urutan pemutaran
* **Favorit**: Menandai dan mengakses lagu favorit dengan cepat
* **Pencarian Lagu**: Menjelajahi seluruh koleksi musik berdasarkan kategori
* **Sistem History**: Melihat riwayat lagu yang telah diputar

### Untuk Admin

* **Unggah File**: Unggah langsung file audio (MP3, WAV, OGG, FLAC, M4A)
* **Unggah Sampul Album**: Unggah gambar sampul (JPG, PNG, GIF, WebP)
* **Manajemen Lagu**: Tambah, ubah, dan hapus lagu beserta metadata lengkap
* **Validasi File**: Validasi otomatis tipe dan ukuran file
* **Sistem Edit**: Edit lagu yang telah di upload

## Manajemen Musik
* **Upload file audio** (`mp3`, `wav`, `ogg`, `flac`, `m4a`).
* **Upload cover image** (`jpg`, `jpeg`, `png`, `gif`, `webp`).
* **Lagu tersimpan secara permanen di file** `songs_data.json`.


## Struktur Data yang Digunakan
  - **Singly Linked List** → Manajemen playlist.
  - **Queue** → Sistem antrian lagu.
  - **Stack** → Riwayat pemutaran lagu.
  - **Binary Search Tree (BST)** → Pencarian lagu yang efisien.
  - **Graph** → Rekomendasi lagu berdasarkan genre.

---

## Memulai

Langkah-langkah menjalankan proyek di komputer lokal Anda.

### Prasyarat

* Python 3.8 atau lebih baru
* pip (Python package manager)
* Browser modern

### Instalasi

1. **Clone repository**

   ```bash
   git clone https://github.com/yourusername/music-player-app.git
   cd music-player-app
   ```

2. **Buat dan aktifkan virtual environment**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instal dependensi**

   ```bash
   pip install -r requirements.txt
   ```

4. **Buat direktori yang dibutuhkan**

   ```bash
   mkdir -p uploads/audio uploads/covers
   ```

5. **Jalankan aplikasi**

   ```bash
   python app.py
   ```

6. **Akses aplikasi**

   ```
   Buka browser dan kunjungi: http://localhost:5000
   ```

---

## Penggunaan

### Kredensial Default

**Akun Admin**

```
Username: admin
Password: admin123
```

**Akun User**

```
Username: user
Password: user123
```

> **Penting**: Ubah kredensial ini sebelum digunakan di lingkungan produksi!

### Panduan Singkat

#### Untuk User:

1. Login menggunakan akun user
2. Jelajahi lagu di menu Library
3. Klik **Play** untuk memulai pemutaran
4. Klik **Add Queue** untuk menambahkan lagu ke antrean
5. Klik **Favorite** untuk menandai lagu favorit
6. Masuk ke menu **Playlists** untuk mengelola playlist
7. Gunakan menu **Queue** untuk mengatur antrean pemutaran

#### Untuk Admin:

1. Login menggunakan akun admin
2. Klik tombol **Add New Song**
3. Isi detail lagu:

   * Judul
   * Artis
   * Durasi (dalam detik)
   * Genre
4. Unggah file audio (maksimal 50MB)
5. Unggah gambar sampul (maksimal 5MB)
6. Klik **Add Song** untuk menyimpan
7. Gunakan **Edit** untuk mengubah data lagu
8. Gunakan **Delete** untuk menghapus lagu

---

## Spesifikasi File

### Format Audio yang Didukung

* MP3 (.mp3)

### Format Gambar Sampul

* JPEG (.jpg, .jpeg)
* PNG (.png)

**Resolusi disarankan**: 500x500px atau 1000x1000px (persegi)

---

## Struktur Proyek

```

music-player-app/
│
├── app.py # Aplikasi utama Flask
├── templates/
│ ├── login.html # Halaman login dengan modal User/Admin
│ ├── user.html # Dashboard User dengan audio player
│ └── admin.html # Dashboard Admin
├── uploads/
│ ├── audio/ # File audio yang diupload
│ └── covers/ # File cover image yang diupload
├── songs_data.json # Penyimpanan data lagu secara permanen

---


  Dibuat dengan ❤️ oleh Adhinda Dwi Rahmadilla, Talitha Ineztasia, Annisa Sofia Albana

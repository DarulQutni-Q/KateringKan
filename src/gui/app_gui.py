import customtkinter as ctk
from tkinter import messagebox
import os
from src.services.katering_manager import KateringManager
from src.exceptions import AlergenTerdeteksiError, BahanProduksiTidakCukupError

# Global font setup (+5px dari standar biar lebih lega)
FONT_JUDUL = ("Helvetica", 29, "bold")
FONT_NORMAL = ("Helvetica", 19)
FONT_TOMBOL = ("Helvetica", 19, "bold")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(0.9)

class KateringAppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.km = KateringManager()
        self.resep_aktif = None

        self.title("KateringKU - Sistem Manajemen Pesanan & Logistik")
        self.geometry("1200x800") 
        
        # Grid Layout layar utama
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._bikin_sidebar()
        self._bikin_mainframe()
        
        self.buka_halaman("dashboard")

    def _bikin_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Dorong tombol keluar ke bawah

        logo = ctk.CTkLabel(self.sidebar_frame, text="KateringKU", font=FONT_JUDUL)
        logo.grid(row=0, column=0, padx=20, pady=(20, 30))

        # --- Navigasi ---
        btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="📦 Bahan & Stok", font=FONT_TOMBOL, command=lambda: self.buka_halaman("dashboard"))
        btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        btn_pelanggan = ctk.CTkButton(self.sidebar_frame, text="👥 Kelola Pelanggan", font=FONT_TOMBOL, command=lambda: self.buka_halaman("pelanggan"))
        btn_pelanggan.grid(row=2, column=0, padx=20, pady=10)

        btn_menu = ctk.CTkButton(self.sidebar_frame, text="🍲 Kelola Menu/Resep", font=FONT_TOMBOL, command=lambda: self.buka_halaman("menu"))
        btn_menu.grid(row=3, column=0, padx=20, pady=10)

        btn_pesan = ctk.CTkButton(self.sidebar_frame, text="📝 Buat Pesanan", font=FONT_TOMBOL, command=lambda: self.buka_halaman("pesan"))
        btn_pesan.grid(row=4, column=0, padx=20, pady=10)

        btn_tracking = ctk.CTkButton(self.sidebar_frame, text="🚚 Tracking Pesanan", font=FONT_TOMBOL, command=lambda: self.buka_halaman("tracking"))
        btn_tracking.grid(row=5, column=0, padx=20, pady=10)

        btn_laporan = ctk.CTkButton(self.sidebar_frame, text="📄 Ekspor CSV", font=FONT_TOMBOL, command=self.ekspor_csv)
        btn_laporan.grid(row=6, column=0, padx=20, pady=10)

        btn_keluar = ctk.CTkButton(self.sidebar_frame, text="Keluar", font=FONT_TOMBOL, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.destroy)
        btn_keluar.grid(row=9, column=0, padx=20, pady=20)

    def _bikin_mainframe(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

    def bersihin_layar(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # =========================================================================
    # HALAMAN 1: DASHBOARD / BAHAN BAKU
    # =========================================================================
    def buka_halaman(self, nama_halaman):
        self.bersihin_layar()

        if nama_halaman == "dashboard":
            ctk.CTkLabel(self.main_frame, text="Inventaris Bahan Baku", font=FONT_JUDUL).grid(row=0, column=0, pady=(0, 20))

            # --- Kiri: Daftar Stok (Format Tabel) ---
            frame_kiri = ctk.CTkScrollableFrame(self.main_frame, width=620)
            frame_kiri.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            
            ctk.CTkLabel(frame_kiri, text="Stok Saat Ini:", font=("Helvetica", 21, "bold")).grid(row=0, column=0, columnspan=4, pady=(10, 20), sticky="w")
            
            # Header Tabel
            headers = ["ID", "NAMA BAHAN", "STOK", "SATUAN", "AKSI"]
            for col, text in enumerate(headers):
                lbl_header = ctk.CTkLabel(frame_kiri, text=text, font=("Helvetica", 19, "bold"), fg_color="#1E3A8A", corner_radius=5)
                lbl_header.grid(row=1, column=col, padx=5, pady=5, sticky="ew", ipadx=10, ipady=5)

            # Isi Tabel
            baris = 2
            for bahan in self.km.daftar_bahan.values():
                ctk.CTkLabel(frame_kiri, text=bahan.id_bahan, font=FONT_NORMAL).grid(row=baris, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(frame_kiri, text=bahan.nama, font=FONT_NORMAL).grid(row=baris, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(frame_kiri, text=str(bahan.stok), font=FONT_NORMAL).grid(row=baris, column=2, padx=5, pady=2, sticky="e")
                ctk.CTkLabel(frame_kiri, text=bahan.satuan, font=FONT_NORMAL).grid(row=baris, column=3, padx=5, pady=2, sticky="w")
                ctk.CTkButton(frame_kiri, text="X", width=40, font=FONT_TOMBOL, fg_color="#E74C3C", hover_color="#C0392B",
                              command=lambda id_b=bahan.id_bahan: self.hapus_bahan_gui(id_b)).grid(row=baris, column=4, padx=5, pady=2)
                baris += 1

            # --- Kanan: Form Tambah/Update Bahan ---
            frame_kanan = ctk.CTkFrame(self.main_frame, width=400)
            frame_kanan.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(frame_kanan, text="Tambah / Update Stok", font=("Helvetica", 21, "bold")).pack(pady=10)

            # Update Stok yg udah ada
            ctk.CTkLabel(frame_kanan, text="Update Bahan Lama:", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10,0))
            list_bahan = [f"{b.id_bahan} - {b.nama}" for b in self.km.daftar_bahan.values()]
            cmb_bahan_upd = ctk.CTkComboBox(frame_kanan, values=list_bahan, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=300)
            if list_bahan: cmb_bahan_upd.set(list_bahan[0])
            cmb_bahan_upd.pack(padx=20, pady=5)
            
            ent_jml_upd = ctk.CTkEntry(frame_kanan, placeholder_text="Jml (Bisa minus buat ngurangin)", font=FONT_NORMAL, width=300)
            ent_jml_upd.pack(padx=20, pady=5)
            
            def proses_update_stok():
                try:
                    id_b = cmb_bahan_upd.get().split(" - ")[0]
                    jml = float(ent_jml_upd.get())
                    self.km.update_stok_bahan(id_b, jml)
                    messagebox.showinfo("Sukses", "Stok berhasil diupdate!")
                    self.buka_halaman("dashboard")
                except Exception as e:
                    messagebox.showerror("Error", "Inputan harus angka ya boss.")
            
            ctk.CTkButton(frame_kanan, text="Update Stok", font=FONT_TOMBOL, command=proses_update_stok).pack(pady=10)

            ctk.CTkLabel(frame_kanan, text="Atau Tambah Bahan Baru:", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(30,0))
            ent_nama_b = ctk.CTkEntry(frame_kanan, placeholder_text="Nama Bahan", font=FONT_NORMAL, width=300)
            ent_nama_b.pack(padx=20, pady=5)
            ent_stok_b = ctk.CTkEntry(frame_kanan, placeholder_text="Stok Awal", font=FONT_NORMAL, width=300)
            ent_stok_b.pack(padx=20, pady=5)
            ent_satuan_b = ctk.CTkEntry(frame_kanan, placeholder_text="Satuan (gram/butir/dll)", font=FONT_NORMAL, width=300)
            ent_satuan_b.pack(padx=20, pady=5)

            def proses_tambah_bahan():
                try:
                    self.km.tambah_bahan(ent_nama_b.get(), float(ent_stok_b.get()), ent_satuan_b.get())
                    messagebox.showinfo("Sukses", "Bahan baru berhasil masuk gudang!")
                    self.buka_halaman("dashboard")
                except:
                    messagebox.showerror("Error", "Cek lagi isiannya boss, stok harus angka.")
                    
            ctk.CTkButton(frame_kanan, text="Simpan Bahan Baru", font=FONT_TOMBOL, command=proses_tambah_bahan).pack(pady=10)

        # =========================================================================
        # HALAMAN 2: PELANGGAN & ALERGI
        # =========================================================================
        elif nama_halaman == "pelanggan":
            ctk.CTkLabel(self.main_frame, text="Kelola Pelanggan & Alergi", font=FONT_JUDUL).grid(row=0, column=0, pady=(0, 20))
            
            # Kiri: Daftar Pelanggan
            frame_kiri = ctk.CTkScrollableFrame(self.main_frame, width=450)
            frame_kiri.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            
            ctk.CTkLabel(frame_kiri, text="Daftar Pelanggan:", font=("Helvetica", 21, "bold")).pack(pady=10)
            for p in self.km.daftar_pelanggan.values():
                alergi_nama = [self.km.daftar_bahan[ab].nama for ab in p.daftar_alergi] if p.daftar_alergi else ["Aman"]
                teks = f"[{p.id_pelanggan}] {p.nama} ({p.no_hp})\nAlergi: {', '.join(alergi_nama)}"
                
                f_item = ctk.CTkFrame(frame_kiri)
                f_item.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(f_item, text=teks, font=FONT_NORMAL, justify="left").pack(side="left", padx=10, pady=5)
                
                # Fungsi hapus pake lambda binding
                ctk.CTkButton(f_item, text="X", width=40, font=FONT_TOMBOL, fg_color="#E74C3C", hover_color="#C0392B", 
                              command=lambda id_p=p.id_pelanggan: self.hapus_pelanggan_gui(id_p)).pack(side="right", padx=10)

            # Kanan: Form Tambah
            frame_kanan = ctk.CTkFrame(self.main_frame)
            frame_kanan.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(frame_kanan, text="Tambah Pelanggan Baru", font=("Helvetica", 21, "bold")).pack(pady=10)
            
            ent_nama_p = ctk.CTkEntry(frame_kanan, placeholder_text="Nama Pelanggan", font=FONT_NORMAL, width=300)
            ent_nama_p.pack(padx=20, pady=5)
            
            ent_hp_p = ctk.CTkEntry(frame_kanan, placeholder_text="No HP", font=FONT_NORMAL, width=300)
            ent_hp_p.pack(padx=20, pady=5)

            ctk.CTkLabel(frame_kanan, text="Pilih Alergi (Opsional):", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10,0))
            
            # List checkbox untuk alergi
            frame_alergi = ctk.CTkScrollableFrame(frame_kanan, width=280, height=200)
            frame_alergi.pack(padx=20, pady=5)
            
            checkboxes_alergi = []
            for b in self.km.daftar_bahan.values():
                var = ctk.StringVar(value="")
                chk = ctk.CTkCheckBox(frame_alergi, text=b.nama, variable=var, onvalue=b.id_bahan, offvalue="", font=FONT_NORMAL)
                chk.pack(anchor="w", pady=2)
                checkboxes_alergi.append(var)

            def proses_tambah_pelanggan():
                nama = ent_nama_p.get()
                hp = ent_hp_p.get()
                if not nama:
                    messagebox.showerror("Error", "Nama ga boleh kosong boss.")
                    return
                    
                alergi_terpilih = [var.get() for var in checkboxes_alergi if var.get() != ""]
                self.km.tambah_pelanggan(nama, hp, alergi_terpilih)
                messagebox.showinfo("Sukses", "Pelanggan baru tersimpan!")
                self.buka_halaman("pelanggan")

            ctk.CTkButton(frame_kanan, text="Simpan Pelanggan", font=FONT_TOMBOL, command=proses_tambah_pelanggan).pack(pady=20)

        # =========================================================================
        # HALAMAN 3: KELOLA MENU & RESEP
        # =========================================================================
        elif nama_halaman == "menu":
            ctk.CTkLabel(self.main_frame, text="Kelola Menu & Resep", font=FONT_JUDUL).grid(row=0, column=0, pady=(0, 20))
            
            frame_kiri = ctk.CTkScrollableFrame(self.main_frame, width=560)
            frame_kiri.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            self._render_daftar_menu(frame_kiri)

            frame_kanan = ctk.CTkScrollableFrame(self.main_frame, width=520)
            frame_kanan.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

            # ===== Section 1: Buat Menu Baru =====
            ctk.CTkLabel(frame_kanan, text="Bikin Menu Baru", font=("Helvetica", 21, "bold")).pack(pady=(10, 5))
            
            cmb_tipe = ctk.CTkComboBox(frame_kanan, values=["MenuReguler", "MenuVegetarian", "MenuBebasGluten"], font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=380)
            cmb_tipe.set("MenuReguler")
            cmb_tipe.pack(padx=20, pady=5)
            
            ent_nama_m = ctk.CTkEntry(frame_kanan, placeholder_text="Nama Menu", font=FONT_NORMAL, width=380)
            ent_nama_m.pack(padx=20, pady=5)
            
            ent_harga_m = ctk.CTkEntry(frame_kanan, placeholder_text="Harga Dasar (Rp)", font=FONT_NORMAL, width=380)
            ent_harga_m.pack(padx=20, pady=5)

            ctk.CTkLabel(frame_kanan, text="Pilih Resep:", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10, 0))
            list_resep = [f"{r.id_resep} - {r.nama_resep}" for r in self.km.daftar_resep.values()]
            cmb_resep = ctk.CTkComboBox(frame_kanan, values=list_resep, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=380)
            if list_resep: cmb_resep.set(list_resep[0])
            cmb_resep.pack(padx=20, pady=5)

            def proses_tambah_menu():
                try:
                    tipe = cmb_tipe.get()
                    nama = ent_nama_m.get()
                    harga = float(ent_harga_m.get())
                    id_r = cmb_resep.get().split(" - ")[0]
                    self.km.tambah_menu(tipe, nama, harga, id_r)
                    messagebox.showinfo("Sukses", "Menu baru berhasil ditambah!")
                    self.buka_halaman("menu")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal tambah menu: {e}")

            ctk.CTkButton(frame_kanan, text="Simpan Menu", font=FONT_TOMBOL, command=proses_tambah_menu).pack(pady=(10, 20))

            # ===== Section 2: Kelola Komposisi Bahan (Resep) =====
            ctk.CTkFrame(frame_kanan, height=2, fg_color="#333333").pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(frame_kanan, text="Kelola Komposisi Bahan (Resep)", font=("Helvetica", 21, "bold")).pack(pady=10)

            ctk.CTkLabel(frame_kanan, text="Pilih Resep:", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10, 0))
            cmb_resep_kelola = ctk.CTkComboBox(frame_kanan, values=list_resep, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=380)
            if list_resep:
                id_awal = self.resep_aktif if self.resep_aktif in self.km.daftar_resep else list_resep[0].split(" - ")[0]
                self.resep_aktif = id_awal
                cmb_resep_kelola.set(f"{id_awal} - {self.km.daftar_resep[id_awal].nama_resep}")
            cmb_resep_kelola.pack(padx=20, pady=5)

            frame_komposisi = ctk.CTkFrame(frame_kanan)
            frame_komposisi.pack(fill="x", padx=20, pady=10)

            def tampil_komposisi(id_resep):
                for w in frame_komposisi.winfo_children():
                    w.destroy()
                r = self.km.daftar_resep.get(id_resep)
                if not r:
                    ctk.CTkLabel(frame_komposisi, text="Resep tidak ditemukan.", font=FONT_NORMAL).pack(pady=10)
                    return
                komposisi = r.komposisi_bahan or {}
                if not komposisi:
                    ctk.CTkLabel(frame_komposisi, text="(Belum ada bahan. Tambah di bawah.)", font=FONT_NORMAL, text_color="#9CA3AF").pack(pady=10)
                    return
                for id_b, jml in komposisi.items():
                    b = self.km.daftar_bahan.get(id_b)
                    nama_b = b.nama if b else f"{id_b} (hilang)"
                    satuan = b.satuan if b else ""
                    f_b = ctk.CTkFrame(frame_komposisi, fg_color="transparent")
                    f_b.pack(fill="x", padx=5, pady=2)
                    ctk.CTkLabel(f_b, text=f"{nama_b}: {jml:g} {satuan}", font=FONT_NORMAL, justify="left").pack(side="left", padx=5)
                    ctk.CTkButton(f_b, text="X", width=40, font=FONT_TOMBOL, fg_color="#E74C3C", hover_color="#C0392B",
                                  command=lambda rid=id_resep, bid=id_b: self.hapus_bahan_resep_gui(rid, bid, frame_kiri, tampil_komposisi)).pack(side="right", padx=5)

            def pilih_resep_kelola(choice):
                if choice:
                    self.resep_aktif = choice.split(" - ")[0]
                    tampil_komposisi(self.resep_aktif)

            cmb_resep_kelola.configure(command=pilih_resep_kelola)

            if list_resep:
                tampil_komposisi(self.resep_aktif)

            ctk.CTkLabel(frame_kanan, text="Tambah Bahan ke Resep:", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10, 0))
            list_bahan_gudang = [f"{b.id_bahan} - {b.nama}" for b in self.km.daftar_bahan.values()]
            cmb_bahan_r = ctk.CTkComboBox(frame_kanan, values=list_bahan_gudang, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=380)
            if list_bahan_gudang: cmb_bahan_r.set(list_bahan_gudang[0])
            cmb_bahan_r.pack(padx=20, pady=5)
            ent_jml_r = ctk.CTkEntry(frame_kanan, placeholder_text="Jumlah bahan per porsi", font=FONT_NORMAL, width=380)
            ent_jml_r.pack(padx=20, pady=5)

            def proses_tambah_bahan_resep():
                try:
                    id_r = cmb_resep_kelola.get().split(" - ")[0]
                    id_b = cmb_bahan_r.get().split(" - ")[0]
                    jml = float(ent_jml_r.get())
                    if jml <= 0:
                        raise ValueError("Jumlah harus lebih dari 0")
                    if self.km.tambah_bahan_ke_resep(id_r, id_b, jml):
                        messagebox.showinfo("Sukses", "Bahan ditambahkan ke resep!")
                        ent_jml_r.delete(0, "end")
                        tampil_komposisi(id_r)
                        self._render_daftar_menu(frame_kiri)
                    else:
                        messagebox.showerror("Error", "Resep atau bahan tidak valid.")
                except Exception:
                    messagebox.showerror("Error", "Isi jumlah dengan angka yang benar boss.")

            ctk.CTkButton(frame_kanan, text="Tambah Bahan ke Resep", font=FONT_TOMBOL, command=proses_tambah_bahan_resep).pack(pady=(10, 20))

            # ===== Section 3: Buat Resep Baru =====
            ctk.CTkFrame(frame_kanan, height=2, fg_color="#333333").pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(frame_kanan, text="Buat Resep Baru", font=("Helvetica", 21, "bold")).pack(pady=10)
            ent_nama_resep = ctk.CTkEntry(frame_kanan, placeholder_text="Nama Resep", font=FONT_NORMAL, width=380)
            ent_nama_resep.pack(padx=20, pady=5)
            ent_instruksi = ctk.CTkEntry(frame_kanan, placeholder_text="Instruksi (opsional)", font=FONT_NORMAL, width=380)
            ent_instruksi.pack(padx=20, pady=5)

            def proses_buat_resep():
                nama_r = ent_nama_resep.get().strip()
                if not nama_r:
                    messagebox.showerror("Error", "Nama resep wajib diisi boss.")
                    return
                r = self.km.tambah_resep(nama_r, {}, ent_instruksi.get().strip())
                self.resep_aktif = r.id_resep
                messagebox.showinfo("Sukses", f"Resep {r.id_resep} dibuat. Tambahkan bahannya di panel Kelola Komposisi.")
                self.buka_halaman("menu")

            ctk.CTkButton(frame_kanan, text="Simpan Resep Baru", font=FONT_TOMBOL, command=proses_buat_resep).pack(pady=(10, 20))


        # =========================================================================
        # HALAMAN 4: TRACKING PESANAN & PENGIRIMAN
        # =========================================================================
        elif nama_halaman == "tracking":
            ctk.CTkLabel(self.main_frame, text="Tracking Jadwal & Pengiriman", font=FONT_JUDUL).grid(row=0, column=0, pady=(0, 20))
            
            frame_list = ctk.CTkScrollableFrame(self.main_frame)
            frame_list.grid(row=1, column=0, sticky="nsew")

            for p in reversed(self.km.daftar_pesanan): # Dibalik biar yg terbaru di atas
                f_item = ctk.CTkFrame(frame_list)
                f_item.pack(fill="x", padx=10, pady=10)
                
                # Deteksi telat
                telat_str = " (⚠️ TERLAMBAT!)" if p.is_terlambat() else ""
                warna_teks = "#E74C3C" if p.is_terlambat() else ("gray10", "#DCE4EE")

                info = (f"[{p.id_pesanan}] {p.pelanggan.nama} | Total: Rp {p.total_biaya:,.0f}\n"
                        f"Prod: {p.tanggal_produksi} | Kirim: {p.tanggal_pengiriman}{telat_str}\n"
                        f"Alamat: {p.alamat}")
                
                ctk.CTkLabel(f_item, text=info, font=FONT_NORMAL, text_color=warna_teks, justify="left").pack(side="left", padx=10, pady=10)

                # Form Update Status di Kanan item
                f_aksi = ctk.CTkFrame(f_item, fg_color="transparent")
                f_aksi.pack(side="right", padx=10)
                
                cmb_status = ctk.CTkComboBox(f_aksi, values=["Diproduksi", "Dikirim", "Terkirim", "Selesai"], font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=150)
                cmb_status.set(p.status)
                cmb_status.pack(pady=5)
                
                # Pake parameter default di lambda biar id nya ga ketimpa loop terakhir
                ctk.CTkButton(f_aksi, text="Update", font=FONT_TOMBOL, width=100,
                              command=lambda id_p=p.id_pesanan, combo=cmb_status: self.update_status_gui(id_p, combo.get())).pack(pady=5)


        # =========================================================================
        # HALAMAN 5: BUAT PESANAN BARU
        # =========================================================================
        elif nama_halaman == "pesan":
            ctk.CTkLabel(self.main_frame, text="Form Order Katering", font=FONT_JUDUL).grid(row=0, column=0, pady=(0, 20))

            # Outer frame untuk scroll
            frame_scroll = ctk.CTkScrollableFrame(self.main_frame)
            frame_scroll.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

            # Inner frame yang diletakkan di tengah
            form_container = ctk.CTkFrame(frame_scroll, fg_color="transparent")
            form_container.pack(expand=True, anchor="n", pady=20) # anchor="n" biar nempel di atas tengah

            ctk.CTkLabel(form_container, text="Pelanggan:", font=FONT_NORMAL).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            list_pelg = [f"{p.id_pelanggan} - {p.nama}" for p in self.km.daftar_pelanggan.values()]
            self.cmb_pelanggan = ctk.CTkComboBox(form_container, values=list_pelg, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=350, height=35)
            if list_pelg: self.cmb_pelanggan.set(list_pelg[0])
            self.cmb_pelanggan.grid(row=0, column=1, padx=10, pady=10)

            ctk.CTkLabel(form_container, text="Menu Utama:", font=FONT_NORMAL).grid(row=1, column=0, padx=10, pady=10, sticky="w")
            list_menu = [f"{m.id_menu} - {m.nama} - {self._format_harga_menu_dropdown(m)}" for m in self.km.daftar_menu.values()]
            list_menu.insert(0, "Pilih Menu...")
            self.cmb_menu1 = ctk.CTkComboBox(form_container, values=list_menu, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=560, height=35)
            self.cmb_menu1.set("Pilih Menu...")
            self.cmb_menu1.grid(row=1, column=1, padx=10, pady=10)
            
            ctk.CTkLabel(form_container, text="Porsi M1:", font=FONT_NORMAL).grid(row=1, column=2, padx=10, pady=10, sticky="w")
            self.ent_porsi1 = ctk.CTkEntry(form_container, width=80, font=FONT_NORMAL, height=35)
            self.ent_porsi1.insert(0, "1")
            self.ent_porsi1.grid(row=1, column=3, padx=10, pady=10)

            ctk.CTkLabel(form_container, text="Menu Tambahan (Paket):", font=FONT_NORMAL).grid(row=2, column=0, padx=10, pady=10, sticky="w")
            self.cmb_menu2 = ctk.CTkComboBox(form_container, values=list_menu, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=560, height=35)
            self.cmb_menu2.set("Pilih Menu...")
            self.cmb_menu2.grid(row=2, column=1, padx=10, pady=10)
            
            ctk.CTkLabel(form_container, text="Porsi M2:", font=FONT_NORMAL).grid(row=2, column=2, padx=10, pady=10, sticky="w")
            self.ent_porsi2 = ctk.CTkEntry(form_container, width=80, font=FONT_NORMAL, height=35)
            self.ent_porsi2.insert(0, "0")
            self.ent_porsi2.grid(row=2, column=3, padx=10, pady=10)

            ctk.CTkLabel(form_container, text="Acara (Opsional):", font=FONT_NORMAL).grid(row=3, column=0, padx=10, pady=10, sticky="w")
            list_acara = [f"{a.id_acara} - {a.nama_acara}" for a in self.km.daftar_acara.values()]
            list_acara.insert(0, "Tidak ada acara")
            self.cmb_acara = ctk.CTkComboBox(form_container, values=list_acara, font=FONT_NORMAL, dropdown_font=FONT_NORMAL, state="readonly", width=350, height=35)
            self.cmb_acara.set("Tidak ada acara")
            self.cmb_acara.grid(row=3, column=1, padx=10, pady=10)

            ctk.CTkLabel(form_container, text="Tgl Produksi (YYYY-MM-DD):", font=FONT_NORMAL).grid(row=4, column=0, padx=10, pady=10, sticky="w")
            self.ent_tgl_prod = ctk.CTkEntry(form_container, width=350, font=FONT_NORMAL, height=35)
            self.ent_tgl_prod.insert(0, "2024-12-01")
            self.ent_tgl_prod.grid(row=4, column=1, padx=10, pady=10)
            
            ctk.CTkLabel(form_container, text="Tgl Kirim (YYYY-MM-DD):", font=FONT_NORMAL).grid(row=5, column=0, padx=10, pady=10, sticky="w")
            self.ent_tgl_kirim = ctk.CTkEntry(form_container, width=350, font=FONT_NORMAL, height=35)
            self.ent_tgl_kirim.insert(0, "2024-12-02")
            self.ent_tgl_kirim.grid(row=5, column=1, padx=10, pady=10)

            ctk.CTkLabel(form_container, text="Alamat Pengiriman:", font=FONT_NORMAL).grid(row=6, column=0, padx=10, pady=10, sticky="nw")
            self.txt_alamat = ctk.CTkTextbox(form_container, width=350, height=80, font=FONT_NORMAL)
            self.txt_alamat.grid(row=6, column=1, padx=10, pady=10)

            ctk.CTkLabel(form_container, text="Opsi Spesial (Decorator):", font=FONT_NORMAL).grid(row=7, column=0, padx=10, pady=10, sticky="nw")
            frame_opsi = ctk.CTkFrame(form_container, fg_color="transparent")
            frame_opsi.grid(row=7, column=1, padx=10, pady=10, sticky="w")
            
            self.var_premium = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(frame_opsi, text="Kemasan Premium (+Rp8k)", font=FONT_NORMAL, variable=self.var_premium).pack(anchor="w", pady=5)
            
            self.var_lauk = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(frame_opsi, text="Extra Telor Ceplok (+Rp5k)", font=FONT_NORMAL, variable=self.var_lauk).pack(anchor="w", pady=5)

            self.var_express = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(frame_opsi, text="Layanan Express (+Rp15k)", font=FONT_NORMAL, variable=self.var_express).pack(anchor="w", pady=5)

            # Tombol Validasi dibikin center dan lebar
            btn_submit = ctk.CTkButton(form_container, text="Validasi & Pesan", font=FONT_TOMBOL, command=self.proses_submit, height=50)
            btn_submit.grid(row=8, column=0, columnspan=4, pady=30, sticky="ew")

    # =========================================================================
    # FUNGSI-FUNGSI LOGIKA GUI
    # =========================================================================
    def hapus_pelanggan_gui(self, id_p):
        if messagebox.askyesno("Konfirmasi", "Beneran mau hapus pelanggan ini?"):
            self.km.hapus_pelanggan(id_p)
            self.buka_halaman("pelanggan")

    def hapus_bahan_gui(self, id_bahan):
        if messagebox.askyesno("Konfirmasi", "Beneran mau hapus bahan ini?"):
            try:
                self.km.hapus_bahan(id_bahan)
                self.buka_halaman("dashboard")
            except ValueError as e:
                messagebox.showerror("Tidak Bisa Hapus", str(e))

    def hapus_menu_gui(self, id_m):
        if messagebox.askyesno("Konfirmasi", "Hapus menu ini dari daftar?"):
            self.km.hapus_menu(id_m)
            self.buka_halaman("menu")

    def _format_harga_menu(self, menu):
        harga = menu.hitung_biaya_porsi()
        tipe = menu.__class__.__name__
        if tipe == "MenuVegetarian":
            return f"Rp {harga:,.0f} (diskon 5%)"
        if tipe == "MenuBebasGluten":
            return f"Rp {harga:,.0f} (markup 15%)"
        return f"Rp {harga:,.0f}"

    def _format_harga_menu_dropdown(self, menu):
        harga = menu.hitung_biaya_porsi()
        tipe = menu.__class__.__name__
        if tipe == "MenuVegetarian":
            return f"Rp {harga:,.0f} (-5%)"
        if tipe == "MenuBebasGluten":
            return f"Rp {harga:,.0f} (+15%)"
        return f"Rp {harga:,.0f}"

    def _render_daftar_menu(self, frame_kiri):
        for w in frame_kiri.winfo_children():
            w.destroy()

        ctk.CTkLabel(frame_kiri, text="Daftar Menu Katering:", font=("Helvetica", 21, "bold")).pack(pady=10)
        for m in self.km.daftar_menu.values():
            nama_bahan = []
            for id_b, jml in m.get_daftar_bahan().items():
                b = self.km.daftar_bahan.get(id_b)
                if b:
                    nama_bahan.append(f"{b.nama} ({jml:g} {b.satuan})")
                else:
                    nama_bahan.append(f"{id_b} ({jml:g})")

            teks = (f"[{m.id_menu}] {m.nama}\n"
                    f"{self._format_harga_menu(m)} | Porsi Terjual: {m.stok_porsi}\n"
                    f"Bahan: {', '.join(nama_bahan) if nama_bahan else '-'}")
            f_item = ctk.CTkFrame(frame_kiri)
            f_item.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(f_item, text=teks, font=FONT_NORMAL, justify="left").pack(side="left", padx=10, pady=5)
            ctk.CTkButton(f_item, text="X", width=40, font=FONT_TOMBOL, fg_color="#E74C3C", hover_color="#C0392B",
                          command=lambda id_m=m.id_menu: self.hapus_menu_gui(id_m)).pack(side="right", padx=10)

    def hapus_bahan_resep_gui(self, id_resep, id_bahan, frame_kiri, refresh_komposisi):
        if messagebox.askyesno("Konfirmasi", f"Hapus bahan ini dari resep {id_resep}?"):
            if self.km.hapus_bahan_dari_resep(id_resep, id_bahan):
                refresh_komposisi(id_resep)
                self._render_daftar_menu(frame_kiri)

    def update_status_gui(self, id_p, status_baru):
        self.km.update_status_pesanan(id_p, status_baru)
        messagebox.showinfo("Sukses", f"Pesanan {id_p} update jadi {status_baru}")
        self.buka_halaman("tracking")

    def proses_submit(self):
        try:
            id_pelg = self.cmb_pelanggan.get().split(" - ")[0]
            
            paket_pesanan = []
            m1 = self.cmb_menu1.get()
            if m1 != "Pilih Menu...":
                paket_pesanan.append({"id_menu": m1.split(" - ")[0], "porsi": int(self.ent_porsi1.get())})
                
            m2 = self.cmb_menu2.get()
            if m2 != "Pilih Menu...":
                p2 = int(self.ent_porsi2.get())
                if p2 > 0:
                    paket_pesanan.append({"id_menu": m2.split(" - ")[0], "porsi": p2})

            if not paket_pesanan:
                messagebox.showwarning("Waduh", "Pilih minimal 1 menu dulu boss.")
                return

            acara_val = self.cmb_acara.get()
            id_acara = None if acara_val == "Tidak ada acara" else acara_val.split(" - ")[0]
            
            tgl_prod = self.ent_tgl_prod.get()
            tgl_kirim = self.ent_tgl_kirim.get()
            alamat = self.txt_alamat.get("1.0", "end-1c").strip()
            if not alamat:
                raise ValueError("Alamat pengiriman jangan dikosongin!")

            opsi_config = {
                'premium': self.var_premium.get(),
                'lauk': self.var_lauk.get(),
                'express': self.var_express.get()
            }

            pesanan = self.km.proses_pesanan_baru(id_pelg, paket_pesanan, tgl_prod, tgl_kirim, alamat, opsi_config, id_acara)
            
            # Tunjukin Rincian Biaya (Requirement Perhitungan Biaya yang transparan)
            pesan_sukses = f"SUKSES!\nID Order: {pesanan.id_pesanan}\nStatus: {pesanan.status}\n\nRINCIAN BIAYA:\n"
            for m in pesanan.menu_list:
                pesan_sukses += f"- {m['menu_obj'].nama} (x{m['porsi']}): Rp {m['menu_obj'].hitung_biaya_porsi() * m['porsi']:,.0f}\n"
            pesan_sukses += f"\nTOTAL TAGIHAN: Rp {pesanan.total_biaya:,.0f}"
            
            messagebox.showinfo("Pesanan Dikonfirmasi", pesan_sukses)
            self.buka_halaman("tracking")

        except ValueError as ve:
            messagebox.showerror("Error Input", str(ve))
        except AlergenTerdeteksiError as alergi:
            messagebox.showerror("BAHAYA ALERGI!", str(alergi))
        except BahanProduksiTidakCukupError as bahan_kurang:
            messagebox.showwarning("Stok Gudang Menipis", str(bahan_kurang))
        except Exception as e:
            messagebox.showerror("Sistem Error", f"Terjadi kesalahan teknis: {e}")

    def ekspor_csv(self):
        try:
            path = self.km.bikin_semua_laporan()
            if path:
                messagebox.showinfo("Ekspor Sukses", f"File laporan disimpan di:\n{path}")
            else:
                messagebox.showwarning("Kosong", "Gagal bikin CSV, mungkin belum ada pesanan.")
        except Exception as e:
            messagebox.showerror("Gagal", f"Tidak dapat mengekspor: {e}")

if __name__ == "__main__":
    app = KateringAppGUI()
    app.mainloop()

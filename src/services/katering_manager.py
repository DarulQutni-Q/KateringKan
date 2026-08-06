from datetime import datetime
from src.models.menu import MenuReguler, MenuVegetarian, MenuBebasGluten
from src.models.bahan import Bahan, Resep
from src.models.decorator import OpsiLaukTambahan, OpsiKemasanPremium, OpsiLayananExpress
from src.models.pesanan import Pelanggan, Pesanan, Acara
from src.services.file_handler import FileHandler
from src.exceptions import AlergenTerdeteksiError, BahanProduksiTidakCukupError

class KateringManager:
    def __init__(self):
        self.daftar_bahan = {} # id: obj Bahan
        self.daftar_resep = {} # id: obj Resep
        self.daftar_pelanggan = {} # id: obj Pelanggan
        self.daftar_acara = {} # id: obj Acara
        self.daftar_menu = {} # id: obj Menu
        self.daftar_pesanan = [] # list obj Pesanan
        
        self.load_data_awal()

    def load_data_awal(self):
        # 1. Load Bahan
        d_bahan = FileHandler.baca_json('bahan.json')
        if not d_bahan:
            self.generate_dummy_master_data()
            return # Karena function dummy sekalian bikin semuanya
        else:
            for b in d_bahan:
                self.daftar_bahan[b['id_bahan']] = Bahan(**b)

        # 2. Load Resep
        d_resep = FileHandler.baca_json('resep.json')
        for r in d_resep:
            self.daftar_resep[r['id_resep']] = Resep(**r)

        # 3. Load Pelanggan
        d_pelg = FileHandler.baca_json('pelanggan.json')
        for p in d_pelg:
            self.daftar_pelanggan[p['id_pelanggan']] = Pelanggan(**p)
            
        # 4. Load Acara
        d_acara = FileHandler.baca_json('acara.json')
        for a in d_acara:
            self.daftar_acara[a['id_acara']] = Acara(**a)

        # 5. Load Menu (dan kaitkan sama Resep)
        d_menu = FileHandler.baca_json('menu_katering.json')
        for m in d_menu:
            tipe = m.pop('tipe')
            id_resep = m.pop('resep_id')
            resep_obj = self.daftar_resep.get(id_resep)
            
            # Buang field sisa yg ga ada di init MenuKatering
            if 'daftar_bahan' in m: m.pop('daftar_bahan')
            
            if tipe == 'MenuReguler':
                self.daftar_menu[m['id_menu']] = MenuReguler(resep=resep_obj, **m)
            elif tipe == 'MenuVegetarian':
                self.daftar_menu[m['id_menu']] = MenuVegetarian(resep=resep_obj, **m)
            elif tipe == 'MenuBebasGluten':
                self.daftar_menu[m['id_menu']] = MenuBebasGluten(resep=resep_obj, **m)

    def simpan_semua_data(self):
        FileHandler.tulis_json('bahan.json', [b.to_dict() for b in self.daftar_bahan.values()])
        FileHandler.tulis_json('resep.json', [r.to_dict() for r in self.daftar_resep.values()])
        FileHandler.tulis_json('pelanggan.json', [p.to_dict() for p in self.daftar_pelanggan.values()])
        FileHandler.tulis_json('acara.json', [a.to_dict() for a in self.daftar_acara.values()])
        FileHandler.tulis_json('menu_katering.json', [m.to_dict() for m in self.daftar_menu.values()])
        FileHandler.tulis_json('pesanan_katering.json', [p.to_dict() for p in self.daftar_pesanan])

    def proses_pesanan_baru(self, id_pelanggan, list_item_pesanan, tgl_produksi, tgl_kirim, alamat, opsi=None, id_acara=None):
        """
        list_item_pesanan bentuknya array dictionary: [{"id_menu": "M01", "porsi": 10}, ...]
        opsi bentuknya dictionary untuk config decorator: {"lauk": bool, "premium": bool, "express": bool}
        """
        pelanggan = self.daftar_pelanggan.get(id_pelanggan)
        if not pelanggan:
            raise ValueError("Pelanggan ga valid.")
            
        acara = self.daftar_acara.get(id_acara) if id_acara else None

        # Build paket menu akhir
        menu_final_list = []
        for item in list_item_pesanan:
            menu_base = self.daftar_menu.get(item['id_menu'])
            if not menu_base:
                continue
                
            menu_jadi = menu_base
            # Wrap dengan decorator berjenjang
            if opsi:
                if opsi.get('premium'):
                    menu_jadi = OpsiKemasanPremium(menu_jadi)
                if opsi.get('lauk'):
                    menu_jadi = OpsiLaukTambahan(menu_jadi, "B005", 1, 5000, "Telor Ceplok")
                if opsi.get('express'):
                    menu_jadi = OpsiLayananExpress(menu_jadi)
                    
            menu_final_list.append({
                "menu_obj": menu_jadi,
                "porsi": item['porsi']
            })

        # Bikin pesanan dummy buat kalkulasi validasi
        pesanan_temp = Pesanan("TEMP", pelanggan, menu_final_list, tgl_produksi, tgl_kirim, alamat, acara)

        # 1. Validasi Alergi (Cek ke semua total bahan pesanan temp)
        kebutuhan_bahan_temp = pesanan_temp.get_semua_kebutuhan_bahan()
        alergen_kena = [id_b for id_b in kebutuhan_bahan_temp.keys() if id_b in pelanggan.daftar_alergi]
        if alergen_kena:
            nama_alergen = [self.daftar_bahan[ab].nama for ab in alergen_kena]
            raise AlergenTerdeteksiError(pelanggan.nama, nama_alergen)

        # 2. Validasi Stok
        bahan_kurang = {}
        for id_b, total_butuh in kebutuhan_bahan_temp.items():
            stok_gudang = self.daftar_bahan[id_b].stok
            if stok_gudang < total_butuh:
                bahan_kurang[self.daftar_bahan[id_b].nama] = total_butuh - stok_gudang
        
        if bahan_kurang:
            raise BahanProduksiTidakCukupError(bahan_kurang)

        # 3. Potong stok beneran & update porsi menu
        for id_b, total_butuh in kebutuhan_bahan_temp.items():
            self.daftar_bahan[id_b].kurangi_stok(total_butuh)
            
        for item in menu_final_list:
            # Update stok_porsi di menu base lewat enkapsulasinya (setter)
            if hasattr(item['menu_obj'], 'menu_dasar'):
                item['menu_obj'].menu_dasar.stok_porsi += item['porsi']
            else:
                item['menu_obj'].stok_porsi += item['porsi']

        # Bikin beneran
        id_baru = f"ORD-{len(self.daftar_pesanan)+1:03d}"
        pesanan_temp.id_pesanan = id_baru
        pesanan_temp.status = "Diproduksi" # Masuk dapur
        self.daftar_pesanan.append(pesanan_temp)
        self.simpan_semua_data()
        
        return pesanan_temp

    def bikin_semua_laporan(self):
        # Minta rekapan lengkap sesuai soal: biaya, terlambat, dll.
        laporan = []
        for p in self.daftar_pesanan:
            menu_names = [f"{m['menu_obj'].nama} (x{m['porsi']})" for m in p.menu_list]
            
            terlambat = "YA" if p.is_terlambat() else "TIDAK"
            
            laporan.append({
                "ID Pesanan": p.id_pesanan,
                "Pelanggan": p.pelanggan.nama,
                "Isi Paket Menu": " | ".join(menu_names),
                "Total Biaya": p.total_biaya,
                "Jadwal Produksi": p.tanggal_produksi,
                "Jadwal Pengiriman": p.tanggal_pengiriman,
                "Alamat": p.alamat,
                "Status": p.status,
                "Kategori Terlambat?": terlambat
            })
            
        return FileHandler.ekspor_laporan_csv(laporan)

    def tambah_bahan(self, nama, stok, satuan):
        id_baru = f"B{len(self.daftar_bahan)+1:03d}"
        b = Bahan(id_baru, nama, stok, satuan)
        self.daftar_bahan[id_baru] = b
        self.simpan_semua_data()
        return b

    def update_stok_bahan(self, id_bahan, jumlah_tambah):
        if id_bahan in self.daftar_bahan:
            self.daftar_bahan[id_bahan].stok += jumlah_tambah
            self.simpan_semua_data()
            return True
        return False

    def hapus_bahan(self, id_bahan):
        if id_bahan not in self.daftar_bahan:
            return False

        # Cek referensi: dipakai di resep mana & alergi siapa
        dipakai_resep = [r.nama_resep for r in self.daftar_resep.values()
                         if id_bahan in (r.komposisi_bahan or {})]
        dipakai_alergi = [p.nama for p in self.daftar_pelanggan.values()
                          if id_bahan in (p.daftar_alergi or [])]

        if dipakai_resep or dipakai_alergi:
            alasan = []
            if dipakai_resep:
                alasan.append("resep: " + ", ".join(dipakai_resep))
            if dipakai_alergi:
                alasan.append("alergi: " + ", ".join(dipakai_alergi))
            raise ValueError("Bahan masih dipakai di " + " & ".join(alasan))

        del self.daftar_bahan[id_bahan]
        self.simpan_semua_data()
        return True

    def tambah_pelanggan(self, nama, no_hp, daftar_alergi):
        id_baru = f"P{len(self.daftar_pelanggan)+1:03d}"
        p = Pelanggan(id_baru, nama, no_hp, daftar_alergi)
        self.daftar_pelanggan[id_baru] = p
        self.simpan_semua_data()
        return p

    def hapus_pelanggan(self, id_pelanggan):
        if id_pelanggan in self.daftar_pelanggan:
            del self.daftar_pelanggan[id_pelanggan]
            self.simpan_semua_data()
            return True
        return False

    def tambah_resep(self, nama_resep, komposisi, instruksi):
        id_baru = f"R{len(self.daftar_resep)+1:02d}"
        r = Resep(id_baru, nama_resep, komposisi, instruksi)
        self.daftar_resep[id_baru] = r
        self.simpan_semua_data()
        return r

    def update_resep(self, id_resep, nama_resep, komposisi_bahan, instruksi):
        if id_resep not in self.daftar_resep:
            return False
        r = self.daftar_resep[id_resep]
        r.nama_resep = nama_resep
        r.komposisi_bahan = komposisi_bahan
        r.instruksi = instruksi
        self._refresh_menu_dari_resep(id_resep)
        self.simpan_semua_data()
        return True

    def _refresh_menu_dari_resep(self, id_resep):
        for m in self.daftar_menu.values():
            if m._resep and m._resep.id_resep == id_resep:
                m.sync_bahan_dari_resep()

    def tambah_bahan_ke_resep(self, id_resep, id_bahan, jumlah):
        if id_resep not in self.daftar_resep or id_bahan not in self.daftar_bahan:
            return False
        r = self.daftar_resep[id_resep]
        komposisi = dict(r.komposisi_bahan or {})
        komposisi[id_bahan] = komposisi.get(id_bahan, 0) + float(jumlah)
        return self.update_resep(id_resep, r.nama_resep, komposisi, r.instruksi)

    def hapus_bahan_dari_resep(self, id_resep, id_bahan):
        if id_resep not in self.daftar_resep:
            return False
        r = self.daftar_resep[id_resep]
        komposisi = dict(r.komposisi_bahan or {})
        if id_bahan in komposisi:
            del komposisi[id_bahan]
            return self.update_resep(id_resep, r.nama_resep, komposisi, r.instruksi)
        return False

    def tambah_menu(self, tipe, nama, harga_dasar, id_resep):
        id_baru = f"M{len(self.daftar_menu)+1:03d}"
        resep_obj = self.daftar_resep.get(id_resep)
        
        if tipe == 'MenuReguler':
            m = MenuReguler(id_baru, nama, harga_dasar, resep_obj)
        elif tipe == 'MenuVegetarian':
            m = MenuVegetarian(id_baru, nama, harga_dasar, resep_obj)
        elif tipe == 'MenuBebasGluten':
            m = MenuBebasGluten(id_baru, nama, harga_dasar, resep_obj)
        else:
            raise ValueError("Tipe menu ga valid boss.")
            
        self.daftar_menu[id_baru] = m
        self.simpan_semua_data()
        return m

    def hapus_menu(self, id_menu):
        if id_menu in self.daftar_menu:
            del self.daftar_menu[id_menu]
            self.simpan_semua_data()
            return True
        return False

    def update_status_pesanan(self, id_pesanan, status_baru):
        for p in self.daftar_pesanan:
            if p.id_pesanan == id_pesanan:
                p.status = status_baru
                self.simpan_semua_data()
                return True
        return False

    def generate_dummy_master_data(self):
        # Setup Bahan
        b1 = Bahan("B001", "Beras Putih", 100000, "gram")
        b2 = Bahan("B002", "Daging Sapi", 50000, "gram")
        b3 = Bahan("B003", "Kacang Tanah", 20000, "gram")
        b4 = Bahan("B004", "Brokoli", 30000, "gram")
        b5 = Bahan("B005", "Telor Ayam", 100, "butir")
        b6 = Bahan("B006", "Tepung Gandum (Gluten)", 40000, "gram")
        b7 = Bahan("B007", "Tepung Maizena (GF)", 30000, "gram")
        
        self.daftar_bahan = {b.id_bahan: b for b in [b1, b2, b3, b4, b5, b6, b7]}

        # Setup Resep
        r1 = Resep("R01", "Resep Nasi Daging Sapi", {"B001": 200, "B002": 150, "B006": 10}, "Rebus daging, masak nasi")
        r2 = Resep("R02", "Resep Nasi Sayur Kacang", {"B001": 200, "B004": 150, "B003": 50}, "Rebus sayur, siram bumbu kacang")
        r3 = Resep("R03", "Resep Daging Krispi GF", {"B002": 200, "B007": 50}, "Balur daging ke maizena, goreng")
        
        self.daftar_resep = {r.id_resep: r for r in [r1, r2, r3]}

        # Setup Pelanggan
        p1 = Pelanggan("P001", "Bapak Fulan", "0811", [])
        p2 = Pelanggan("P002", "Ibu Fulanah", "0822", ["B003"]) # Alergi kacang
        p3 = Pelanggan("P003", "Mbak Sehat", "0833", ["B006"]) # Alergi gluten
        self.daftar_pelanggan = {p.id_pelanggan: p for p in [p1, p2, p3]}

        # Setup Acara
        a1 = Acara("A01", "Pernikahan Budi", "Wedding")
        a2 = Acara("A02", "Rapat Paripurna", "Corporate")
        self.daftar_acara = {a.id_acara: a for a in [a1, a2]}

        # Setup Menu
        m1 = MenuReguler("M001", "Nasi Daging Biasa", 35000, r1)
        m2 = MenuVegetarian("M002", "Nasi Pecel Brokoli", 20000, r2)
        m3 = MenuBebasGluten("M003", "Daging Krispi Diet", 40000, r3)
        self.daftar_menu = {m.id_menu: m for m in [m1, m2, m3]}

        self.simpan_semua_data()

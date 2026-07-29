from datetime import datetime

class Pelanggan:
    def __init__(self, id_pelanggan, nama, no_hp, daftar_alergi=None):
        self.id_pelanggan = id_pelanggan
        self.nama = nama
        self.no_hp = no_hp
        self.daftar_alergi = daftar_alergi if daftar_alergi else []

    def to_dict(self):
        return {
            "id_pelanggan": self.id_pelanggan,
            "nama": self.nama,
            "no_hp": self.no_hp,
            "daftar_alergi": self.daftar_alergi
        }

class Acara:
    def __init__(self, id_acara, nama_acara, tipe_acara):
        self.id_acara = id_acara
        self.nama_acara = nama_acara
        self.tipe_acara = tipe_acara # e.g. "Pernikahan", "Rapat"

    def to_dict(self):
        return {
            "id_acara": self.id_acara,
            "nama_acara": self.nama_acara,
            "tipe_acara": self.tipe_acara
        }

class Pesanan:
    def __init__(self, id_pesanan, pelanggan, menu_list, tanggal_produksi, tanggal_pengiriman, alamat, acara=None, status="Pending"):
        self.id_pesanan = id_pesanan
        self.pelanggan = pelanggan
        
        # Menu_list ini formatnya list of dictionary -> [{"menu_obj": obj, "porsi": 10}, ...]
        # Ini mencakup kebutuhan "Paket Pesanan" (bisa multple menu).
        self.menu_list = menu_list 
        
        self.tanggal_produksi = tanggal_produksi
        self.tanggal_pengiriman = tanggal_pengiriman
        self.alamat = alamat
        self.acara = acara
        self.status = status
        
        self.total_biaya = self.hitung_total()

    def hitung_total(self):
        total = 0
        for item in self.menu_list:
            menu = item['menu_obj']
            porsi = item['porsi']
            total += (menu.hitung_biaya_porsi() * porsi)
        return total

    def get_semua_kebutuhan_bahan(self):
        # Gabungin semua bahan dari semua menu di list pesanan ini
        bahan_total = {}
        for item in self.menu_list:
            bahan_menu = item['menu_obj'].get_daftar_bahan()
            porsi = item['porsi']
            for id_b, qty in bahan_menu.items():
                if id_b in bahan_total:
                    bahan_total[id_b] += (qty * porsi)
                else:
                    bahan_total[id_b] = (qty * porsi)
        return bahan_total

    def is_terlambat(self):
        try:
            tgl_kirim = datetime.strptime(self.tanggal_pengiriman, "%Y-%m-%d")
            sekarang = datetime.now()
            if self.status not in ["Terkirim", "Selesai"] and sekarang > tgl_kirim:
                return True
        except ValueError:
            pass # Kalau format tanggal aneh, lewatin aja
        return False

    def to_dict(self):
        # Buat nyimpen ke json
        menu_simpan = []
        for item in self.menu_list:
            menu_simpan.append({
                "id_menu": item['menu_obj'].id_menu,
                "nama_lengkap": item['menu_obj'].nama,
                "porsi": item['porsi'],
                "biaya_satuan": item['menu_obj'].hitung_biaya_porsi()
            })

        return {
            "id_pesanan": self.id_pesanan,
            "id_pelanggan": self.pelanggan.id_pelanggan,
            "id_acara": self.acara.id_acara if self.acara else None,
            "menu_list": menu_simpan,
            "total_biaya": self.total_biaya,
            "tanggal_produksi": self.tanggal_produksi,
            "tanggal_pengiriman": self.tanggal_pengiriman,
            "alamat": self.alamat,
            "status": self.status
        }

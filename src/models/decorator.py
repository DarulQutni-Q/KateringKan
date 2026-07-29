from src.models.menu import MenuKatering

class MenuDecorator(MenuKatering):
    def __init__(self, menu_dasar: MenuKatering):
        # Narik property dari objek base menu-nya
        super().__init__(
            menu_dasar.id_menu,
            menu_dasar.nama,
            menu_dasar.harga_dasar,
            menu_dasar._resep,
            menu_dasar.stok_porsi
        )
        self.menu_dasar = menu_dasar
        # Override daftar bahan biar pas ditambah dekorator ntar update
        self._daftar_bahan = menu_dasar.get_daftar_bahan().copy()

    def hitung_biaya_porsi(self):
        return self.menu_dasar.hitung_biaya_porsi()
        
    def get_daftar_bahan(self):
        return self._daftar_bahan

# ---- Macam-macam Decorator ----

class OpsiLaukTambahan(MenuDecorator):
    def __init__(self, menu_dasar, id_lauk, jumlah_lauk, harga_lauk, nama_lauk):
        super().__init__(menu_dasar)
        self.id_lauk = id_lauk
        self.jumlah_lauk = jumlah_lauk
        self.harga_lauk = harga_lauk
        self.nama = f"{self.menu_dasar.nama} (+ {nama_lauk})"
        
        # Merge bahan lauk ke daftar bahan menu base
        if self.id_lauk in self._daftar_bahan:
            self._daftar_bahan[self.id_lauk] += self.jumlah_lauk
        else:
            self._daftar_bahan[self.id_lauk] = self.jumlah_lauk

    def hitung_biaya_porsi(self):
        return super().hitung_biaya_porsi() + self.harga_lauk


class OpsiMinuman(MenuDecorator):
    def __init__(self, menu_dasar, harga_minum, nama_minum="Es Teh Manis"):
        super().__init__(menu_dasar)
        self.harga_minum = harga_minum
        self.nama = f"{self.menu_dasar.nama} & {nama_minum}"

    def hitung_biaya_porsi(self):
        return super().hitung_biaya_porsi() + self.harga_minum


class OpsiKemasanPremium(MenuDecorator):
    def __init__(self, menu_dasar):
        super().__init__(menu_dasar)
        self.harga_kemasan = 8000
        self.nama = f"{self.menu_dasar.nama} (Premium Pkg)"

    def hitung_biaya_porsi(self):
        return super().hitung_biaya_porsi() + self.harga_kemasan


class OpsiLayananExpress(MenuDecorator):
    def __init__(self, menu_dasar):
        super().__init__(menu_dasar)
        self.harga_layanan = 15000
        self.nama = f"{self.menu_dasar.nama} [EXPRESS]"

    def hitung_biaya_porsi(self):
        return super().hitung_biaya_porsi() + self.harga_layanan

from abc import ABC, abstractmethod
from src.models.bahan import Resep

class MenuKatering(ABC):
    def __init__(self, id_menu, nama, harga_dasar, resep: Resep, stok_porsi=0):
        self.id_menu = id_menu
        self.nama = nama
        self.harga_dasar = harga_dasar
        
        # Encapsulation 5 konsep wajib
        self._resep = resep  
        self._daftar_bahan = resep.komposisi_bahan.copy() if resep else {}
        self._stok_porsi = stok_porsi

    @property
    def stok_porsi(self):
        return self._stok_porsi

    @stok_porsi.setter
    def stok_porsi(self, nilai):
        if nilai < 0:
            raise ValueError("Stok porsi dilarang minus!")
        self._stok_porsi = nilai
        
    def get_daftar_bahan(self):
        return self._daftar_bahan

    @abstractmethod
    def hitung_biaya_porsi(self):
        """Method wajib buat dioverride di subclass."""
        pass
        
    def to_dict(self):
        return {
            "id_menu": self.id_menu,
            "nama": self.nama,
            "harga_dasar": self.harga_dasar,
            "resep_id": self._resep.id_resep if self._resep else None,
            "daftar_bahan": self._daftar_bahan,
            "stok_porsi": self._stok_porsi,
            "tipe": self.__class__.__name__
        }

class MenuReguler(MenuKatering):
    def hitung_biaya_porsi(self):
        # Harga normal aja
        return float(self.harga_dasar)

class MenuVegetarian(MenuKatering):
    def hitung_biaya_porsi(self):
        # Diskon 5% karena bahan sayur lebih murah
        return float(self.harga_dasar * 0.95)

class MenuBebasGluten(MenuKatering):
    def hitung_biaya_porsi(self):
        # Markup 15% buat bahan gluten free
        return float(self.harga_dasar * 1.15)

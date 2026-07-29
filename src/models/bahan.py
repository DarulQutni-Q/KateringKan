class Bahan:
    def __init__(self, id_bahan, nama, stok, satuan):
        self.id_bahan = id_bahan
        self.nama = nama
        self.stok = stok
        self.satuan = satuan
        
    def kurangi_stok(self, jumlah):
        if self.stok < jumlah:
            raise ValueError(f"Stok {self.nama} kurang bos.")
        self.stok -= jumlah

    def to_dict(self):
        return {
            "id_bahan": self.id_bahan,
            "nama": self.nama,
            "stok": self.stok,
            "satuan": self.satuan
        }

class Resep:
    def __init__(self, id_resep, nama_resep, komposisi_bahan, instruksi):
        self.id_resep = id_resep
        self.nama_resep = nama_resep
        # Format: {id_bahan: jumlah_dibutuhkan}
        self.komposisi_bahan = komposisi_bahan 
        self.instruksi = instruksi

    def to_dict(self):
        return {
            "id_resep": self.id_resep,
            "nama_resep": self.nama_resep,
            "komposisi_bahan": self.komposisi_bahan,
            "instruksi": self.instruksi
        }

class AlergenTerdeteksiError(Exception):
    """Dipicu kalau menu yang dipesan ngandung bahan alergen si pelanggan."""
    def __init__(self, pelanggan, bahan_alergen):
        self.pelanggan = pelanggan
        self.bahan_alergen = bahan_alergen
        pesan = f"Alergi terdeteksi! {pelanggan} alergi sama bahan: {', '.join(bahan_alergen)}"
        super().__init__(pesan)

class BahanProduksiTidakCukupError(Exception):
    """Dipicu pas mau produksi tapi stok bahan di gudang kurang."""
    def __init__(self, bahan_kurang):
        self.bahan_kurang = bahan_kurang
        detail = ", ".join([f"{nama} (kurang {jumlah})" for nama, jumlah in bahan_kurang.items()])
        pesan = f"Stok bahan ga cukup buat produksi: {detail}"
        super().__init__(pesan)

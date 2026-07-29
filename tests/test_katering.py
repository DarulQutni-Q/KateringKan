import unittest
import os
import shutil
from src.models.menu import MenuReguler, MenuVegetarian, MenuBebasGluten
from src.models.bahan import Bahan, Resep
from src.models.decorator import OpsiLaukTambahan, OpsiKemasanPremium, OpsiLayananExpress
from src.models.pesanan import Pelanggan, Pesanan, Acara
from src.services.katering_manager import KateringManager
from src.exceptions import AlergenTerdeteksiError, BahanProduksiTidakCukupError
from src.services.file_handler import FileHandler

class TestKateringApp(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        FileHandler.DATA_DIR = self.test_dir
        
        # Init Manager bakalan langsung bikin dummy data kalo kosong
        self.km = KateringManager()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # 1. Test Polymorphism (Harga Varian)
    def test_polymorphism_harga(self):
        resep_dummy = Resep("R99", "Dummy", {}, "Uji coba")
        reguler = MenuReguler("M01", "Nasi", 10000, resep_dummy)
        vege = MenuVegetarian("M02", "Salad", 10000, resep_dummy)
        gf = MenuBebasGluten("M03", "Ayam GF", 10000, resep_dummy)
        
        self.assertEqual(reguler.hitung_biaya_porsi(), 10000)
        self.assertEqual(vege.hitung_biaya_porsi(), 9500) # Diskon 5%
        self.assertEqual(gf.hitung_biaya_porsi(), 11500) # Markup 15%

    # 2. Test Encapsulation 
    def test_encapsulation_stok_porsi(self):
        resep_dummy = Resep("R99", "Dummy", {}, "Uji")
        menu = MenuReguler("M01", "Nasi", 10000, resep_dummy)
        with self.assertRaises(ValueError):
            menu.stok_porsi = -10 # Setter ga nerima minus

    # 3. Test Pola Desain Decorator - Stack Harga & Bahan
    def test_decorator_berjenjang(self):
        resep_dummy = Resep("R99", "Dummy", {"B01": 100}, "Uji")
        menu_dasar = MenuReguler("M01", "Nasi Biasa", 20000, resep_dummy)
        
        menu_premium = OpsiKemasanPremium(menu_dasar) # +8000
        menu_lauk = OpsiLaukTambahan(menu_premium, "B02", 2, 5000, "Telor") # +5000, B02:2
        menu_express = OpsiLayananExpress(menu_lauk) # +15000
        
        # Total: 20000 + 8000 + 5000 + 15000 = 48000
        self.assertEqual(menu_express.hitung_biaya_porsi(), 48000)
        
        # Bahan harus kecampur B01 dan B02
        bahan = menu_express.get_daftar_bahan()
        self.assertEqual(bahan["B01"], 100)
        self.assertEqual(bahan["B02"], 2)

    # 4. Test Custom Exception: AlergenTerdeteksiError (Skenario Kesalahan 1)
    def test_alergen_terdeteksi(self):
        # P002 alergi B003 (Kacang). R02(M002) punya B003.
        paket = [{"id_menu": "M002", "porsi": 1}]
        with self.assertRaises(AlergenTerdeteksiError):
            self.km.proses_pesanan_baru("P002", paket, "2024-01-01", "2024-01-02", "Jalan A")

    # 5. Test Custom Exception: BahanProduksiTidakCukupError (Skenario Kesalahan 2)
    def test_bahan_tidak_cukup(self):
        # Pesen 5.000 porsi paket. B001 cuma ada 100.000 gram. 5000x200 = 1jt gram (kurang)
        paket = [{"id_menu": "M001", "porsi": 5000}]
        with self.assertRaises(BahanProduksiTidakCukupError):
            self.km.proses_pesanan_baru("P001", paket, "2024-01-01", "2024-01-02", "Jalan A")

    # 6. Test File Handling
    def test_file_handler_baca_tulis(self):
        paket = [{"id_menu": "M001", "porsi": 1}]
        self.km.proses_pesanan_baru("P001", paket, "2024-01-01", "2024-01-02", "Jalan B")
        
        data_pesanan = FileHandler.baca_json('pesanan_katering.json')
        self.assertTrue(len(data_pesanan) > 0)
        self.assertEqual(data_pesanan[0]['id_pelanggan'], "P001")
        
        # Ekspor CSV
        path_csv = self.km.bikin_semua_laporan()
        self.assertTrue(os.path.exists(path_csv))

    # 7. Test Pesanan Paket (Multiple Menu) & Hitung Total Biaya (Skenario Normal)
    def test_pesanan_paket(self):
        paket = [
            {"id_menu": "M001", "porsi": 2}, # 35000 x 2 = 70000
            {"id_menu": "M002", "porsi": 1}  # 20000 x 0.95 = 19000
        ]
        pesanan = self.km.proses_pesanan_baru("P001", paket, "2024-01-01", "2024-01-02", "Rumah")
        self.assertEqual(pesanan.total_biaya, 89000)

    # 8. Test Logika Keterlambatan Pesanan
    def test_pesanan_terlambat(self):
        # Bikin manual pesanan dengan tgl kirim jadul (tahun 2000)
        p = Pesanan("X", self.km.daftar_pelanggan["P001"], [], "2000-01-01", "2000-01-02", "A", status="Pending")
        self.assertTrue(p.is_terlambat())
        
        p.status = "Terkirim" # Kalo terkirim yaudah ga telat itungannya
        self.assertFalse(p.is_terlambat())

if __name__ == '__main__':
    unittest.main()

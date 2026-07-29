import json
import csv
import os
from datetime import datetime

class FileHandler:
    # Cari root folder (JokiDewa) secara dinamis biar aman di cross-platform OS
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, 'data')

    @classmethod
    def pastikan_folder_ada(cls):
        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)

    @classmethod
    def baca_json(cls, nama_file):
        cls.pastikan_folder_ada()
        path = os.path.join(cls.DATA_DIR, nama_file)
        if not os.path.exists(path):
            return []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Gagal baca file {nama_file}. Format rusak.")
            return []
        except Exception as e:
            print(f"Error baca {nama_file}: {e}")
            return []

    @classmethod
    def tulis_json(cls, nama_file, data):
        cls.pastikan_folder_ada()
        path = os.path.join(cls.DATA_DIR, nama_file)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Gagal simpan ke {nama_file}: {e}")

    @classmethod
    def ekspor_laporan_csv(cls, data_laporan):
        cls.pastikan_folder_ada()
        path = os.path.join(cls.DATA_DIR, 'laporan_produksi.csv')
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                if not data_laporan:
                    writer = csv.writer(f)
                    writer.writerow(["Data laporan kosong."])
                    return path
                
                # Header dinamis
                writer = csv.DictWriter(f, fieldnames=data_laporan[0].keys())
                writer.writeheader()
                for row in data_laporan:
                    writer.writerow(row)
            return path
        except Exception as e:
            print(f"Gagal generate CSV: {e}")
            return None

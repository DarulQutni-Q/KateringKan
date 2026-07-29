import sys
import os

# Tambahin root folder ke path biar bisa import dari src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui.app_gui import KateringAppGUI

def jalankan_app():
    print("Mulai inisialisasi aplikasi KateringKU...")
    app = KateringAppGUI()
    print("Membuka GUI...")
    app.mainloop()
    print("Aplikasi ditutup.")

if __name__ == "__main__":
    jalankan_app()

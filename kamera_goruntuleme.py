#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# kamera_goruntuleme.py

import os
import sys
import traceback
from datetime import datetime
import shutil # shutil.which için

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = RESET = ""

TERMUX_API_CMD = "termux-camera-photo"

def check_termux_camera_api():
    """Termux kamera aracının varlığını ve çalıştırılabilirliğini kontrol eder."""
    tool_path = shutil.which(TERMUX_API_CMD)
    if not tool_path:
        print(f"{R}Hata: '{TERMUX_API_CMD}' komutu bulunamadı!{RESET}")
        print(f"{Y}Bu özellik SADECE Termux üzerinde 'termux-api' paketi kuruluysa çalışır.{RESET}")
        print(f"{Y}Lütfen 'pkg install termux-api' komutu ile kurun.{RESET}")
        return False
    # Çalıştırma izni var mı diye kontrol edilebilir ama which bulduysa genelde vardır.
    print(f"{G}Termux kamera aracı bulundu: {tool_path}{RESET}")
    return True

def kamera_cek():
    """Termux API kullanarak fotoğraf çeker."""
    print(f"\n{C}--- Termux Kamera ile Fotoğraf Çekme ---{RESET}")

    # Termux API kontrolü
    if not check_termux_camera_api():
        return # Araç yoksa devam etme

    try:
        # Kullanıcıdan kamera seçimi iste (0: arka, 1: ön)
        # Not: Cihazda ön kamera yoksa veya ID farklıysa hata verebilir.
        cam_id = input(f"{Y}Kullanılacak Kamera ID [0=Arka (varsayılan), 1=Ön]: {RESET}").strip()
        if cam_id not in ['0', '1']:
            print(f"{Y}Varsayılan kamera (ID: 0) kullanılıyor.{RESET}")
            cam_id = '0'

        # Kaydedilecek dosya adı
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dosya_adi = f"termux_kamera_{timestamp}.jpg"

        # Kayıt dizinini belirle (Termux genellikle paylaşılan depolamaya erişebilir)
        # /storage/emulated/0/DCIM gibi bir yer daha uygun olabilir.
        # Ancak basitlik için betiğin çalıştığı yere kaydedelim.
        # Daha iyisi: Kullanıcıdan dizin istemek veya varsayılan bir DCIM yolu denemek.
        kayit_yolu = dosya_adi
        print(f"{C}Fotoğraf '{kayit_yolu}' olarak kaydedilecek...{RESET}")

        # Fotoğraf çekme komutu
        # Komut: termux-camera-photo -c [ID] [DOSYA_YOLU]
        command = [TERMUX_API_CMD, "-c", cam_id, kayit_yolu]

        print(f"{Y}Komut çalıştırılıyor: {' '.join(command)}{RESET}")
        # Komutu çalıştır ve çıktısını bekle
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False, encoding='utf-8') # Timeout ekle

        # Sonucu kontrol et
        if result.returncode == 0:
            # Dosyanın gerçekten oluşup oluşmadığını kontrol et
            if os.path.exists(kayit_yolu):
                print(f"{G}✅ Fotoğraf başarıyla kaydedildi: {kayit_yolu}{RESET}")
                print(f"{G}Dosya boyutu: {os.path.getsize(kayit_yolu)} bytes{RESET}")
            else:
                 print(f"{R}Hata: Komut başarılı görünüyor ancak dosya bulunamadı!{RESET}")
                 print(f"{Y}Stderr: {result.stderr}{RESET}")
        else:
            # Komut hata ile bittiyse
            print(f"{R}Hata: Fotoğraf çekilemedi! (Return Code: {result.returncode}){RESET}")
            print(f"{R}Termux:API hatası veya izin sorunu olabilir.{RESET}")
            print(f"{Y}Stderr: {result.stderr}{RESET}")
            print(f"{Y}İpuçları: Termux için Kamera iznini kontrol edin. Farklı bir Kamera ID (0 veya 1) deneyin.{RESET}")

    except subprocess.TimeoutExpired:
        print(f"{R}Hata: Kamera işlemi zaman aşımına uğradı (30s).{RESET}")
    except FileNotFoundError:
         print(f"{R}Hata: '{TERMUX_API_CMD}' komutu çalıştırılamadı (tekrar kontrol).{RESET}")
    except Exception as e:
        print(f"{R}❌ Beklenmedik bir hata oluştu: {e}{RESET}")
        traceback.print_exc()

if __name__ == "__main__":
    kamera_cek()
    # Ana menüye dönmek için bekleme istemi ana betikte olduğu için burada gerek yok.
    # input("\nAna menüye dönmek için Enter'a basın...")
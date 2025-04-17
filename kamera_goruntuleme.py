#!/usr/bin/env python3
import os
from datetime import datetime

def kamera_cek():
    try:
        dosya_adi = f"kamera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        # Termux API kontrolü
        if not os.path.exists('/data/data/com.termux/files/usr/bin/termux-camera-photo'):
            raise Exception("Termux API yüklü değil!")
        
        # Depolama izni kontrolü
        if not os.path.exists('/storage/emulated/0'):
            raise Exception("Depolama erişimi reddedildi!")
        
        # Fotoğraf çekme
        ret = os.system(f"termux-camera-photo -c 0 {dosya_adi}")
        
        if ret == 0:
            print(f"✅ Fotoğraf kaydedildi: /storage/emulated/0/{dosya_adi}")
        else:
            raise Exception("Kamera erişimi başarısız!")
            
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        print("Çözüm: termux-setup-storage && pkg install termux-api")

if __name__ == "__main__":
    kamera_cek()
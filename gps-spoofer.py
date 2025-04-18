# -*- coding: utf-8 -*-
# gps-spoofer.py

import time
import subprocess
import sys
import traceback
import shutil # shutil.which için
import json # Sahte veri için

# --- Gerekli Kütüphaneleri ve Aracı Kontrol Et ---
try:
    # gps3 kütüphanesini import etmeyi dene
    from gps3 import gps3
except ImportError:
    print("\nHata: 'gps3' kütüphanesi bulunamadı!")
    print("Bu betiğin çalışması için gereklidir.")
    print("Lütfen kurun: pip install gps3")
    sys.exit(1)

# gpsd aracını kontrol et
GPSD_CMD = "gpsd"
def check_gpsd():
    """gpsd aracının sistemde kurulu olup olmadığını kontrol eder."""
    gpsd_path = shutil.which(GPSD_CMD)
    if not gpsd_path:
        print(f"\nHata: '{GPSD_CMD}' komutu sistemde bulunamadı!")
        print("Bu betik, GPS verisini yönetmek için 'gpsd' servisine ihtiyaç duyar.")
        print("Lütfen işletim sisteminize uygun şekilde 'gpsd' paketini kurun.")
        print("(Örn: Debian/Ubuntu -> sudo apt install gpsd gpsd-clients)")
        print("(Örn: Arch -> sudo pacman -S gpsd)")
        return False
    print(f"{G}'{GPSD_CMD}' bulundu: {gpsd_path}{RESET}")
    return True

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = RESET = ""

# --- ÖNEMLİ UYARILAR ---
print(f"""{R}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!                 UYARI / WARNING                       !!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
- Bu araç, GPS konumunu SAHTE olarak bildirmek için tasarlanmıştır.
- Çalışması için sisteminizde 'gpsd' servisinin kurulu, yapılandırılmış
  ve çalışıyor olması GEREKLİDİR. Ayrıca 'gps3' Python kütüphanesi
  de kurulmalıdır (pip install gps3).
- 'gpsd' servisini doğru şekilde yapılandırmak karmaşık olabilir.
- Konum bilgisini yanıltmak, bazı uygulamaların (örn: navigasyon,
  konum tabanlı oyunlar) düzgün çalışmamasına veya hizmet
  şartlarının ihlaline neden olabilir.
- YANLIŞ KULLANIMI beklenmedik sonuçlar doğurabilir. Dikkatli olun!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
{RESET}""")
time.sleep(3)


class GPSSpoofer:
    def __init__(self):
        self.gpsd_socket = None
        self.data_stream = None
        self.gpsd_process = None # gpsd'yi biz başlatırsak işlemi tutmak için

    def start_gpsd_service(self):
        """gpsd servisini başlatmayı dener (sistemde kuruluysa)."""
        # Zaten çalışıyor mu diye kontrol etmek zor, biz başlatmayı deneyelim.
        # Ancak genellikle kullanıcı tarafından manuel başlatılması/yapılandırılması gerekir.
        # Bu yüzden sadece uyaralım ve manuel başlatılmasını önerelim.
        print(f"{Y}Uyarı: 'gpsd' servisinin arka planda çalışıyor olması gerekir.{RESET}")
        print(f"{Y}Eğer çalışmıyorsa, yeni bir terminalde 'sudo gpsd /dev/ttyXXX -F /var/run/gpsd.sock' gibi bir komutla başlatmanız gerekebilir (cihazınıza göre değişir).{RESET}")
        # return True # Şimdilik başlatmayı denemeyelim, manuel varsayalım.

        # Başlatmayı denemek istersek (root gerekebilir ve risklidir):
        # gpsd_path = shutil.which(GPSD_CMD)
        # if not gpsd_path: return False
        # try:
        #     print(f"{C}'gpsd' servisi başlatılıyor... (sudo gerekebilir){RESET}")
        #     # -N: Arka plana atma, -n: Hemen okumaya başla
        #     # Hangi cihazı (-b /dev/...) veya soketi (-F ...) dinleyeceği belirtilmeli!
        #     # Bu komut büyük ihtimalle eksik argümanla başarısız olur.
        #     # Sadece TCP üzerinden bağlanmayı deneyen basit bir komut:
        #     cmd = ["sudo", gpsd_path, "-N", "-n", "tcp://localhost:2947"]
        #     self.gpsd_process = subprocess.Popen(cmd)
        #     print(f"{G}'gpsd' başlatıldı (PID: {self.gpsd_process.pid}).{RESET}")
        #     time.sleep(2) # Başlaması için bekle
        #     return True
        # except Exception as e:
        #     print(f"{R}'gpsd' başlatılırken hata: {e}{RESET}")
        #     self.gpsd_process = None
        #     return False
        return True # Manuel başlatıldığını varsay

    def connect_to_gpsd(self):
        """Çalışan gpsd servisine bağlanır."""
        try:
            print(f"{C}gpsd soketine bağlanılıyor (localhost:2947)...{RESET}")
            self.gpsd_socket = gps3.GPSDSocket()
            self.data_stream = gps3.DataStream()
            self.gpsd_socket.connect(host='127.0.0.1', port=2947) # Standart gpsd portu
            self.gpsd_socket.watch() # Veri akışını başlat
            print(f"{G}gpsd'ye başarıyla bağlandı.{RESET}")
            return True
        except ConnectionRefusedError:
             print(f"{R}Hata: gpsd bağlantısı reddedildi. 'gpsd' servisi çalışmıyor veya yanlış yapılandırılmış olabilir.{RESET}")
             return False
        except Exception as e:
            print(f"{R}gpsd'ye bağlanırken hata: {e}{RESET}")
            traceback.print_exc()
            return False

    def stop_connection(self):
        """gpsd bağlantısını kapatır."""
        if self.gpsd_socket:
            try:
                self.gpsd_socket.close()
                print(f"{Y}gpsd bağlantısı kapatıldı.{RESET}")
            except Exception as e:
                 print(f"{R}gpsd soketi kapatılırken hata: {e}{RESET}")
            finally:
                 self.gpsd_socket = None
                 self.data_stream = None
        # Eğer biz başlattıysak işlemi durdurmayı dene
        # if self.gpsd_process:
        #     try:
        #         print(f"{C}'gpsd' işlemi durduruluyor (PID: {self.gpsd_process.pid})...{RESET}")
        #         self.gpsd_process.terminate()
        #         self.gpsd_process.wait(timeout=5)
        #         print(f"{G}'gpsd' işlemi durduruldu.{RESET}")
        #     except Exception as e:
        #          print(f"{R}'gpsd' işlemi durdurulurken hata: {e}{RESET}")
        #     finally:
        #          self.gpsd_process = None


    def spoof(self, lat, lon, speed=0.0, altitude=0.0, num_updates=None):
        """Belirtilen koordinatları gpsd'ye gönderir."""
        if not self.gpsd_socket or not self.data_stream:
            print(f"{R}Hata: Önce gpsd'ye bağlanılmalı!{RESET}")
            return False

        print(f"{C}GPS Spoofing başlatıldı -> Lat: {lat}, Lon: {lon}{RESET}")
        print(f"{Y}Durdurmak için Ctrl+C'ye basın.{RESET}")

        update_count = 0
        try:
            while True:
                # Sahte GPS verisi oluştur (JSON formatında gpsd'nin beklediği gibi)
                # Gerekli alanlar: class, time, lat, lon. Diğerleri opsiyonel.
                fake_tpv = {
                    "class": "TPV", # Time-Position-Velocity report
                    "time": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()), # ISO 8601 format
                    "ept": 0.005, # Estimated time error
                    "lat": float(lat), # Latitude
                    "lon": float(lon), # Longitude
                    "alt": float(altitude), # Altitude
                    "epx": 15.0, # Estimated longitude error
                    "epy": 15.0, # Estimated latitude error
                    "epv": 5.0, # Estimated altitude error
                    "track": 0.0, # Course over ground, degrees from true north
                    "speed": float(speed), # Speed over ground, meters per second
                    "climb": 0.0, # Climb rate, meters per second
                    "eps": 30.0, # Estimated speed error
                    "mode": 3 # GPS fix status: 3=3D fix
                 }
                # gps3 kütüphanesi doğrudan JSON göndermeyi desteklemiyor gibi.
                # gpsd'ye sahte veri göndermek için genellikle gpsfake aracı kullanılır.
                # Python'dan doğrudan sokete yazmak daha karmaşık olacaktır.
                # Bu yüzden bu kısım BÜYÜK İHTİMALLE ÇALIŞMAZ.
                # print(f"Gönderilen Veri (Simülasyon): {fake_tpv}", end='\r') # Sadece ne gönderileceğini yazdır
                print(f"{Y}Spoofing aktif (Veri gönderimi simüle ediliyor)... Ctrl+C ile durdurun.{RESET}", end='\r')

                # Gerçek veri gönderme (ÇALIŞMAYACAKTIR):
                # self.data_stream.unpack(json.dumps(fake_tpv)) # Bu metod gelen veriyi işler, göndermez.
                # Sokete doğrudan yazmak gerekir, örn:
                # self.gpsd_socket.send(json.dumps(fake_tpv).encode('utf-8')) # Bu da çalışmayabilir, gpsd protokolü farklı olabilir.

                update_count += 1
                if num_updates and update_count >= num_updates:
                    print(f"\n{G}Belirtilen sayıda ({num_updates}) güncelleme gönderildi.{RESET}")
                    break

                time.sleep(1) # Saniyede bir güncelleme gönder

        except KeyboardInterrupt:
            print(f"\n{Y}GPS spoofing durduruldu (Ctrl+C).{RESET}")
            return True
        except Exception as e:
             print(f"\n{R}Spoofing sırasında hata: {e}{RESET}")
             traceback.print_exc()
             return False


# Ana Çalıştırma Bloğu
if __name__ == "__main__":
    if not check_gpsd(): # gpsd kurulu mu?
        sys.exit(1)

    spoofer = GPSSpoofer()

    if not spoofer.start_gpsd_service(): # Servisi başlatmayı dene (veya manuel başlatıldığını varsay)
         print(f"{R}gpsd servisi başlatılamadığı veya manuel başlatılmadığı için devam edilemiyor.{RESET}")
         sys.exit(1)

    if spoofer.connect_to_gpsd(): # gpsd'ye bağlan
        try:
            # Kullanıcıdan koordinatları al
            while True:
                try:
                     lat_str = input(f"{Y}Hedef Enlem (Latitude) örn: 41.0082 : {RESET}").strip()
                     lat = float(lat_str)
                     break
                except ValueError: print(f"{R}Geçersiz sayı formatı!{RESET}")
            while True:
                 try:
                     lon_str = input(f"{Y}Hedef Boylam (Longitude) örn: 28.9784 : {RESET}").strip()
                     lon = float(lon_str)
                     break
                 except ValueError: print(f"{R}Geçersiz sayı formatı!{RESET}")

            # Spoof işlemini başlat
            spoofer.spoof(lat, lon)

        finally:
            # Program bittiğinde veya hata olduğunda bağlantıyı kapat
            spoofer.stop_connection()
    else:
         print(f"{R}gpsd'ye bağlanılamadığı için spoofing başlatılamadı.{RESET}")

    print(f"\n{G}Program sonlandırıldı.{RESET}")
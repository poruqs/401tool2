# -*- coding: utf-8 -*-
# wifipass_breaker.py - DİKKAT: ŞİFRE KIRMA İŞLEMİ SİMÜLASYONDUR!

import os
import subprocess
import sys
import time
import shutil # shutil.which için

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; W = Fore.WHITE; RESET = Style.RESET_ALL
except ImportError:
    print("Uyarı: Renkli çıktılar için 'colorama' kütüphanesi gerekli ('pip install colorama').")
    R = Y = G = C = W = RESET = ""

# --- ÖNEMLİ UYARI ---
print(f"""{R}{Style.BRIGHT}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!                     DİKKAT / WARNING                    !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Bu araç GERÇEK WiFi şifrelerini KIRMAZ!
Şifre kırma bölümü TAMAMEN SİMÜLASYONDUR ve sadece
eğitim/görsel amaçlıdır. Her zaman örnek bir şifre gösterir.

WiFi ağlarını tarama özelliği ise SADECE Termux üzerinde
ve gerekli izinler (Termux:API, Konum vb.) verildiğinde
çalışabilir. Başka platformlarda tarama başarısız olur.

İzinsiz olarak WiFi ağlarına sızmaya çalışmak YASA DIŞIDIR.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
{RESET}""")
time.sleep(5)

# Termux kontrol fonksiyonu
def check_termux_wifi_scan():
    """Termux WiFi tarama aracının varlığını kontrol eder."""
    tool_path = shutil.which("termux-wifi-scaninfo")
    if tool_path:
        print(f"{G}Termux WiFi tarama aracı bulundu: {tool_path}{RESET}")
        return True
    else:
        print(f"{R}Hata: 'termux-wifi-scaninfo' komutu bulunamadı.{RESET}")
        print(f"{Y}WiFi tarama özelliği sadece Termux'ta çalışır.{RESET}")
        print(f"{Y}Termux kullanıyorsanız, 'pkg install termux-api' komutu ile kurun ve gerekli izinleri verin (Konum).{RESET}")
        return False

def print_banner():
    """Menü banner'ını yazdırır."""
    clear_screen()
    print(f"""{C}
    ╔════════════════════════════════════════════╗
    ║        {Y}401HackTeam - WiFi Aracı (Simülasyon){C}        ║
    ╠════════════════════════════════════════════╣
    ║                                            ║
    ║    {G}1. WiFi Ağlarını Tara (Sadece Termux){C}      ║
    ║    {Y}2. Şifre Kırma Simülasyonu Başlat{C}        ║
    ║    {R}3. Çıkış{C}                                ║
    ║                                            ║
    ╚════════════════════════════════════════════╝{RESET}
    """)

def clear_screen():
     os.system('cls' if os.name == 'nt' else 'clear')

def scan_wifi():
    """Termux üzerinde WiFi ağlarını tarar."""
    print(f"\n{C}[+] WiFi Ağları Taranıyor (Sadece Termux)...{RESET}")

    # Termux aracını tekrar kontrol et
    if not check_termux_wifi_scan():
        return None # Tarama yapılamaz

    try:
        # Komutu çalıştır
        result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, timeout=15, check=False, encoding='utf-8')

        if result.returncode != 0:
            print(f"{R}Hata: Tarama komutu çalıştırılamadı.{RESET}")
            print(f"{R}Çıktı:\n{result.stderr}{RESET}")
            print(f"{Y}Termux:API izinlerini (özellikle Konum) kontrol edin.{RESET}")
            return None

        # Çıktıyı işle (genellikle JSON formatında döner)
        # Basitçe satır satır yazdıralım şimdilik
        networks_output = result.stdout.strip()
        if not networks_output:
            print(f"{Y}[-] Hiç WiFi ağı bulunamadı veya tarama sonucu boş.{RESET}")
            return []

        print(f"\n{G}[+] Bulunan WiFi Ağları:{RESET}")
        lines = networks_output.splitlines()
        # Kullanıcının seçmesi için numaralandıralım
        numbered_networks = []
        for i, line in enumerate(lines):
             # Genellikle SSID'yi içeren satırları alalım (basit filtreleme)
             if '"ssid":' in line.lower():
                 # Daha okunabilir hale getirmeye çalışalım
                 try:
                     # JSON parse etmeyi deneyebiliriz ama format değişebilir, basit tutalım
                     ssid_part = line.split('"ssid":')[1].split('"')[1]
                     display_line = f"{Y}[{len(numbered_networks) + 1}] SSID: {ssid_part}{RESET}"
                     print(display_line)
                     numbered_networks.append(ssid_part) # Sadece SSID'yi sakla
                 except IndexError:
                     # SSID parse edilemezse ham satırı göster
                     display_line = f"{Y}[{len(numbered_networks) + 1}] {line.strip()}{RESET}"
                     print(display_line)
                     numbered_networks.append(line.strip()) # Ham satırı sakla
        return numbered_networks

    except subprocess.TimeoutExpired:
        print(f"{R}Hata: WiFi tarama zaman aşımına uğradı (15s).{RESET}")
        return None
    except Exception as e:
        print(f"{R}Tarama sırasında beklenmedik hata: {e}{RESET}")
        return None


def simulate_crack_wifi(network_name):
    """Şifre kırma işlemini SİMÜLE EDER."""
    print(f"\n{R}{Style.BRIGHT}⚠️ UYARI: Bu işlem GERÇEK şifre kırmaz! Sadece bir simülasyondur!{RESET}")
    print(f"\n{Y}[+] '{network_name}' için şifre kırma SİMÜLASYONU başlatılıyor...{RESET}")
    time.sleep(2) # Biraz bekleme ekle
    print(f"{Y}[+] Simülasyon ilerliyor... %10{RESET}", end='\r'); time.sleep(0.5)
    print(f"{Y}[+] Simülasyon ilerliyor... %45{RESET}", end='\r'); time.sleep(0.5)
    print(f"{Y}[+] Simülasyon ilerliyor... %80{RESET}", end='\r'); time.sleep(0.5)
    print(f"{Y}[+] Simülasyon ilerliyor... %100{RESET}")
    time.sleep(1)

    # Her zaman aynı sahte sonucu göster
    print(f"\n{G}[+] Simülasyon Sonucu:{RESET}")
    print(f"{W}WiFi Adı   : {network_name}{RESET}")
    print(f"{R}{Style.BRIGHT}Şifresi    : >> 401HackTeam-Simulasyon << (ÖRNEK - GERÇEK DEĞİL!){RESET}")


def main():
    termux_available = check_termux_wifi_scan() # Başlangıçta kontrol et
    networks = [] # Bulunan ağları saklamak için

    while True:
        print_banner()

        print(f"{W}" + "═"*50 + RESET)
        choice = input(f"{C}\n[?] Seçiminiz (1-3): {RESET}").strip()
        print(f"{W}" + "═"*50 + RESET)

        if choice == "1":
            if termux_available:
                networks = scan_wifi() # Ağları tara ve sakla
                if networks is None: # Tarama hatası olduysa
                    print(f"{R}Tarama başarısız oldu. Menüye dönülüyor.{RESET}")
                elif not networks: # Ağ bulunamadıysa
                     print(f"{Y}Çevrede ağ bulunamadı. Menüye dönülüyor.{RESET}")
            else:
                print(f"{R}Bu özellik sadece Termux üzerinde çalışır.{RESET}")
            input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")

        elif choice == "2":
             # Şifre kırma simülasyonu
             if networks: # Eğer daha önce başarılı bir tarama yapıldıysa
                  print("\n--- Taranan Ağlar ---")
                  for i, net_name in enumerate(networks, 1):
                       print(f"{Y}[{i}] {net_name}{RESET}")
                  print("---------------------")
                  while True:
                       select = input(f"{C}Simülasyon için ağ numarası seçin (veya 'm' manuel giriş): {RESET}").strip()
                       if select.lower() == 'm':
                            target_name = input(f"{C}Manuel ağ adı girin: {RESET}").strip()
                            if target_name: break
                       elif select.isdigit():
                            try:
                                 target_name = networks[int(select) - 1]
                                 break
                            except IndexError:
                                 print(f"{R}Geçersiz numara!{RESET}")
                       else:
                            print(f"{R}Geçersiz giriş.{RESET}")

             else: # Tarama yapılmadıysa veya başarısız olduysa manuel isim iste
                  target_name = input(f"{C}Şifre kırma simülasyonu için hedef ağ adını girin: {RESET}").strip()

             if target_name:
                 simulate_crack_wifi(target_name)
             else:
                 print(f"{R}Ağ adı girilmedi. İşlem iptal edildi.{RESET}")
             input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")

        elif choice == "3":
            print(f"\n{G}Çıkış yapılıyor...{RESET}")
            break

        else:
            print(f"{R}Geçersiz seçim! Lütfen 1, 2 veya 3 girin.{RESET}")
            time.sleep(1.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{G}Program sonlandırıldı.{RESET}")
    except Exception as e:
         print(f"\n{R}Beklenmedik Hata: {e}{RESET}")
         traceback.print_exc()
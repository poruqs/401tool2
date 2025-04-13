# -*- coding: utf-8 -*-
import os
import sys
import socket
import json
import re
import subprocess
import webbrowser
import time
import ipaddress # For IP validation

# Optional Colorama setup
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    BRIGHT = Style.BRIGHT
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    B = Fore.BLUE
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE
    RESET = Style.RESET_ALL
except ImportError:
    BRIGHT = R = G = Y = B = M = C = W = RESET = ""

# --- Configuration ---
BANNER_FILE = os.path.join("files", "banner.txt") # Assumes "files" subdir

# --- Helper Functions ---
def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Prints the banner from the file."""
    try:
        with open(BANNER_FILE, 'r', encoding='utf-8') as f:
            # You might want to add color codes here if the banner file doesn't have them
            print(f"{G}{BRIGHT}{f.read()}{RESET}")
    except FileNotFoundError:
        print(f"{Y}Uyarı: {BANNER_FILE} bulunamadı. Banner gösterilemiyor.{RESET}")
        print(f"{R}{BRIGHT}IPTOOLKIT{RESET}") # Fallback title
    except Exception as e:
        print(f"{R}Banner okunurken hata: {e}{RESET}")

def pause():
    """Pauses execution until Enter is pressed."""
    try:
        input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit()

def validate_ip(ip):
    """Checks if the string is a valid IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        print(f"{R}HATA: Geçersiz IP adresi formatı: {ip}{RESET}")
        return False

def get_ip_input(prompt=" IP Adresi: "):
    """Gets and validates IP address input."""
    while True:
        try:
            ip = input(f"{Y}{prompt}{W}").strip()
            if validate_ip(ip):
                return ip
            # else: continue loop
        except KeyboardInterrupt:
            return None # Indicate cancellation

# --- Tool Functions ---

def geolocate_ip():
    """Gets geolocation data for a public IP using ipinfo.io."""
    clear_screen()
    print(f"{C}{BRIGHT}--- IP Geolocate ---{RESET}\n")
    ip = get_ip_input()
    if ip is None: return # User cancelled

    api_url = f"http://ipinfo.io/{ip}/json"
    print(f"\n{C}API isteği gönderiliyor: {api_url}{RESET}")
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        clear_screen()
        print(f"{C}{BRIGHT}--- Geolocation Sonuçları ({ip}) ---{RESET}\n")
        # Map keys to Turkish or keep original, format nicely
        key_map = {
            "ip":       "IP Adresi",
            "hostname": "Hostname",
            "city":     "Şehir",
            "region":   "Bölge/Eyalet",
            "country":  "Ülke",
            "loc":      "Konum (Lat,Lon)",
            "org":      "ISP/Organizasyon",
            "postal":   "Posta Kodu",
            "timezone": "Zaman Dilimi",
        }
        for key, label in key_map.items():
            value = data.get(key, "N/A") # Get value or N/A if key doesn't exist
            print(f" {Y}{label:<18}:{W} {value}")
        print("\n" + "-"*30)

    except requests.exceptions.Timeout:
        print(f"{R}HATA: API isteği zaman aşımına uğradı.{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{R}HATA: API isteği başarısız: {e}{RESET}")
    except json.JSONDecodeError:
        print(f"{R}HATA: API'den gelen yanıt JSON formatında değil.{RESET}")
    except Exception as e:
        print(f"{R}Beklenmedik bir hata oluştu: {e}{RESET}")
    pause()

def trace_dns():
    """Performs a reverse DNS lookup for an IP."""
    clear_screen()
    print(f"{C}{BRIGHT}--- Reverse DNS Lookup (Trace DNS) ---{RESET}\n")
    ip = get_ip_input()
    if ip is None: return

    print(f"\n{C}Reverse DNS sorgusu yapılıyor: {ip}{RESET}")
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
        clear_screen()
        print(f"{C}{BRIGHT}--- Reverse DNS Sonucu ({ip}) ---{RESET}\n")
        print(f" {Y}{'Hostname:' :<12}{W} {hostname}")
        if aliaslist:
            print(f" {Y}{'Aliases:' :<12}{W} {', '.join(aliaslist)}")
        # print(f" {Y}{'IP Addrs:' :<12}{W} {', '.join(ipaddrlist)}") # Usually same as input IP
    except socket.herror as e:
        print(f"\n{R}HATA: Hostname bulunamadı veya DNS hatası: {e}{RESET}")
    except socket.gaierror as e:
         print(f"\n{R}HATA: Adres çözümleme hatası: {e}{RESET}")
    except Exception as e:
        print(f"\n{R}Beklenmedik bir hata oluştu: {e}{RESET}")
    pause()

def port_scan():
    """Scans specified ports on a target IP."""
    clear_screen()
    print(f"{C}{BRIGHT}--- Port Scan ---{RESET}\n")
    ip = get_ip_input()
    if ip is None: return

    ports_str = input(f"{Y} Taranacak Portlar (örn: 21,22,80,443): {W}").strip()
    ports_to_scan = []
    if not ports_str:
        print(f"{R}HATA: Port girmediniz.{RESET}")
        pause()
        return

    try:
        port_parts = ports_str.split(',')
        for part in port_parts:
            part = part.strip()
            if '-' in part: # Handle port ranges like 80-90
                start, end = map(int, part.split('-'))
                if 1 <= start <= end <= 65535:
                    ports_to_scan.extend(range(start, end + 1))
                else:
                    raise ValueError("Geçersiz port aralığı")
            else: # Handle single ports
                port = int(part)
                if 1 <= port <= 65535:
                    ports_to_scan.append(port)
                else:
                     raise ValueError("Geçersiz port numarası")
        ports_to_scan = sorted(list(set(ports_to_scan))) # Remove duplicates and sort
    except ValueError as e:
        print(f"{R}HATA: Geçersiz port girişi ({e}). Lütfen sayıları virgülle ayırın (örn: 21,22,80-90).{RESET}")
        pause()
        return

    clear_screen()
    print(f"{C}{BRIGHT}--- Port Scan Sonuçları ({ip}) ---{RESET}\n")
    print(f"{C}Tarama başlatıldı ({len(ports_to_scan)} port)...{RESET}")
    open_ports = []
    socket.setdefaulttimeout(0.5) # Bağlantı denemesi için zaman aşımı (saniye)

    for port in ports_to_scan:
        # Progress indicator (optional)
        print(f"\r{C}Denetleniyor: {port:<5}{RESET}", end="")
        sys.stdout.flush()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # result > 0 ise hata, 0 ise başarılı (port açık)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
            # Print open ports as they are found
            print(f"\r{G}AÇIK: {port:<5}{RESET}")
        sock.close()

    # Clear the progress line
    print("\r" + " " * 30 + "\r", end="")

    print(f"\n{C}Tarama tamamlandı.{RESET}")
    if open_ports:
        print(f"{G}Açık Portlar: {', '.join(map(str, open_ports))}{RESET}")
    else:
        print(f"{Y}Taranan portlar arasında açık port bulunamadı.{RESET}")

    pause()

def ddos_links():
    """Displays links to DDoS stresser websites."""
    clear_screen()
    print(f"{R}{BRIGHT}--- DDOS Servisleri (UYARI!) ---{RESET}\n")
    print(f"{Y}UYARI: Bu siteleri kullanmak yasa dışı olabilir ve ciddi sonuçlar doğurabilir.")
    print(f"{Y}Sadece eğitim amaçlıdır ve kullanılması önerilmez.{RESET}\n")

    links = {
        '1': "https://freestresser.so/", # Linkler değişmiş/kapanmış olabilir
        '2': "https://hardstresser.com/",
        '3': "https://stresser.net/",
        '4': "https://str3ssed.co/",
        '5': "https://projectdeltastress.com/"
    }
    for key, url in links.items():
        print(f" {key}) {url}")
    print(f" 6) Geri")
    print("-" * 30)

    try:
        choice = input(" Açmak istediğiniz link (veya 6): ").strip()
        if choice in links:
            print(f"\n{C}{links[choice]} tarayıcıda açılıyor...{RESET}")
            webbrowser.open(links[choice])
        elif choice == '6':
            return # Go back to main menu
        else:
            print(f"{R}Geçersiz seçim.{RESET}")
    except Exception as e:
        print(f"{R}Tarayıcı açılırken hata: {e}{RESET}")
    pause()

def trace_mac_address():
    """Tries to find the MAC address for a local IP using ping and arp."""
    clear_screen()
    print(f"{C}{BRIGHT}--- MAC Adresi Bulma (Yerel Ağ) ---{RESET}\n")
    ip = get_ip_input(" Yerel IP Adresi: ")
    if ip is None: return

    print(f"\n{C}IP adresine ping gönderiliyor: {ip}...{RESET}")
    try:
        # Ping gönder (Windows ve Linux uyumlu) - Yanıtı gizle
        ping_cmd = ['ping', '-n' if os.name == 'nt' else '-c', '1', '-w', '1', ip]
        subprocess.run(ping_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{G}Ping başarılı. ARP tablosu kontrol ediliyor...{RESET}")
        time.sleep(0.5) # ARP tablosunun güncellenmesi için kısa bekleme
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{Y}Uyarı: IP adresine ({ip}) ping gönderilemedi. MAC adresi bulunamayabilir.{RESET}")
        # Yine de ARP kontrolüne devam etmeyi deneyebiliriz

    print(f"{C}ARP tablosu okunuyor...{RESET}")
    mac_address = None
    try:
        # ARP komutunu çalıştır ve çıktısını al
        arp_output = subprocess.check_output(['arp', '-a'], text=True, errors='ignore')
        # print(f"ARP Output:\n{arp_output}\n---") # Debugging için
        # Çıktıyı işle (IP adresiyle eşleşen MAC'i bul)
        # Format platforma göre değişebilir, bu daha genel bir regex
        # Örnek satırlar:
        # Internet Address      Physical Address      Type
        # 192.168.1.1           00-1a-2b-3c-4d-5e     dynamic
        # ? (192.168.1.1) at 00:1a:2b:3c:4d:5e [ether] on eth0
        ip_pattern = re.escape(ip) # IP'yi regex için güvenli hale getir
        # Daha esnek MAC adresi formatları (XX-XX... veya XX:XX...)
        mac_pattern = r"([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}"
        # IP'yi ve MAC'i aynı satırda arayan regex
        match = re.search(rf"{ip_pattern}\D+({mac_pattern})", arp_output, re.IGNORECASE)

        if match:
            mac_address = match.group(1).upper().replace("-", ":") # Formatı standartlaştır
        else:
             print(f"{Y}ARP tablosunda {ip} için eşleşen MAC adresi bulunamadı.{RESET}")

    except FileNotFoundError:
        print(f"{R}HATA: 'arp' komutu bulunamadı. Sisteminizde kurulu olmayabilir.{RESET}")
    except Exception as e:
        print(f"{R}ARP tablosu okunurken hata oluştu: {e}{RESET}")

    if mac_address:
        clear_screen()
        print(f"{C}{BRIGHT}--- MAC Adresi Sonucu ({ip}) ---{RESET}\n")
        print(f" {Y}{'Bulunan MAC Adresi:' :<20}{W} {mac_address}")
    # else: # Hata mesajı zaten yukarıda verildi

    pause()

def arp_spoof_placeholder():
    """Placeholder for ARP Spoof, potentially calling external tool."""
    clear_screen()
    print(f"{R}{BRIGHT}--- ARP Spoof (UYARI!) ---{RESET}\n")
    print(f"{Y}UYARI: ARP Spoofing saldırıları ağ trafiğini aksatabilir ve yasa dışıdır.")
    print(f"{Y}Bu özellik sadece izinli ağlarda test amaçlı kullanılmalıdır.")
    print(f"{Y}Bu Python betiği ARP spoofing yapmaz, ancak varsa 'arpspoof.exe' aracını çağırabilir.")
    print("-" * 30)

    ip = get_ip_input(" Hedef IP Adresi: ")
    if ip is None: return

    arpspoof_exe = "arpspoof.exe" # Or provide full path if needed
    if os.path.exists(os.path.join("files", arpspoof_exe)): # Check in files subdir
         arpspoof_cmd_path = os.path.join("files", arpspoof_exe)
         print(f"\n{C}'{arpspoof_cmd_path} {ip}' komutu yeni pencerede çalıştırılıyor...{RESET}")
         try:
             # Windows'ta yeni bir cmd penceresi açar
             if os.name == 'nt':
                  subprocess.Popen(f'start cmd /c "mode 87, 10 && title Spoofing {ip}... && echo. && cd files && {arpspoof_exe} {ip}"', shell=True)
             else:
                  print(f"{Y}Uyarı: ARP Spoofing için 'start cmd /c' Windows'a özeldir. '{arpspoof_exe}' manuel olarak çalıştırılmalı.{RESET}")
                  # Linux/Mac için Popen farklı kullanılabilir ama arayüz olmaz:
                  # subprocess.Popen([arpspoof_cmd_path, ip])
         except Exception as e:
              print(f"{R}HATA: '{arpspoof_exe}' çalıştırılamadı: {e}{RESET}")
    else:
        print(f"\n{R}HATA: '{arpspoof_exe}' dosyası 'files' klasöründe bulunamadı.{RESET}")
        print(f"{Y}ARP Spoofing yapılamıyor.{RESET}")

    # Batch script gibi hemen menüye döner
    # pause() # İsteğe bağlı olarak burada beklenebilir

def rpc_dump_placeholder():
    """Placeholder for rpcdump functionality."""
    clear_screen()
    print(f"{C}{BRIGHT}--- RPC Dump (Placeholder) ---{RESET}\n")
    print(f"{Y}Bu özellik, orijinal script'teki 'rpcdump' aracını gerektirir.")
    print(f"{Y}Bu Python betiği RPC Dump yapmaz.")
    print("-" * 30)

    ip = get_ip_input()
    if ip is None: return

    rpcdump_exe = "rpcdump" # Or rpcdump.exe, provide full path if needed
    # Check if rpcdump exists (e.g., in files subdir or PATH)
    # This requires knowing the exact name and location
    rpcdump_path = os.path.join("files", rpcdump_exe) # Example check
    can_run = False
    if os.path.exists(rpcdump_path):
        can_run = True
    else:
        # Try checking system PATH (more complex)
        # import shutil
        # if shutil.which(rpcdump_exe):
        #    rpcdump_path = rpcdump_exe # Use command directly if in PATH
        #    can_run = True
        pass # Keep it simple for now

    if can_run:
         print(f"\n{C}'{rpcdump_path} {ip}' komutu çalıştırılıyor...{RESET}")
         try:
              # Run and capture output
              result = subprocess.run([rpcdump_path, ip], capture_output=True, text=True, check=True, timeout=30)
              print(f"{G}--- rpcdump Çıktısı ---{RESET}")
              print(result.stdout if result.stdout else "(Çıktı yok)")
              if result.stderr:
                   print(f"{Y}--- rpcdump Hata Çıktısı ---{RESET}")
                   print(result.stderr)
         except FileNotFoundError:
             print(f"{R}HATA: '{rpcdump_path}' bulunamadı veya çalıştırılamadı.{RESET}")
         except subprocess.CalledProcessError as e:
              print(f"{R}HATA: '{rpcdump_exe}' hata ile sonlandı (Kod: {e.returncode}).{RESET}")
              if e.stdout: print(f"Stdout:\n{e.stdout}")
              if e.stderr: print(f"Stderr:\n{e.stderr}")
         except subprocess.TimeoutExpired:
              print(f"{R}HATA: '{rpcdump_exe}' zaman aşımına uğradı.{RESET}")
         except Exception as e:
              print(f"{R}HATA: '{rpcdump_exe}' çalıştırılırken hata: {e}{RESET}")
    else:
         print(f"\n{R}HATA: '{rpcdump_exe}' yürütülebilir dosyası bulunamadı.{RESET}")
         print(f"{Y}RPC Dump yapılamıyor.{RESET}")

    pause()

# --- Main Execution ---
if __name__ == "__main__":
    # Check dependencies
    try:
        import requests
    except ImportError:
        print(f"{R}HATA: 'requests' kütüphanesi bulunamadı.{RESET}")
        print(f"{Y}Lütfen kurmak için 'pip install requests' komutunu çalıştırın.{RESET}")
        sys.exit(1)

    # Set console title (Platform specific)
    if os.name == 'nt':
        os.system("title IPTOOLKIT")
    else:
        # Linux/Mac uses escape codes
        sys.stdout.write("\x1b]2;IPTOOLKIT\x07")

    # Set console size (Not directly possible in Python stdlib reliably)
    # os.system("mode 75, 30") # Windows only, might fail

    # Change to 'files' directory if needed by external tools
    # if os.path.exists("files"):
    #     try:
    #         os.chdir("files") # Be careful with changing directory
    #         print(f"{C}Çalışma dizini 'files' olarak değiştirildi.{RESET}")
    #     except Exception as e:
    #         print(f"{R}Dizin değiştirilemedi: {e}{RESET}")
    # else:
    #     print(f"{Y}Uyarı: 'files' dizini bulunamadı. Banner ve bazı araçlar çalışmayabilir.{RESET}")


    # Main loop
    while True:
        clear_screen()
        print_banner()
        print("\n")
        print(f"      {W}{BRIGHT}PUBLIC IP{RESET}")
        print(f"      {W}{BRIGHT}---------{RESET}")
        print(f"   {Y}1{W}) Geolocate")
        print(f"   {Y}2{W}) Trace DNS")
        print(f"   {Y}3{W}) Port Scan")
        print(f"   {Y}4{W}) {R}DDOS Links{W} (Uyarı!)") # Add warning color
        print("\n")
        print(f"      {W}{BRIGHT}LOCAL IP{RESET}")
        print(f"      {W}{BRIGHT}----------{RESET}")
        print(f"   {Y}5{W}) Trace Mac Address")
        print(f"   {Y}6{W}) Port Scan")
        print(f"   {Y}7{W}) {R}ARP Spoof{W} (Uyarı!)") # Add warning color
        print(f"   {Y}8{W}) RPC Dump (Placeholder)")
        print("\n")
        print(f"   {R}0{W}) Çıkış")
        print("-" * 35)

        try:
            choice = input(f"{G}{BRIGHT}>> Seçiminiz: {W}")

            if choice == '1':
                geolocate_ip()
            elif choice == '2':
                trace_dns()
            elif choice == '3':
                port_scan() # Public IP için
            elif choice == '4':
                ddos_links()
            elif choice == '5':
                trace_mac_address()
            elif choice == '6':
                port_scan() # Local IP için (aynı fonksiyonu kullanır)
            elif choice == '7':
                arp_spoof_placeholder()
            elif choice == '8':
                rpc_dump_placeholder()
            elif choice == '0':
                print(f"\n{B}Çıkılıyor...{RESET}")
                break
            else:
                print(f"\n{R}Geçersiz seçim.{RESET}")
                time.sleep(1)

        except KeyboardInterrupt:
             print("\nÇıkılıyor...")
             break
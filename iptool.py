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

# --- UYARI ---
# Bu araç çeşitli IP işlemleri (geolocation, port tarama, MAC bulma vb.) yapar.
# Bazı özellikler (ARP Spoof, RPC Dump) harici araçlara bağımlıdır ve sağlanmamıştır.
# MAC adresi bulma ve harici araç çağırma platforma özgü olabilir ve her zaman çalışmayabilir.
# DDoS linkleri bölümündeki siteler tehlikeli olabilir ve kullanılması önerilmez.
# --- UYARI SONU ---

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
    # Fallback if colorama is not installed
    BRIGHT = R = G = Y = B = M = C = W = RESET = ""
    # Define dummy classes to prevent NameError if colorama failed
    class Style: BRIGHT = ""; RESET_ALL = ""
    class Fore: RED = ""; GREEN = ""; YELLOW = ""; BLUE = ""; MAGENTA = ""; CYAN = ""; WHITE = ""

# --- Configuration ---
# NOT: Bu betik, banner göstermek için "files" adlı bir alt klasörde
# "banner.txt" isimli bir dosya arar. Bu dosya sağlanmadığı için banner gösterilmeyecektir.
BANNER_FILE = os.path.join("files", "banner.txt")

# --- Helper Functions ---
def clear_screen():
    """Clears the terminal screen (Windows/Linux/Mac compatible)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Prints the banner from the file if it exists."""
    try:
        # Banner dosyasını UTF-8 olarak okumayı dene
        with open(BANNER_FILE, 'r', encoding='utf-8') as f:
            print(f"{G}{BRIGHT}{f.read()}{RESET}")
    except FileNotFoundError:
        # Dosya yoksa uyarı ver ve basit bir başlık göster
        print(f"{Y}Uyarı: Banner dosyası ({BANNER_FILE}) bulunamadı.{RESET}")
        print(f"\n{R}{BRIGHT}--- IP TOOLKIT ---{RESET}") # Fallback title
    except Exception as e:
        print(f"{R}Banner dosyası okunurken hata oluştu: {e}{RESET}")
        print(f"\n{R}{BRIGHT}--- IP TOOLKIT ---{RESET}") # Fallback title

def pause():
    """Pauses execution until Enter is pressed."""
    try:
        input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit()

def validate_ip(ip):
    """Checks if the string is a valid IP address (v4 or v6)."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Hata mesajını doğrudan get_ip_input içinde verelim
        # print(f"{R}HATA: Geçersiz IP adresi formatı: {ip}{RESET}")
        return False

def get_ip_input(prompt=" IP Adresi: "):
    """Gets and validates IP address input from the user."""
    while True:
        try:
            ip = input(f"{Y}{prompt}{W}").strip()
            if not ip: # Boş girişi kontrol et
                print(f"{R}HATA: IP adresi boş olamaz.{RESET}")
                continue
            if validate_ip(ip):
                return ip
            else:
                # validate_ip False döndürdüyse hata mesajı ver
                 print(f"{R}HATA: Geçersiz IP adresi formatı girildi.{RESET}")
                 # Döngüye devam et
        except KeyboardInterrupt:
            print("\nİşlem iptal edildi.")
            return None # Indicate cancellation

# --- Tool Functions ---

def geolocate_ip():
    """Gets geolocation data for a public IP using ipinfo.io."""
    clear_screen()
    print(f"{C}{BRIGHT}--- IP Geolocate ---{RESET}\n")
    ip = get_ip_input(" Genel IP Adresi: ")
    if ip is None: return # User cancelled

    api_url = f"http://ipinfo.io/{ip}/json"
    print(f"\n{C}API isteği gönderiliyor: {api_url}{RESET}")
    try:
        # requests kütüphanesini burada import edelim (main'de kontrol ediliyor ama yine de)
        import requests
        response = requests.get(api_url, timeout=15) # Timeout artırıldı
        response.raise_for_status() # Hatalı durum kodları için exception fırlat (örn. 404, 429)
        data = response.json()

        clear_screen()
        print(f"{C}{BRIGHT}--- Geolocation Sonuçları ({ip}) ---{RESET}\n")
        # Anahtarları Türkçeleştirilmiş bir harita ile gösterelim
        key_map = {
            "ip":       "IP Adresi",
            "hostname": "Hostname",
            "city":     "Şehir",
            "region":   "Bölge/Eyalet",
            "country":  "Ülke",
            "loc":      "Konum (Enlem,Boylam)",
            "org":      "ISP/Organizasyon",
            "postal":   "Posta Kodu",
            "timezone": "Zaman Dilimi",
        }
        for key, label in key_map.items():
            # API yanıtında anahtar yoksa "N/A" göster
            value = data.get(key, "N/A")
            print(f" {Y}{label:<18}:{W} {value}")

        # Haritada göstermek için Google Maps linki (isteğe bağlı)
        if 'loc' in data and data['loc'] != "N/A":
            try:
                lat, lon = data['loc'].split(',')
                # Google Maps URL formatını güncelleyelim
                maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                print(f" {Y}{'Harita Linki':<18}:{W} {maps_url}")
            except:
                 pass # Konum formatı beklenenden farklıysa hata verme

        print("\n" + "-"*40)

    except requests.exceptions.Timeout:
        print(f"{R}HATA: API isteği zaman aşımına uğradı.{RESET}")
    except requests.exceptions.HTTPError as e:
         # 4xx veya 5xx hatalarını yakala (örn. 429 Too Many Requests)
         print(f"{R}HATA: API'den HTTP hatası alındı: {e}{RESET}")
         if e.response.status_code == 429:
              print(f"{Y}Çok fazla istek gönderilmiş olabilir. Bir süre bekleyip tekrar deneyin.{RESET}")
    except requests.exceptions.RequestException as e:
        # Diğer bağlantı veya istek hataları
        print(f"{R}HATA: API isteği başarısız oldu: {e}{RESET}")
    except json.JSONDecodeError:
        print(f"{R}HATA: API'den gelen yanıt JSON formatında değil.{RESET}")
        # print(f"{Y}Yanıt: {response.text[:200]}{RESET}") # Hata ayıklama için
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
            # Hostname zaten aliaslist içinde olabilir, tekrar etmemek için kontrol
            unique_aliases = [a for a in aliaslist if a != hostname]
            if unique_aliases:
                 print(f" {Y}{'Aliases:' :<12}{W} {', '.join(unique_aliases)}")
        # Genellikle sorgulanan IP döner, yazdırmaya gerek yok
        # print(f" {Y}{'IP Addrs:' :<12}{W} {', '.join(ipaddrlist)}")
        print("\n" + "-"*40)
    except socket.herror as e:
        # Host bulunamadığında veya başka DNS hatası
        print(f"\n{R}HATA: Hostname bulunamadı veya DNS hatası: {e}{RESET}")
    except socket.gaierror as e:
         # Adresle ilgili genel hata (örn. geçersiz IP formatı - get_ip_input yakalamalı)
         print(f"\n{R}HATA: Adres çözümleme hatası: {e}{RESET}")
    except Exception as e:
        print(f"\n{R}Beklenmedik bir hata oluştu: {e}{RESET}")
    pause()

def port_scan():
    """Scans specified ports on a target IP."""
    clear_screen()
    print(f"{C}{BRIGHT}--- Port Scan ---{RESET}\n")
    ip = get_ip_input(" Hedef IP Adresi: ")
    if ip is None: return

    ports_str = input(f"{Y} Taranacak Portlar (örn: 21,22,80,443,1000-1024): {W}").strip()
    ports_to_scan = []
    if not ports_str:
        print(f"{R}HATA: Port listesi boş olamaz.{RESET}")
        pause()
        return

    # Port girdisini işle (tek portlar ve aralıklar)
    try:
        port_parts = ports_str.split(',')
        for part in port_parts:
            part = part.strip()
            if '-' in part: # Port aralığı (örn: 80-90)
                start_end = part.split('-')
                if len(start_end) == 2:
                    start, end = map(int, start_end)
                    if 1 <= start <= end <= 65535:
                        ports_to_scan.extend(range(start, end + 1))
                    else:
                        raise ValueError(f"Geçersiz port aralığı: {part}")
                else:
                    raise ValueError(f"Geçersiz aralık formatı: {part}")
            else: # Tek port
                port = int(part)
                if 1 <= port <= 65535:
                    ports_to_scan.append(port)
                else:
                     raise ValueError(f"Geçersiz port numarası: {port}")
        # Tekrarları kaldır ve sırala
        ports_to_scan = sorted(list(set(ports_to_scan)))
        if not ports_to_scan: # Eğer sadece geçersiz girişler varsa
             raise ValueError("Geçerli port bulunamadı")
    except ValueError as e:
        print(f"{R}HATA: Geçersiz port girişi - {e}. Lütfen sayıları virgülle ayırın (örn: 21,22,80-90).{RESET}")
        pause()
        return
    except Exception as e: # Genel hata yakalama (örn. map(int,...) için harf girilirse)
        print(f"{R}HATA: Portlar işlenirken hata oluştu: {e}.{RESET}")
        pause()
        return

    clear_screen()
    print(f"{C}{BRIGHT}--- Port Scan Sonuçları ({ip}) ---{RESET}\n")
    print(f"{C}Tarama başlatıldı ({len(ports_to_scan)} port)...{RESET}")
    open_ports = []
    closed_ports_count = 0
    # Bağlantı denemesi için varsayılan zaman aşımı (saniye)
    connection_timeout = 0.5
    socket.setdefaulttimeout(connection_timeout)

    # Taramayı başlat
    start_time = time.time()
    try:
        for i, port in enumerate(ports_to_scan):
            # İlerleme durumu göstergesi (isteğe bağlı)
            progress = (i + 1) / len(ports_to_scan) * 100
            print(f"\r{C}Denetleniyor: {port:<5} ({progress:.1f}%) - Açık: {len(open_ports)}{RESET}", end="")
            sys.stdout.flush()

            # Yeni soket oluştur
            # AF_INET for IPv4, SOCK_STREAM for TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Bağlantı denemesi (connect_ex hata yerine kod döndürür)
            # result == 0 ise port açık
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
                # Açık port bulunduğunda hemen yazdırabiliriz (isteğe bağlı)
                # print(f"\r{G}AÇIK: {port:<5}{' ' * 20}{RESET}") # Önceki satırı temizle
            else:
                closed_ports_count += 1
            sock.close()
    except KeyboardInterrupt:
        print("\nTarama kullanıcı tarafından iptal edildi.")
    except Exception as e:
        print(f"\n{R}Tarama sırasında hata oluştu: {e}{RESET}")
    finally:
        end_time = time.time()
        # İlerleme satırını temizle
        print("\r" + " " * 60 + "\r", end="")

    # Sonuçları yazdır
    print(f"\n{C}Tarama tamamlandı ({end_time - start_time:.2f} saniye).{RESET}")
    if open_ports:
        print(f"{G}Açık Portlar ({len(open_ports)} adet): {', '.join(map(str, open_ports))}{RESET}")
    else:
        print(f"{Y}Taranan portlar arasında açık port bulunamadı ({closed_ports_count} kapalı).{RESET}")

    pause()

def ddos_links():
    """Displays links to DDoS stresser websites (USE WITH EXTREME CAUTION)."""
    clear_screen()
    print(f"{R}{BRIGHT}--- DDOS Servisleri (ÇOK DİKKATLİ KULLANIN!) ---{RESET}\n")
    print(f"{R}{BRIGHT}UYARI: Bu siteleri veya benzerlerini kullanmak çoğu ülkede YASA DIŞIDIR!{RESET}")
    print(f"{R}{BRIGHT}Bu tür servisler genellikle dolandırıcılık amaçlıdır veya yasa dışı faaliyetler için kullanılır.{RESET}")
    print(f"{Y}Bu linkler yalnızca eğitim ve farkındalık amacıyla listelenmiştir, KULLANILMASI KESİNLİKLE ÖNERİLMEZ.{RESET}\n")

    # NOT: Bu linkler büyük ihtimalle ölüdür veya tehlikelidir.
    links = {
        '1': "https://freestresser.so/",
        '2': "https://hardstresser.com/",
        '3': "https://stresser.net/",
        '4': "https://str3ssed.co/",
        '5': "https://projectdeltastress.com/"
    }
    for key, url in links.items():
        print(f" {key}) {url} {R}(Tehlikeli olabilir!){RESET}")
    print(f"\n 6) Geri")
    print("-" * 40)

    try:
        choice = input(" Açmak istediğiniz link numarası (veya 6): ").strip()
        if choice in links:
            chosen_url = links[choice]
            print(f"\n{R}UYARI:{Y} '{chosen_url}' adresini açmak üzeresiniz.")
            confirm = input("Bu riskli siteyi gerçekten açmak istiyor musunuz? (e/H): ").strip().lower()
            if confirm == 'e':
                print(f"\n{C}Tarayıcıda açılıyor: {chosen_url}{RESET}")
                webbrowser.open(chosen_url)
            else:
                print("İşlem iptal edildi.")
        elif choice == '6':
            return # Go back to main menu
        else:
            print(f"{R}Geçersiz seçim.{RESET}")
    except Exception as e:
        print(f"{R}Tarayıcı açılırken veya girdi alınırken hata: {e}{RESET}")
    pause()

def trace_mac_address():
    """Tries to find the MAC address for a local IP using ping and arp."""
    clear_screen()
    print(f"{C}{BRIGHT}--- MAC Adresi Bulma (Yerel Ağ) ---{RESET}\n")
    # Sadece özel IP adreslerini kabul etmek daha mantıklı olabilir
    # (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    ip = get_ip_input(" Yerel IP Adresi (örn: 192.168.1.x): ")
    if ip is None: return

    # Girilen IP'nin yerel ağda olup olmadığını kontrol et (isteğe bağlı)
    try:
         ip_obj = ipaddress.ip_address(ip)
         if not ip_obj.is_private:
              print(f"{Y}Uyarı: Girilen IP ({ip}) özel bir ağ adresi değil. MAC adresi bulma genellikle sadece yerel ağda çalışır.{RESET}")
              cont = input("Yine de devam etmek istiyor musunuz? (e/H): ").strip().lower()
              if cont != 'e': return
    except ValueError:
         # Zaten get_ip_input kontrol ediyor ama yine de ekleyelim
         print(f"{R}HATA: IP adresi kontrolü başarısız.{RESET}")
         pause()
         return

    print(f"\n{C}IP adresine ping gönderiliyor ({ip})...{RESET}")
    ping_success = False
    try:
        # Ping gönder (Windows ve Linux/Mac uyumlu) - Çıktıyı gizle
        # Timeout değerini belirle
        timeout_sec = 1 # Saniye cinsinden
        ping_cmd = ['ping']
        if os.name == 'nt': # Windows
            ping_cmd.extend(['-n', '1', '-w', str(timeout_sec * 1000), ip]) # -w milisaniye bekler
        else: # Linux/Mac
            ping_cmd.extend(['-c', '1', '-W', str(timeout_sec), ip]) # -W saniye bekler

        # stderr=subprocess.DEVNULL: Hataları da gizle (örn. 'Destination host unreachable')
        subprocess.run(ping_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout_sec + 1) # Komut zaman aşımı
        print(f"{G}Ping başarılı. ARP tablosu kontrol ediliyor...{RESET}")
        ping_success = True
        time.sleep(0.5) # ARP tablosunun güncellenmesi için kısa bekleme
    except subprocess.TimeoutExpired:
         print(f"{Y}Uyarı: Ping isteği zaman aşımına uğradı ({ip}).{RESET}")
    except subprocess.CalledProcessError:
        # Ping komutu hata kodu döndürdü (örn. host unreachable)
        print(f"{Y}Uyarı: IP adresine ({ip}) ping gönderilemedi (Yanıt alınamadı veya host bulunamadı).{RESET}")
    except FileNotFoundError:
         # Ping komutu sistemde bulunamadı
         print(f"{R}HATA: 'ping' komutu bulunamadı. Sistem PATH'inizi kontrol edin.{RESET}")
    except Exception as e:
         print(f"{R}Ping gönderilirken beklenmedik hata: {e}{RESET}")

    # Ping başarısız olsa bile ARP tablosunu kontrol etmeyi dene
    print(f"{C}ARP tablosu okunuyor...{RESET}")
    mac_address = None
    try:
        # ARP komutunu çalıştır ve çıktısını al (encoding hatalarını yoksay)
        # Önce IP'ye özel sorgu yapmayı dene
        arp_cmd_specific = ['arp']
        if os.name == 'nt':
             arp_cmd_specific.extend(['-a', ip])
        else: # Linux/Mac
             arp_cmd_specific.extend(['-n', ip])

        try:
            arp_output = subprocess.check_output(arp_cmd_specific, text=True, errors='ignore', timeout=5)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
             # Belirli IP için sonuç yoksa veya hata/timeout olursa, tüm tabloyu çek
             print(f"{Y}'arp -a/n {ip}' ile sonuç bulunamadı/hata alındı, tüm ARP tablosu taranıyor...{RESET}")
             arp_cmd_all = ['arp', '-a'] if os.name == 'nt' else ['arp', '-n']
             arp_output = subprocess.check_output(arp_cmd_all, text=True, errors='ignore', timeout=5)

        # print(f"ARP Çıktısı:\n{arp_output}\n---") # Debugging için

        # MAC adresi formatlarını arayan regex (XX-XX... veya XX:XX...)
        mac_pattern = r"([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}"
        # IP adresiyle MAC adresini aynı satırda veya yakınında ara
        ip_pattern = re.escape(ip).replace('.', r'\.') # IP'yi regex için güvenli hale getir

        # ARP çıktısını satır satır işle
        found_mac = None
        for line in arp_output.splitlines():
            # Hem IP hem MAC aynı satırda mı diye bak
            if re.search(ip_pattern, line): # Önce IP'yi bul
                mac_match = re.search(mac_pattern, line) # Sonra MAC'i ara
                if mac_match:
                    found_mac = mac_match.group(0).upper().replace("-", ":")
                    break # İlk eşleşmeyi al ve çık

        if found_mac:
            mac_address = found_mac
        else:
            print(f"{Y}ARP tablosunda {ip} için eşleşen MAC adresi bulunamadı.{RESET}")
            if not ping_success:
                 print(f"{Y}(Ping başarısız olduğu için bu beklenen bir durum olabilir){RESET}")

    except FileNotFoundError:
        print(f"{R}HATA: 'arp' komutu bulunamadı. Sisteminizde kurulu olmayabilir.{RESET}")
    except subprocess.TimeoutExpired:
         print(f"{R}HATA: 'arp' komutu zaman aşımına uğradı.{RESET}")
    except Exception as e:
        print(f"{R}ARP tablosu okunurken veya işlenirken hata oluştu: {e}{RESET}")

    # Sonucu göster (Ekranı tekrar temizlemeye gerek yok, zaten başta temizlenmişti)
    # clear_screen()
    print(f"\n{C}{BRIGHT}--- MAC Adresi Sonucu ({ip}) ---{RESET}\n")
    if mac_address:
        print(f" {G}{'Bulunan MAC Adresi:' :<20}{W} {mac_address}")
    else:
        print(f" {R}MAC Adresi bulunamadı.{RESET}")
    print("\n" + "-"*40)
    pause()

def arp_spoof_placeholder():
    """Placeholder for ARP Spoof, attempting to call an external tool."""
    clear_screen()
    print(f"{R}{BRIGHT}--- ARP Spoof (DİKKAT! Harici Araç Gerekli) ---{RESET}\n")
    print(f"{R}{BRIGHT}UYARI: ARP Spoofing saldırıları ağ trafiğini aksatabilir ve çoğu yerde yasa dışıdır.{RESET}")
    print(f"{Y}Bu özellik yalnızca izinli ağlarda, eğitim ve test amaçlı kullanılmalıdır.")
    print(f"{Y}Bu Python betiği ARP spoofing yapmaz, ancak 'files' klasöründe varsa")
    print(f"{Y}'arpspoof.exe' (Windows) veya 'arpspoof' (Linux) gibi bir aracı çağırmayı dener.{RESET}")
    print(f"{Y}Bu araçların ayrıca kurulmuş olması gerekir (örn: 'dsniff' paketi Linux için).{RESET}")
    print("-" * 60)

    target_ip = get_ip_input(" Hedef IP Adresi: ")
    if target_ip is None: return

    # Gateway IP'sini de sormak genellikle gereklidir
    gateway_ip = get_ip_input(" Ağ Geçidi (Gateway) IP Adresi: ")
    if gateway_ip is None: return

    # Harici aracın adı ve yolu (varsayılan olarak 'files' klasöründe aranır)
    tool_name = "arpspoof.exe" if os.name == 'nt' else "arpspoof"
    tool_path_files = os.path.join("files", tool_name)
    tool_path_system = None # Sistem PATH'indeki yolu tutmak için

    # Önce 'files' klasörünü kontrol et
    if os.path.exists(tool_path_files):
        tool_path_system = tool_path_files
        print(f"{C}Bilgi: '{tool_name}' aracı 'files' klasöründe bulundu.{RESET}")
    else:
        # Sistem PATH'ini kontrol etmeyi dene
        try:
            check_cmd = ['where'] if os.name == 'nt' else ['which']
            result = subprocess.run(check_cmd + [tool_name], capture_output=True, text=True, check=True, timeout=5)
            tool_path_system = result.stdout.strip().splitlines()[0]
            print(f"{C}Bilgi: '{tool_name}' aracı sistem PATH'inde bulundu: {tool_path_system}{RESET}")
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # 'where'/'which' komutu yoksa veya araç bulunamazsa
            print(f"{R}HATA: '{tool_name}' aracı 'files' klasöründe veya sistem PATH'inde bulunamadı.{RESET}")
            print(f"{Y}Lütfen aracı kurun (örn: Linux için 'sudo apt install dsniff') veya 'files' klasörüne kopyalayın.{RESET}")
            pause()
            return # Araç bulunamadıysa devam etme

    # Aracı çalıştırma (Platforma özgü)
    if tool_path_system:
         if os.name == 'nt':
              # Windows'ta yeni pencerede çalıştır
              # Komut genellikle 'arpspoof -t <hedefIP> <GatewayIP>' şeklinde olur.
              command_to_run = f'start cmd /k "{tool_path_system} -t {target_ip} {gateway_ip}"' # /k pencereyi açık tutar
              print(f"\n{C}Windows komutu yeni pencerede çalıştırılıyor:\n  {command_to_run}{RESET}")
              try:
                   subprocess.Popen(command_to_run, shell=True)
                   print(f"{Y}Yeni bir komut istemcisi penceresi açılmış olmalı.{RESET}")
              except Exception as e:
                   print(f"{R}HATA: '{tool_name}' aracı yeni pencerede çalıştırılamadı: {e}{RESET}")
         else:
              # Linux/Mac için
              # Arayüzü (-i) belirtmek genellikle gereklidir. Kullanıcıdan isteyelim.
              interface = input(f"{Y} Kullanılacak Ağ Arayüzü (örn: eth0, wlan0): {W}").strip()
              if not interface:
                   print(f"{R}HATA: Ağ arayüzü belirtilmedi.{RESET}")
              else:
                   # Komutu doğrudan terminalde çalıştırmayı önerelim (sudo gerektirir)
                   command_str = f"sudo {tool_path_system} -i {interface} -t {target_ip} {gateway_ip}"
                   print(f"\n{Y}ARP Spoofing'i başlatmak için aşağıdaki komutu ayrı bir terminalde çalıştırmanız önerilir:")
                   print(f"{C}{command_str}{RESET}")
                   # İsteğe bağlı olarak burada çalıştırmayı deneyebiliriz ama interaktif olmayabilir
                   # try:
                   #     print(f"\n{C}Komut çalıştırılıyor (Ctrl+C ile durdurun): {command_str}{RESET}")
                   #     subprocess.run(['sudo', tool_path_system, '-i', interface, '-t', target_ip, gateway_ip], check=True)
                   # except Exception as e:
                   #     print(f"{R}HATA: '{tool_name}' çalıştırılamadı: {e}{RESET}")

    # Bu fonksiyon genellikle hemen menüye döner.
    pause()

def rpc_dump_placeholder():
    """Placeholder for rpcdump functionality, attempting to call external tool."""
    clear_screen()
    print(f"{C}{BRIGHT}--- RPC Dump (Harici Araç Gerekli) ---{RESET}\n")
    print(f"{Y}Bu özellik, Windows sistemlerdeki RPC endpoint'lerini listelemek için")
    print(f"{Y}genellikle 'rpcdump.exe' (Sysinternals veya benzeri) veya Linux'ta Impacket'in")
    print(f"{Y}'rpcdump.py' betiğini kullanır. Bu Python betiği RPC Dump yapmaz.")
    print(f"{Y}Ancak 'files' klasöründe veya sistem PATH'inde varsa aracı çağırmayı dener.{RESET}")
    print("-" * 60)

    ip = get_ip_input(" Hedef IP Adresi: ")
    if ip is None: return

    # Harici aracın adı ve yolu
    tool_name = "rpcdump.exe" if os.name == 'nt' else "rpcdump.py" # Linux için impacket varsayalım
    tool_path_files = os.path.join("files", tool_name)
    tool_path_system = None
    is_python_script = tool_name.endswith(".py") # Linux aracı python betiği mi?

    # Önce 'files' klasörünü kontrol et
    if os.path.exists(tool_path_files):
        tool_path_system = tool_path_files
        print(f"{C}Bilgi: '{tool_name}' aracı 'files' klasöründe bulundu.{RESET}")
    else:
        # Sistem PATH'ini kontrol etmeyi dene
        try:
            check_cmd = ['where'] if os.name == 'nt' else ['which']
            # Eğer python betiği ise doğrudan which/where çalışmayabilir, genel rpcdump arayalım
            search_name = "rpcdump" if os.name != 'nt' and not is_python_script else tool_name
            result = subprocess.run(check_cmd + [search_name], capture_output=True, text=True, check=True, timeout=5)
            tool_path_system = result.stdout.strip().splitlines()[0]
            print(f"{C}Bilgi: '{search_name}' aracı sistem PATH'inde bulundu: {tool_path_system}{RESET}")
            # Eğer bulunan rpcdump.py değilse ve biz .py bekliyorsak uyarı ver
            if os.name != 'nt' and is_python_script and not tool_path_system.endswith(".py"):
                 print(f"{Y}Uyarı: Sistemde bulunan '{tool_path_system}' beklenen Python betiği olmayabilir.{RESET}")
                 tool_path_system = None # Emin değilsek çalıştırmayalım
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # Araç bulunamadı
            print(f"{R}HATA: '{tool_name}' (veya 'rpcdump') 'files' klasöründe veya sistem PATH'inde bulunamadı.{RESET}")
            print(f"{Y}Lütfen aracı kurun (örn: Windows için Sysinternals, Linux için 'impacket-scripts') veya 'files' klasörüne kopyalayın.{RESET}")
            pause()
            return

    if tool_path_system:
         # Komutu oluştur
         command = []
         if is_python_script and os.name != 'nt':
             command.extend([sys.executable, tool_path_system, ip]) # rpcdump.py IP
         elif os.name == 'nt':
              command.extend([tool_path_system, '/s', ip]) # rpcdump.exe /s IP
         else: # Diğer rpcdump varyantları için varsayım
             command.append(ip)

         print(f"\n{C}Komut çalıştırılıyor: {' '.join(command)}{RESET}")
         try:
              # Komutu çalıştır ve çıktısını yakala
              result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60, errors='ignore')
              clear_screen()
              print(f"{G}{BRIGHT}--- rpcdump Çıktısı ({ip}) ---{RESET}")
              print(result.stdout if result.stdout else "(Çıktı yok)")
              # Hata çıktısı varsa onu da göster
              if result.stderr:
                   print(f"{Y}{BRIGHT}--- rpcdump Hata Çıktısı ---{RESET}")
                   print(result.stderr)
         except FileNotFoundError:
             # sys.executable bulunamazsa (çok nadir) veya tool_path_system geçersizse
             print(f"{R}HATA: '{command[0]}' bulunamadı veya çalıştırılamadı.{RESET}")
         except subprocess.CalledProcessError as e:
              # Komut sıfır olmayan bir kodla biterse (genellikle hata)
              print(f"{R}HATA: '{tool_name}' hata ile sonlandı (Kod: {e.returncode}).{RESET}")
              # Hata durumunda stdout ve stderr'yi yazdırmak faydalı olabilir
              if e.stdout: print(f"{Y}Stdout:\n{e.stdout}{RESET}")
              if e.stderr: print(f"{R}Stderr:\n{e.stderr}{RESET}")
         except subprocess.TimeoutExpired:
              print(f"{R}HATA: '{tool_name}' komutu zaman aşımına uğradı.{RESET}")
         except Exception as e:
              print(f"{R}HATA: '{tool_name}' çalıştırılırken hata: {e}{RESET}")

    pause()

# --- Main Execution ---
if __name__ == "__main__":
    # Gerekli temel kütüphaneleri kontrol et
    try:
        import requests # geolocate_ip için
    except ImportError:
        print(f"{R}HATA: 'requests' kütüphanesi bulunamadı.{RESET}")
        print(f"{Y}Lütfen kurmak için 'pip install requests' komutunu çalıştırın.{RESET}")
        sys.exit(1)
    try:
         import ipaddress # IP doğrulaması için
    except ImportError:
         print(f"{R}HATA: 'ipaddress' kütüphanesi bulunamadı.{RESET}")
         print(f"{Y}Python sürümünüzü kontrol edin (3.3+ gereklidir) veya 'pip install ipaddress' deneyin.{RESET}")
         sys.exit(1)

    # Konsol başlığını ayarla (işletim sistemine özgü)
    title = "IPTOOLKIT by 401"
    if os.name == 'nt':
        os.system(f"title {title}")
    else:
        # Linux/Mac için escape kodu
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()

    # Ana menü döngüsü
    while True:
        clear_screen()
        print_banner() # Banner (veya fallback başlık) yazdırılır
        print("\n")
        # Güncellenmiş Menü Başlıkları ve Seçenekleri
        print(f"      {W}{BRIGHT}GENEL (PUBLIC) IP İŞLEMLERİ{RESET}")
        print(f"      {W}{BRIGHT}---------------------------{RESET}")
        print(f"   {Y}1{W}) Geolocate          {C}(IP Konum Bilgisi){W}")
        print(f"   {Y}2{W}) Trace DNS          {C}(Hostname Bulma){W}")
        print(f"   {Y}3{W}) Port Scan          {C}(Açık Port Tarama){W}")
        print(f"   {Y}4{W}) {R}DDOS Links{W}         {R}(Servis Linkleri - Riskli!){W}")
        print("\n")
        print(f"      {W}{BRIGHT}YEREL (LOCAL) IP İŞLEMLERİ{RESET}")
        print(f"      {W}{BRIGHT}--------------------------{RESET}")
        print(f"   {Y}5{W}) Trace Mac Address  {C}(Yerel MAC Adresi Bulma){W}")
        print(f"   {Y}6{W}) Port Scan          {C}(Açık Port Tarama){W}") # Aynı işlem, yerel IP için
        print(f"   {Y}7{W}) {R}ARP Spoof{W}          {R}(ARP Zehirleme - Harici Araç!){W}")
        print(f"   {Y}8{W}) RPC Dump           {Y}(RPC Bilgisi - Harici Araç!){W}")
        print("\n")
        print(f"   {R}0{W}) Çıkış")
        print("-" * 50) # Ayırıcı çizgi

        try:
            choice = input(f"{G}{BRIGHT}>> Seçiminiz: {W}")

            # Seçimleri ilgili fonksiyonlara yönlendir
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
                break # Döngüden çık
            else:
                # Geçersiz seçim durumunda uyarı ver
                print(f"\n{R}Geçersiz seçim. Lütfen menüdeki numaralardan birini girin.{RESET}")
                time.sleep(1.5) # Kullanıcının mesajı görmesi için kısa bekleme

        except KeyboardInterrupt:
             # Ana menüde Ctrl+C yapılırsa
             print("\nÇıkış yapılıyor...")
             break # Döngüden çık
        except Exception as e:
             # Ana döngüde beklenmedik hata olursa yakala ve göster
             print(f"\n{R}{BRIGHT}ANA DÖNGÜ HATASI: {e}{RESET}")
             import traceback
             traceback.print_exc() # Hatanın detayını yazdır
             pause() # Kullanıcının hatayı görmesi için bekle
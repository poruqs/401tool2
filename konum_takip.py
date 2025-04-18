#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# konum_takip.py

import os
import json
import sys
import traceback
import socket # IP format kontrolü için
from datetime import datetime
import shutil # shutil.which için

# requests kütüphanesini kontrol et
try:
    import requests
except ImportError:
    print("Hata: 'requests' kütüphanesi bulunamadı.")
    print("Lütfen kurun: pip install requests")
    # sys.exit(1) # IP kısmı çalışmayacak ama yerel kısım çalışabilir

# Renkli çıktılar
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; B = Fore.BLUE; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = B = RESET = ""

TERMUX_LOC_CMD = "termux-location"

def check_termux_location_api():
    """Termux konum aracının varlığını kontrol eder."""
    tool_path = shutil.which(TERMUX_LOC_CMD)
    if not tool_path:
        print(f"{R}Hata: '{TERMUX_LOC_CMD}' komutu bulunamadı!{RESET}")
        print(f"{Y}Yerel konumu alma özelliği SADECE Termux üzerinde 'termux-api' paketi kuruluysa çalışır.{RESET}")
        print(f"{Y}Lütfen 'pkg install termux-api' komutu ile kurun ve Konum iznini verin.{RESET}")
        return False
    print(f"{G}Termux konum aracı bulundu: {tool_path}{RESET}")
    return True

def ip_konum_bul(ip):
    """Verilen IP adresinin konumunu bulur."""
    try:
        print(f"\n{B}🔍 IP Konumu Aranıyor: {ip}{RESET}")

        # requests kurulu mu diye tekrar kontrol
        if 'requests' not in sys.modules:
            print(f"{R}Hata: 'requests' kütüphanesi yüklenemediği için IP konumu bulunamıyor.{RESET}")
            return

        api_url = f"http://ip-api.com/json/{ip}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # HTTP hatalarını kontrol et
        data = response.json()

        if data.get('status') == 'success':
            print(f"\n{G}📍 IP Konum Bilgisi:{RESET}")
            print(f"  IP:           {data.get('query', 'N/A')}")
            print(f"  Ülke:         {data.get('country', 'N/A')}")
            print(f"  Şehir:        {data.get('city', 'N/A')}")
            print(f"  ISP:          {data.get('isp', 'N/A')}")
            print(f"  Organizasyon: {data.get('org', 'N/A')}")
            print(f"  Koordinatlar: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")

            # Google Maps linki
            if data.get('lat') and data.get('lon'):
                 print(f"\n{Y}🗺️ Google Maps Linki:{RESET}")
                 print(f"   https://www.google.com/maps/search/?api=1&query={data['lat']},{data['lon']}")

            # Log dosyası
            try:
                 with open("ip_konum_log.txt", "a", encoding='utf-8') as f:
                     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                     f.write(f"\n[{timestamp}] IP: {ip}\n")
                     f.write(f"  Ülke: {data.get('country')}\n")
                     f.write(f"  Şehir: {data.get('city')}\n")
                     f.write(f"  Koordinatlar: {data.get('lat')}, {data.get('lon')}\n")
                 print(f"{G}Bilgiler 'ip_konum_log.txt' dosyasına eklendi.{RESET}")
            except Exception as log_err:
                 print(f"{Y}Uyarı: Log dosyasına yazılamadı: {log_err}{RESET}")
        else:
            print(f"{R}❌ Konum bilgisi alınamadı! API Yanıtı: {data.get('message', 'Bilinmiyor')}{RESET}")

    except requests.exceptions.RequestException as e:
        print(f"{R}❌ Ağ Hatası: IP konumu alınamadı. Bağlantıyı kontrol edin.{RESET}")
        print(f"{R}   Detay: {e}{RESET}")
    except Exception as e:
        print(f"{R}❌ IP konumu alınırken beklenmedik hata: {e}{RESET}")
        traceback.print_exc()


def yerel_konum_bul():
    """Termux API kullanarak yerel GPS konumunu alır."""
    print(f"\n{B}📡 Yerel Konum Tespit Ediliyor (Sadece Termux)...{RESET}")

    if not check_termux_location_api():
        return # Araç yoksa devam etme

    try:
        # Konum sağlayıcı seçimi (gps, network, passive)
        # GPS daha doğru ama daha yavaş ve iç mekanlarda çalışmayabilir.
        provider = input(f"{Y}Konum Sağlayıcı [gps (önerilen), network, passive - varsayılan=gps]: {RESET}").strip().lower()
        if provider not in ['gps', 'network', 'passive']:
            provider = 'gps'
        print(f"{C}'{provider}' sağlayıcısı kullanılıyor... (Bu işlem biraz sürebilir){RESET}")

        # Konum alma komutu (timeout ekleyelim)
        # Komut: termux-location -p [provider]
        command = [TERMUX_LOC_CMD, "-p", provider]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False, encoding='utf-8') # 60 saniye timeout

        if result.returncode != 0:
             print(f"{R}Hata: Konum bilgisi alınamadı! (Return Code: {result.returncode}){RESET}")
             print(f"{R}Termux:API hatası veya Konum izni sorunu olabilir.{RESET}")
             print(f"{Y}Stderr: {result.stderr}{RESET}")
             return

        # Dönen JSON verisini parse et
        try:
            konum_data = json.loads(result.stdout)
            if not isinstance(konum_data, dict): # Bazen boş string dönebilir
                 raise json.JSONDecodeError("Boş veya geçersiz JSON", result.stdout, 0)
        except json.JSONDecodeError as e:
             print(f"{R}Hata: Termux API'den gelen konum verisi JSON formatında değil!{RESET}")
             print(f"{Y}Alınan Ham Veri: {result.stdout}{RESET}")
             print(f"{R}Detay: {e}{RESET}")
             return

        # Konum verisini yazdır
        print(f"\n{G}📍 Yerel Konum Bilgisi ({konum_data.get('provider','Bilinmiyor')}):{RESET}")
        print(f"  Enlem:     {konum_data.get('latitude', 'N/A')}")
        print(f"  Boylam:    {konum_data.get('longitude', 'N/A')}")
        print(f"  Yükseklik: {konum_data.get('altitude', 'N/A')} m")
        print(f"  Doğruluk:  {konum_data.get('accuracy', 'N/A')} m")
        print(f"  Hız:       {konum_data.get('speed', 'N/A')} m/s")
        print(f"  Zaman:     {datetime.fromtimestamp(konum_data.get('elapsedMs', 0)/1000) if konum_data.get('elapsedMs') else 'N/A'}") # Unix zamanını çevir

        # Google Maps linki
        if konum_data.get('latitude') and konum_data.get('longitude'):
            print(f"\n{Y}🗺️ Google Maps Linki:{RESET}")
            print(f"   https://www.google.com/maps/search/?api=1&query={konum_data['latitude']},{konum_data['longitude']}")

        # Log dosyası
        try:
             with open("yerel_konum_log.txt", "a", encoding='utf-8') as f:
                 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 f.write(f"\n[{timestamp}] Yerel Konum ({konum_data.get('provider','?')})\n")
                 for key, value in konum_data.items():
                      f.write(f"  {key.capitalize()}: {value}\n")
             print(f"{G}Bilgiler 'yerel_konum_log.txt' dosyasına eklendi.{RESET}")
        except Exception as log_err:
             print(f"{Y}Uyarı: Log dosyasına yazılamadı: {log_err}{RESET}")

    except subprocess.TimeoutExpired:
        print(f"{R}Hata: Konum alma işlemi zaman aşımına uğradı (60s). Farklı bir sağlayıcı (network?) deneyin veya GPS sinyalini kontrol edin.{RESET}")
    except FileNotFoundError:
         print(f"{R}Hata: '{TERMUX_LOC_CMD}' komutu çalıştırılamadı (tekrar kontrol).{RESET}")
    except Exception as e:
        print(f"{R}❌ Yerel konum alınırken beklenmedik hata: {e}{RESET}")
        traceback.print_exc()


def menu():
    """Ana menüyü gösterir."""
    print(f"""{B}
    ╔══════════════════════════════╗
    ║   {C}GELİŞMİŞ KONUM BULUCU{B}      ║
    ╠══════════════════════════════╣
    ║ {G}1. IP Adresinden Konum Bul{B}  ║
    ║ {G}2. Yerel Konumu Tespit Et{B}  ║
    ║    {Y}(Sadece Termux){B}         ║
    ║ {R}0. Çıkış{B}                    ║
    ╚══════════════════════════════╝{RESET}""")
    return input(f"{Y}Seçim (1/2/0): {RESET}").strip()

if __name__ == "__main__":
    # Termux kontrolünü başlangıçta yapabiliriz ama her seçimde yapmak daha güncel olabilir.
    # termux_loc_available = check_termux_location_api()

    while True:
        secim = menu()
        if secim == "1":
            ip_input = input(f"{Y}Hedef IP adresi: {RESET}").strip()
            if ip_input:
                 try:
                      # IP formatını doğrula
                      socket.inet_aton(ip_input)
                      ip_konum_bul(ip_input)
                 except socket.error:
                      print(f"{R}Geçersiz IP formatı!{RESET}")
            else:
                 print(f"{R}IP adresi boş olamaz.{RESET}")
        elif secim == "2":
            yerel_konum_bul() # Fonksiyon kendi içinde Termux kontrolü yapıyor
        elif secim == "0":
            print(f"{G}Çıkış yapılıyor...{RESET}")
            break
        else:
            print(f"{R}Geçersiz seçim!{RESET}")

        try:
            input(f"\n{C}Devam etmek için Enter'a basın...{RESET}")
        except KeyboardInterrupt:
            print(f"\n{G}Çıkış yapılıyor...{RESET}")
            break
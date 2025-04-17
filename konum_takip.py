#!/usr/bin/env python3
import os
import json
import requests
import socket
from datetime import datetime

# Renkli çıktılar
class colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    END = "\033[0m"

def ip_konum_bul(ip):
    try:
        print(f"\n{colors.BLUE}🔍 {ip} konumu aranıyor...{colors.END}")
        
        # IP API sorgusu
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        
        if response['status'] == 'success':
            print(f"\n{colors.GREEN}📍 IP Konum Bilgisi:{colors.END}")
            print(f"IP: {ip}")
            print(f"Ülke: {response.get('country', 'Bilinmiyor')}")
            print(f"Şehir: {response.get('city', 'Bilinmiyor')}")
            print(f"ISP: {response.get('isp', 'Bilinmiyor')}")
            print(f"Koordinatlar: {response.get('lat', '?')}, {response.get('lon', '?')}")
            
            # Google Maps linki
            print(f"\n{colors.YELLOW}🗺️ Google Maps:{colors.END}")
            print(f"https://maps.google.com/?q={response['lat']},{response['lon']}")
            
            # Kayıt dosyası
            with open("ip_konum_log.txt", "a") as f:
                f.write(f"\n[{datetime.now()}] {ip}:\n")
                f.write(f"Ülke: {response.get('country')}\n")
                f.write(f"Şehir: {response.get('city')}\n")
                f.write(f"Koordinatlar: {response.get('lat')}, {response.get('lon')}\n\n")
        else:
            print(f"{colors.RED}❌ Konum bilgisi alınamadı!{colors.END}")
    
    except Exception as e:
        print(f"{colors.RED}❌ Hata: {str(e)}{colors.END}")

def yerel_konum_bul():
    try:
        print(f"\n{colors.BLUE}📡 Yerel konum tespit ediliyor...{colors.END}")
        
        # Termux API kontrolü
        if not os.path.exists('/data/data/com.termux/files/usr/bin/termux-location'):
            raise Exception("Termux-location kurulu değil!")
        
        # GPS ile konum alma
        konum = json.loads(os.popen("termux-location -p gps").read())
        
        if not konum:
            raise Exception("GPS verisi alınamadı!")
        
        print(f"\n{colors.GREEN}📍 Yerel Konum Bilgisi:{colors.END}")
        print(f"Enlem: {konum.get('latitude', 'Bilinmiyor')}")
        print(f"Boylam: {konum.get('longitude', 'Bilinmiyor')}")
        print(f"Doğruluk: {konum.get('accuracy', 'Bilinmiyor')} metre")
        
        # Google Maps linki
        print(f"\n{colors.YELLOW}🗺️ Google Maps:{colors.END}")
        print(f"https://maps.google.com/?q={konum['latitude']},{konum['longitude']}")
        
        # Kayıt dosyası
        with open("yerel_konum_log.txt", "a") as f:
            f.write(f"\n[{datetime.now()}]\n")
            f.write(f"Enlem: {konum.get('latitude')}\n")
            f.write(f"Boylam: {konum.get('longitude')}\n")
            f.write(f"Doğruluk: {konum.get('accuracy')}m\n\n")
            
    except Exception as e:
        print(f"{colors.RED}❌ Hata: {str(e)}{colors.END}")
        print("Çözüm: termux-setup-storage && pkg install termux-api")

def menu():
    print(f"""
{colors.BLUE}
╔══════════════════════════════╗
║      GELİŞMİŞ KONUM BULUCU   ║
╠══════════════════════════════╣
║ 1. IP'den Konum Bul          ║
║ 2. Yerel Konumu Tespit Et    ║
║                              ║
║ 0. Çıkış                     ║
╚══════════════════════════════╝{colors.END}""")
    return input("Seçim (1/2/0): ")

if __name__ == "__main__":
    while True:
        secim = menu()
        if secim == "1":
            ip = input("\nHedef IP adresi: ")
            ip_konum_bul(ip)
        elif secim == "2":
            yerel_konum_bul()
        elif secim == "0":
            print(f"{colors.RED}Çıkış yapılıyor...{colors.END}")
            break
        else:
            print(f"{colors.RED}Geçersiz seçim!{colors.END}")
        
        input("\nDevam etmek için Enter'a basın...")
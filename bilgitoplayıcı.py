#!/usr/bin/env python3
import os
import re
import socket
import requests
from datetime import datetime

# Renkli çıktılar
class colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    END = "\033[0m"

def ip_to_phoneinfo(ip):
    try:
        # WHOIS sorgusu
        print(f"\n{colors.BLUE}🔍 {ip} analiz ediliyor...{colors.END}")
        
        # Temel IP bilgileri
        try:
            host = socket.gethostbyaddr(ip)[0]
        except:
            host = "Bilinmiyor"
        
        # API ile detaylı bilgi (ip-api.com)
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        
        if response['status'] == 'success':
            print(f"\n{colors.GREEN}📍 Konum Bilgisi:{colors.END}")
            print(f"Ülke: {response.get('country', 'Bilinmiyor')}")
            print(f"Şehir: {response.get('city', 'Bilinmiyor')}")
            print(f"ISP: {response.get('isp', 'Bilinmiyor')}")
            print(f"Organizasyon: {response.get('org', 'Bilinmiyor')}")
            
            # Port tarama (temel)
            print(f"\n{colors.YELLOW}🛡️ Temel Port Tarama:{colors.END}")
            ports = [21, 22, 80, 443]
            for port in ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                status = "AÇIK" if result == 0 else "KAPALI"
                print(f"Port {port}: {status}")
                sock.close()
            
            # Kayıt dosyası
            with open("ip_kayitlari.txt", "a") as f:
                f.write(f"\n[{datetime.now()}] {ip}:\n")
                f.write(f"Host: {host}\n")
                f.write(f"Konum: {response.get('city')}, {response.get('country')}\n")
                f.write(f"ISP: {response.get('isp')}\n\n")
                
        else:
            print(f"{colors.RED}❌ IP bilgileri alınamadı!{colors.END}")
    
    except Exception as e:
        print(f"{colors.RED}❌ Hata: {str(e)}{colors.END}")

def telefon_bilgisi():
    try:
        # Android cihaz bilgileri
        print(f"\n{colors.GREEN}📱 Yerel Cihaz Bilgileri:{colors.END}")
        
        # Temel bilgiler
        info = {
            "Model": os.popen("getprop ro.product.model").read().strip(),
            "Üretici": os.popen("getprop ro.product.manufacturer").read().strip(),
            "Android": os.popen("getprop ro.build.version.release").read().strip(),
            "IP": os.popen("ip route get 1 | awk '{print $7}'").read().strip(),
            "MAC": os.popen("ip link show wlan0 | awk '/ether/ {print $2}'").read().strip()
        }
        
        for key, value in info.items():
            print(f"{key}: {value}")
        
        # Kayıt dosyası
        with open("telefon_bilgileri.txt", "w") as f:
            for key, value in info.items():
                f.write(f"{key}: {value}\n")
                
    except Exception as e:
        print(f"{colors.RED}❌ Hata: {str(e)}{colors.END}")

def menu():
    print(f"""
{colors.BLUE}
╔══════════════════════════════╗
║   TELEFON BİLGİ TOPLAYICI    ║
╠══════════════════════════════╣
║ 1. IP'den Bilgi Topla        ║
║ 2. Yerel Cihaz Bilgileri     ║
║                              ║
║ 0. Çıkış                     ║
╚══════════════════════════════╝{colors.END}""")
    return input("Seçim (1/2/0): ")

if __name__ == "__main__":
    while True:
        secim = menu()
        if secim == "1":
            ip = input("\nHedef IP adresi: ")
            ip_to_phoneinfo(ip)
        elif secim == "2":
            telefon_bilgisi()
        elif secim == "0":
            print(f"{colors.RED}Çıkış yapılıyor...{colors.END}")
            break
        else:
            print(f"{colors.RED}Geçersiz seçim!{colors.END}")
        
        input("\nDevam etmek için Enter'a basın...")
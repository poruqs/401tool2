#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# bilgitoplayıcı.py

import os
import re
import socket
import sys # sys.exit için
import traceback # Hata gösterme
from datetime import datetime

# requests kütüphanesini kontrol et
try:
    import requests
except ImportError:
    print("Hata: 'requests' kütüphanesi bulunamadı.")
    print("Lütfen kurun: pip install requests")
    # Çalışmaya devam edebilir (IP kısmı çalışmaz) ama uyarı verelim.
    # sys.exit(1) # İstersen burada çıkılabilir

# Renkli çıktılar
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; B = Fore.BLUE; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = B = RESET = ""

def ip_info(ip):
    """Verilen IP adresi hakkında bilgi toplar."""
    try:
        print(f"\n{B}🔍 IP adresi analiz ediliyor: {ip}{RESET}")

        # API ile detaylı bilgi (ip-api.com)
        try:
            # requests kurulu mu diye tekrar kontrol (import başta başarısız olduysa)
            if 'requests' not in sys.modules:
                 print(f"{R}Hata: 'requests' kütüphanesi yüklenemediği için IP bilgisi alınamıyor.{RESET}")
                 return

            api_url = f"http://ip-api.com/json/{ip}"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status() # HTTP hatalarını kontrol et
            data = response.json()

            if data.get('status') == 'success':
                print(f"\n{G}📍 Konum ve Ağ Bilgisi:{RESET}")
                print(f"  IP:           {data.get('query', 'N/A')}")
                print(f"  Ülke:         {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})")
                print(f"  Bölge:        {data.get('regionName', 'N/A')} ({data.get('region', 'N/A')})")
                print(f"  Şehir:        {data.get('city', 'N/A')}")
                print(f"  Posta Kodu:   {data.get('zip', 'N/A')}")
                print(f"  Koordinatlar: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
                print(f"  Zaman Dilimi: {data.get('timezone', 'N/A')}")
                print(f"  ISP:          {data.get('isp', 'N/A')}")
                print(f"  Organizasyon: {data.get('org', 'N/A')}")
                print(f"  AS Numarası:  {data.get('as', 'N/A')}")

                # Google Maps linki
                if data.get('lat') and data.get('lon'):
                     print(f"\n{Y}🗺️ Google Maps Linki:{RESET}")
                     print(f"   https://www.google.com/maps/search/?api=1&query={data['lat']},{data['lon']}")

                 # Kayıt dosyası (opsiyonel)
                try:
                     with open("ip_kayitlari.txt", "a", encoding='utf-8') as f:
                         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                         f.write(f"\n[{timestamp}] IP: {ip}\n")
                         for key, value in data.items():
                             f.write(f"  {key.capitalize()}: {value}\n")
                     print(f"{G}Bilgiler 'ip_kayitlari.txt' dosyasına eklendi.{RESET}")
                except Exception as log_err:
                     print(f"{Y}Uyarı: Log dosyasına yazılamadı: {log_err}{RESET}")

            else:
                print(f"{R}❌ IP bilgisi alınamadı. API Yanıtı: {data.get('message', 'Bilinmeyen API hatası')}{RESET}")

        except requests.exceptions.RequestException as e:
             print(f"{R}❌ Ağ Hatası: IP bilgisi alınamadı. İnternet bağlantınızı kontrol edin.{RESET}")
             print(f"{R}   Detay: {e}{RESET}")
        except Exception as e:
             print(f"{R}❌ IP bilgisi alınırken beklenmedik hata: {e}{RESET}")
             traceback.print_exc()

    except Exception as outer_e:
         print(f"{R}❌ IP Bilgisi fonksiyonunda genel hata: {outer_e}{RESET}")
         traceback.print_exc()


def telefon_bilgisi():
    """Yerel cihaz bilgilerini (Termux/Android) toplamaya çalışır."""
    print(f"\n{B}📱 Yerel Cihaz Bilgileri Toplanıyor...{RESET}")
    print(f"{Y}Uyarı: Bu bölüm büyük ölçüde Termux/Android üzerinde çalışır.{RESET}")

    info = {}
    commands = {
        "Model": "getprop ro.product.model",
        "Üretici": "getprop ro.product.manufacturer",
        "Marka": "getprop ro.product.brand",
        "Cihaz": "getprop ro.product.device",
        "Android Sürümü": "getprop ro.build.version.release",
        "API Seviyesi": "getprop ro.build.version.sdk",
        "Güvenlik Yaması": "getprop ro.build.version.security_patch",
        "Donanım": "getprop ro.hardware",
        # Ağ bilgileri (daha güvenilir yöntemler kullanılabilir)
        "Yerel IP (wlan0)": "ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1",
        "MAC (wlan0)": "ip link show wlan0 | awk '/ether/ {print $2}'"
    }

    for key, cmd in commands.items():
        try:
            # Komutu çalıştır ve çıktısını al
            # shell=True güvenlik riski taşır ama pipe (|) ve awk gibi yapılar için basit yol
            # Daha güvenli yöntemler subprocess.Popen ve Popen.communicate kullanmaktır.
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5, check=False, encoding='utf-8')
            output = result.stdout.strip() if result.returncode == 0 else "N/A (Komut Hatası)"
            # Bazı komutlar hata verse bile devam et
        except subprocess.TimeoutExpired:
             output = "N/A (Zaman Aşımı)"
        except FileNotFoundError:
             output = f"N/A ('{cmd.split()[0]}' bulunamadı)" # Komut bulunamadı
        except Exception as e:
            output = f"N/A (Hata: {e})"

        info[key] = output if output else "N/A (Boş Çıktı)" # Boş çıktıyı da belirt

    # Toplanan bilgileri yazdır
    print(f"\n{G}--- Cihaz Bilgileri ---{RESET}")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Bilgileri dosyaya kaydet (opsiyonel)
    try:
        with open("telefon_bilgileri.txt", "w", encoding='utf-8') as f:
            f.write(f"--- Cihaz Bilgileri ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---\n")
            for key, value in info.items():
                f.write(f"{key}: {value}\n")
        print(f"\n{G}Bilgiler 'telefon_bilgileri.txt' dosyasına kaydedildi.{RESET}")
    except Exception as e:
        print(f"\n{Y}Uyarı: Cihaz bilgileri dosyaya kaydedilemedi: {e}{RESET}")

def menu():
    """Ana menüyü gösterir."""
    print(f"""{B}
    ╔══════════════════════════════╗
    ║   {C}TELEFON BİLGİ TOPLAYICI{B}    ║
    ╠══════════════════════════════╣
    ║ {G}1. IP Adresinden Bilgi Topla{B} ║
    ║ {G}2. Yerel Cihaz Bilgileri{B}    ║
    ║ {R}0. Çıkış{B}                    ║
    ╚══════════════════════════════╝{RESET}""")
    return input(f"{Y}Seçim (1/2/0): {RESET}").strip()

if __name__ == "__main__":
    while True:
        secim = menu()
        if secim == "1":
            ip_input = input(f"{Y}Hedef IP adresi: {RESET}").strip()
            if ip_input:
                 # Basit IP format kontrolü
                 try:
                      socket.inet_aton(ip_input) # Hata fırlatırsa geçersizdir
                      ip_info(ip_input)
                 except socket.error:
                      print(f"{R}Geçersiz IP formatı!{RESET}")
            else:
                 print(f"{R}IP adresi boş olamaz.{RESET}")
        elif secim == "2":
            telefon_bilgisi()
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
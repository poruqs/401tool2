# -*- coding: utf-8 -*-
import requests
import os
import sys
import json
import ipaddress
from time import sleep

# --- GÜVENLİK UYARISI ---
print("""\033[1;31m
=============================================
BU ARAÇ SADECE KENDİ CHROMECAST CİHAZLARINIZ
İÇİN GELİŞTİRİLMİŞTİR. BAŞKALARININ CİHAZLARINA
İZİNSİZ ERİŞİM YASA DIŞIDIR VE ETİK DEĞİLDİR!
=============================================\033[0m
""")
sleep(2)

def clear_screen():
    """Platforma uygun ekran temizleme"""
    os.system('cls' if os.name == 'nt' else 'clear')

def validate_ip(ip):
    """IP adresi doğrulama"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def print_title():
    """Program başlığını göster"""
    print("\n" + "="*50)
    print(" Chromecast Kontrol Arayüzü")
    print("="*50)

class ChromecastController:
    def __init__(self):
        self.ip = ""
        self.port = 8008  # Chromecast default port
        self.timeout = 10  # İstek zaman aşımı (saniye)
    
    def get_ip_input(self):
        """Kullanıcıdan geçerli bir IP adresi al"""
        while True:
            clear_screen()
            print_title()
            ip_input = input("\n Chromecast IP Adresi (Çıkış için q): ").strip()
            
            if ip_input.lower() == 'q':
                sys.exit("Çıkılıyor...")
            
            if validate_ip(ip_input):
                self.ip = ip_input
                return True
            else:
                print("\n\033[91mHATA: Geçersiz IP formatı!\033[0m")
                sleep(1)
    
    def send_request(self, endpoint, method="POST", data=None):
        """Chromecast'e HTTP isteği gönder"""
        url = f"http://{self.ip}:{self.port}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if data else {}
        
        try:
            response = requests.request(
                method,
                url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            print(f"\nDurum Kodu: {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"\n\033[91mHATA: {str(e)}\033[0m")
            return None
    
    def play_video(self):
        """YouTube videosu oynat"""
        video_id = input("\n YouTube Video ID: ").strip()
        if not video_id:
            print("\n\033[91mHATA: Video ID boş olamaz!\033[0m")
            return
        
        payload = {"v": video_id}
        response = self.send_request("apps/YouTube", data=payload)
        
        if response and response.status_code == 201:
            print("\n\033[92mVideo oynatma isteği gönderildi!\033[0m")
        else:
            print("\n\033[91mVideo oynatılamadı!\033[0m")
    
    def reboot_device(self):
        """Cihazı yeniden başlat"""
        confirm = input("\n Cihazı yeniden başlatmak istediğinize emin misiniz? (e/h): ")
        if confirm.lower() != 'e':
            return
        
        response = self.send_request("setup/reboot", data={"params": "now"})
        
        if response and response.status_code == 200:
            print("\n\033[92mYeniden başlatma isteği gönderildi!\033[0m")
        else:
            print("\n\033[91mYeniden başlatma başarısız!\033[0m")
    
    def factory_reset(self):
        """Fabrika ayarlarına sıfırla"""
        confirm = input("\n FABRİKA AYARLARINA SIFIRLAMA! (GERİ ALINAMAZ) Onaylıyor musunuz? (e/h): ")
        if confirm.lower() != 'e':
            return
        
        response = self.send_request("setup/reboot", data={"params": "fdr"})
        
        if response and response.status_code == 200:
            print("\n\033[92mSıfırlama isteği gönderildi!\033[0m")
        else:
            print("\n\033[91mSıfırlama başarısız!\033[0m")
    
    def show_menu(self):
        """Ana menüyü göster"""
        while True:
            clear_screen()
            print_title()
            print(f"\n Seçili Cihaz: \033[93m{self.ip if self.ip else 'Tanımlanmadı'}\033[0m")
            
            print("\n 1 - IP Adresi Gir")
            print(" 2 - Video Oynat (YouTube)")
            print(" 3 - Yeniden Başlat")
            print(" 4 - Fabrika Ayarlarına Sıfırla")
            print(" 0 - Çıkış")
            
            choice = input("\n Seçiminiz: ").strip()
            
            if choice == '1':
                self.get_ip_input()
            elif choice == '2':
                if not self.ip:
                    print("\n\033[91mÖnce geçerli bir IP adresi girin!\033[0m")
                    sleep(1)
                else:
                    self.play_video()
            elif choice == '3':
                if not self.ip:
                    print("\n\033[91mÖnce geçerli bir IP adresi girin!\033[0m")
                    sleep(1)
                else:
                    self.reboot_device()
            elif choice == '4':
                if not self.ip:
                    print("\n\033[91mÖnce geçerli bir IP adresi girin!\033[0m")
                    sleep(1)
                else:
                    self.factory_reset()
            elif choice == '0':
                sys.exit("\nÇıkılıyor...")
            else:
                print("\n\033[91mGeçersiz seçim!\033[0m")
                sleep(1)
            
            if choice in ['2', '3', '4']:
                input("\n Devam etmek için Enter'a basın...")

def check_dependencies():
    """Gerekli kütüphaneleri kontrol et"""
    try:
        import requests
        import ipaddress
    except ImportError as e:
        print(f"\n\033[91mHATA: Gerekli kütüphane eksik - {str(e)}\033[0m")
        print("Kurulum için: pip install requests")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()
    controller = ChromecastController()
    controller.show_menu()
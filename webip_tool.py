#!/usr/bin/env python3
import socket

def ip_to_site():
    ip = input("\nIP adresi girin (örn: 8.8.8.8): ")
    try:
        site = socket.gethostbyaddr(ip)[0]
        print(f"\n🌐 Web Adresi: {site}")
        print(f"🔗 Link: http://{site}")
    except:
        print("\n❌ Site bulunamadı veya hata oluştu!")

def site_to_ip():
    site = input("\nSite adresi girin (örn: google.com): ").replace("https://", "").replace("http://", "").replace("www.", "")
    try:
        ip = socket.gethostbyname(site)
        print(f"\n🖥️ IP Adresi: {ip}")
    except:
        print("\n❌ IP bulunamadı veya hata oluştu!")

while True:
    print("""
    ╔══════════════════════════╗
    ║    IP/SITE DÖNÜŞTÜRÜCÜ   ║
    ╠══════════════════════════╣
    ║ 1. IP'den Site Bul       ║
    ║ 2. Siteden IP Bul        ║
    ║ 0. Çıkış                 ║
    ╚══════════════════════════╝
    """)
    
    secim = input("Seçim (1/2/0): ")
    
    if secim == "1":
        ip_to_site()
    elif secim == "2":
        site_to_ip()
    elif secim == "0":
        print("\nÇıkış yapılıyor...")
        break
    else:
        print("\nGeçersiz seçim!")
    
    input("\nDevam etmek için Enter'a basın...")
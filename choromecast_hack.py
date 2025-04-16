# -*- coding: utf-8 -*-
# Gerekli kütüphane: pip install requests
import requests
import os
import sys
import json # JSON verisi göndermek için
import ipaddress # IP doğrulaması için eklendi

# --- UYARI ---
# Bu araç yerel ağdaki Chromecast cihazlarını kontrol etmeye çalışır.
# Chromecast cihazlarının kontrol API'leri zamanla değişebilir ve
# bu betikteki endpointler veya veri formatları artık çalışmayabilir.
# Başkalarına ait cihazları izinsiz kontrol etmek etik değildir ve ağ kurallarını ihlal edebilir.
# --- UYARI SONU ---


# Platforma uygun ekran temizleme fonksiyonu
def clear_screen():
    """Ekranı temizler (Windows için 'cls', Linux/macOS için 'clear')."""
    os.system('cls' if os.name == 'nt' else 'clear')

# IP adresi doğrulama fonksiyonu
def validate_ip(ip):
    """String'in geçerli bir IP adresi olup olmadığını kontrol eder."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Hata mesajını get_ip_input içinde verelim
        return False

# Ana başlığı yazdırma fonksiyonu
def print_title():
    """Program başlığını yazdırır."""
    print("...................................................")
    print(".       Chromecast Hack - Control               .")
    print("...................................................")

# Ana menü ve işlem döngüsü
def main():
    ip_address = ""

    while True:
        clear_screen()
        print_title()

        # Eğer IP adresi daha önce alınmadıysa veya geçersizse al
        while not ip_address:
            try:
                ip_input = input(" Chromecast Cihazının IP Adresi: ")
                if not ip_input: # Boş giriş kontrolü
                     print("HATA: IP adresi boş olamaz.")
                     continue
                if validate_ip(ip_input):
                    ip_address = ip_input
                else:
                    # Geçersizse hata mesajı ver ve döngüye devam et
                    print("HATA: Geçerli bir IP adresi formatı girmediniz.")
                    # input("Devam etmek için Enter'a basın...") # İsteğe bağlı bekleme
                    # clear_screen()
                    # print_title()
                    continue # Tekrar sor
            except KeyboardInterrupt:
                print("\nÇıkılıyor...")
                sys.exit()

        # Seçilen IP'yi ve menüyü göster
        clear_screen()
        print_title()
        print(f" Seçili Cihaz IP: {ip_address}\n")

        # Menü seçenekleri
        print(" 1 - Video Oynat (YouTube ID ile)")
        print(" 2 - Yeniden Başlat (Reboot)")
        print(" 3 - Fabrika Ayarlarına Sıfırla (Factory Reset)")
        print(" 4 - IP Adresini Değiştir")
        print(" 0 - Çıkış")
        print("...................................................")

        try:
            choice = input(" Bir seçenek seçin : ")

            if choice == '1':
                try:
                    video_id = input(" Oynatılacak YouTube Video ID: ")
                    if not video_id:
                        print("HATA: Video ID boş olamaz.")
                    else:
                        play_video(ip_address, video_id)
                except KeyboardInterrupt:
                    print("\nİşlem iptal edildi.")

            elif choice == '2':
                reboot_chromecast(ip_address)
            elif choice == '3':
                factory_reset_chromecast(ip_address)
            elif choice == '4':
                ip_address = "" # IP adresini sıfırla ki döngü başında tekrar sorsun
                print("\nIP adresi sıfırlandı. Ana menüde yeni IP sorulacak.")
                # input("Devam etmek için Enter'a basın...") # Hemen sorması için bekletmeyelim
            elif choice == '0':
                print("\nÇıkılıyor...")
                break # Döngüden çık
            else:
                print("\nHATA: Geçersiz seçim.")

        except KeyboardInterrupt:
            print("\nÇıkılıyor...")
            break
        except Exception as e:
            print(f"\nBEKLENMEDİK HATA: {e}")
            import traceback
            traceback.print_exc() # Hatanın detayını göster

        # Her işlemden sonra bekletme (IP değiştirme ve çıkış hariç)
        if choice not in ['4', '0']:
             try:
                  input("\nDevam etmek için Enter'a basın...")
             except KeyboardInterrupt:
                  print("\nÇıkılıyor...")
                  break


# Chromecast'e istek göndermek için yardımcı fonksiyon
def send_request(ip, endpoint, method="POST", json_data=None, data=None, timeout=10):
    """Belirtilen endpoint'e HTTP isteği gönderir."""
    # Chromecast genellikle 8008 portunu kullanır (HTTP)
    url = f"http://{ip}:8008/{endpoint}"
    headers = {}
    # Gönderilecek veri türüne göre Content-Type ayarla
    if json_data is not None:
         headers["Content-Type"] = "application/json; charset=utf-8"
    elif data is not None:
         headers["Content-Type"] = "application/x-www-form-urlencoded" # Form verisi için

    try:
        print(f"\nİstek gönderiliyor: {method.upper()} {url}")
        if json_data: print(f"JSON Verisi: {json.dumps(json_data)}")
        if data: print(f"Form Verisi: {data}") # Form verisini de yazdırabiliriz

        response = None
        # İsteği gönder
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json_data, data=data, timeout=timeout)
        elif method.upper() == "GET":
             response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == "DELETE": # YouTube uygulamasını durdurmak için kullanılabilir (?)
             response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            print(f"HATA: Desteklenmeyen HTTP metodu: {method}")
            return None

        # Yanıtı kontrol et
        print(f"Yanıt Kodu: {response.status_code}")
        # Yanıt içeriği çok uzun olabilir, başını gösterelim
        # print(f"Yanıt İçeriği (ilk 200 karakter): {response.text[:200]}")

        # Başarılı kabul edilen kodlar (genellikle 2xx)
        if 200 <= response.status_code < 300:
            print("İşlem isteği başarıyla gönderildi veya cihaz yanıt verdi.")
            return response
        else:
            # Hatalı durum kodları için daha fazla bilgi vermeye çalış
            error_reason = response.reason #örn: 'Not Found', 'Forbidden'
            print(f"HATA: Cihazdan beklenen yanıt alınamadı (Kod: {response.status_code} - {error_reason}).")
            print(f"   Yanıt detayı (varsa): {response.text[:200]}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"HATA: Cihaza bağlanılamadı ({ip}:{8008}). IP adresini, cihazın açık olduğunu ve ağ bağlantısını kontrol edin.")
        return None
    except requests.exceptions.Timeout:
        print(f"HATA: İstek zaman aşımına uğradı ({timeout} saniye). Cihaz yanıt vermiyor veya meşgul olabilir.")
        return None
    except requests.exceptions.RequestException as e:
        # Diğer requests hataları
        print(f"HATA: İstek gönderilirken bir ağ/istek hatası oluştu: {e}")
        return None
    except Exception as e:
        # Beklenmedik diğer hatalar
        print(f"HATA: İstek gönderilirken beklenmedik bir hata oluştu: {e}")
        return None

# İşlem fonksiyonları
def play_video(ip, video_id):
    """Chromecast'te YouTube videosu oynatma isteği gönderir."""
    # Chromecast'te YouTube uygulamasını başlatıp video oynatmak için DIAL protokolü kullanılır.
    # YouTube uygulamasının ID'si genellikle "YouTube" veya benzeridir.
    # Uygulamaya POST isteği ile 'v=<video_id>' parametresi gönderilir.
    print(f"\n'{video_id}' ID'li YouTube videosunu oynatma deneniyor...")
    # Payload form verisi olarak gönderilir ('v=VIDEO_ID')
    payload_data = f'v={video_id}'
    # Endpoint genellikle uygulamanın adıdır: /apps/YouTube
    result = send_request(ip, "apps/YouTube", method="POST", data=payload_data)
    if result:
        # Başarılı yanıt (genellikle 201 Created veya 200 OK) uygulamanın başlatıldığını gösterir.
        print(f"YouTube uygulamasını başlatma ve '{video_id}' videosunu oynatma isteği {ip} adresine gönderildi.")
    else:
        print("Video oynatma isteği gönderilemedi. Cihaz meşgul olabilir veya YouTube uygulaması bulunamadı.")

def reboot_chromecast(ip):
    """Chromecast'i yeniden başlatma isteği gönderir."""
    # Cihaz yönetimi endpoint'i genellikle /setup/... altındadır.
    print("\nCihazı yeniden başlatma deneniyor...")
    payload = {"params": "now"} # veya "reboot" olabilir, API'ye bağlı
    # /setup/reboot endpoint'ine JSON payload ile POST isteği
    result = send_request(ip, "setup/reboot", method="POST", json_data=payload)
    if result:
        print(f"Cihaz ({ip}) yeniden başlatma isteği gönderildi.")
    else:
        print("Yeniden başlatma isteği gönderilemedi. Endpoint veya parametre yanlış olabilir.")


def factory_reset_chromecast(ip):
    """Chromecast'i fabrika ayarlarına sıfırlama isteği gönderir."""
    print("") # Boş satır
    try:
        confirm = input(f"UYARI: Cihaz ({ip}) fabrika ayarlarına sıfırlanacak! Bu işlem geri alınamaz.\nEmin misiniz? (E/H): ").strip().upper()
    except KeyboardInterrupt:
        print("\nİptal edildi.")
        return

    if confirm == 'E':
        print("\nCihazı fabrika ayarlarına sıfırlama deneniyor...")
        payload = {"params": "fdr"} # Factory Data Reset için genellikle 'fdr' parametresi kullanılır
        # Yeniden başlatma ile aynı endpoint'e farklı parametre gönderilir
        result = send_request(ip, "setup/reboot", method="POST", json_data=payload)
        if result:
            print(f"Cihaz ({ip}) fabrika ayarlarına sıfırlama isteği gönderildi.")
        else:
            print("Fabrika ayarlarına sıfırlama isteği gönderilemedi. Endpoint veya parametre yanlış olabilir.")
    else:
        print("İşlem iptal edildi.")


# Ana programı çalıştır
if __name__ == "__main__":
    # Gerekli kütüphaneleri kontrol et
    module_error = False
    try:
        import requests
    except ImportError:
        print("HATA: Gerekli 'requests' kütüphanesi bulunamadı.")
        module_error = True
    try:
        import ipaddress
    except ImportError:
        print("HATA: Gerekli 'ipaddress' kütüphanesi bulunamadı (Python 3.3+ gereklidir).")
        module_error = True

    if module_error:
        print("Lütfen eksik kütüphaneleri 'pip install <kütüphane_adı>' komutu ile kurun.")
        sys.exit(1)

    main()
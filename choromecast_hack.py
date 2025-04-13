# Gerekli kütüphane: pip install requests
import requests
import os
import sys
import json # JSON verisi göndermek için

# Platforma uygun ekran temizleme fonksiyonu
def clear_screen():
    """Ekranı temizler (Windows için 'cls', Linux/macOS için 'clear')."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Ana başlığı yazdırma fonksiyonu
def print_title():
    """Program başlığını yazdırır."""
    print("...................................................")
    print(".       Chromecast Hack - Control               .")
    print("...................................................")

# Ana menü ve işlem döngüsü
def main():
    ip_address = ""
    video_id = ""

    while True:
        clear_screen()
        print_title()

        # Eğer IP adresi veya Video ID daha önce alınmadıysa al
        if not ip_address:
            try:
                ip_address = input(" Chromecast IP Adresi: ")
                # Basit IP format kontrolü (isteğe bağlı ama önerilir)
                if not ip_address or len(ip_address.split('.')) != 4:
                    print("HATA: Geçerli bir IP adresi girmediniz.")
                    ip_address = "" # Tekrar sormak için sıfırla
                    input("Devam etmek için Enter'a basın...")
                    continue
            except KeyboardInterrupt:
                print("\nÇıkılıyor...")
                sys.exit()

        # Video ID'yi her seferinde sormak yerine sadece 1. seçenek için soralım
        # if not video_id: # Veya her döngüde sorulabilir, batch script gibi
        #    try:
        #         video_id = input(" Youtube Video ID   : ")
        #         if not video_id:
        #             print("HATA: Video ID boş olamaz.")
        #             video_id = ""
        #             input("Devam etmek için Enter'a basın...")
        #             continue
        #     except KeyboardInterrupt:
        #         print("\nÇıkılıyor...")
        #         sys.exit()

        clear_screen()
        print_title()
        print(f" Cihaz IP: {ip_address}\n") # Seçilen IP'yi göster

        # Menü seçenekleri
        print(" 1 - Video Oynat")
        print(" 2 - Yeniden Başlat (Reboot)")
        print(" 3 - Fabrika Ayarlarına Sıfırla (Factory Reset)")
        print(" 4 - IP Adresini Değiştir")
        print(" 0 - Çıkış")
        print("...................................................")

        try:
            choice = input(" Bir seçenek seçin : ")

            if choice == '1':
                # Video ID'yi burada soralım
                try:
                    current_video_id = input(" Oynatılacak Youtube Video ID: ")
                    if not current_video_id:
                        print("HATA: Video ID boş olamaz.")
                    else:
                        play_video(ip_address, current_video_id)
                except KeyboardInterrupt:
                    print("\nİşlem iptal edildi.")

            elif choice == '2':
                reboot_chromecast(ip_address)
            elif choice == '3':
                factory_reset_chromecast(ip_address)
            elif choice == '4':
                ip_address = "" # IP adresini sıfırla ki döngü başında tekrar sorsun
                print("\nIP adresi sıfırlandı. Yeni IP sorulacak.")
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

        # Her işlemden sonra bekletme
        if choice != '4': # IP değiştirme sonrası hemen yeni IP sorsun
             input("\nDevam etmek için Enter'a basın...")


# Chromecast'e istek göndermek için yardımcı fonksiyon
def send_request(ip, endpoint, method="POST", json_data=None, data=None):
    """Belirtilen endpoint'e HTTP isteği gönderir."""
    url = f"http://{ip}:8008/{endpoint}"
    headers = {"Content-Type": "application/json"} if json_data else {}

    try:
        print(f"\nİstek gönderiliyor: {url}")
        if method.upper() == "POST":
            # JSON verisi varsa json parametresiyle, yoksa data ile gönder
            if json_data:
                response = requests.post(url, headers=headers, json=json_data, timeout=10)
            else:
                response = requests.post(url, headers=headers, data=data, timeout=10)
        # Başka metodlar (GET vb.) gerekirse buraya eklenebilir
        # elif method.upper() == "GET":
        #    response = requests.get(url, timeout=10)
        else:
            print(f"HATA: Desteklenmeyen HTTP metodu: {method}")
            return None

        # Yanıtı kontrol et
        print(f"Yanıt Kodu: {response.status_code}")
        # print(f"Yanıt İçeriği: {response.text[:200]}") # Yanıtın başını göster (hata ayıklama için)

        # Başarılı kabul edilen kodlar (API'ye göre değişebilir)
        if 200 <= response.status_code < 300:
            print("İşlem isteği başarıyla gönderildi.")
            return response
        else:
            print(f"HATA: Cihazdan beklenen yanıt alınamadı. Kod: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"HATA: Cihaza bağlanılamadı ({ip}). IP adresini veya ağ bağlantısını kontrol edin.")
        return None
    except requests.exceptions.Timeout:
        print("HATA: İstek zaman aşımına uğradı.")
        return None
    except Exception as e:
        print(f"HATA: İstek gönderilirken hata oluştu: {e}")
        return None

# İşlem fonksiyonları
def play_video(ip, video_id):
    """Chromecast'te YouTube videosu oynatır."""
    # YouTube uygulamasına JSON formatında video ID göndermeyi deneyelim
    # Batch script'teki 'v=%id%' kısmı curl'ün -d parametresiyle farklı yorumlanabilir.
    # API genellikle JSON bekler.
    payload = {'v': video_id}
    result = send_request(ip, "apps/YouTube", method="POST", json_data=payload)
    # if result:
    #     print(f"Video '{video_id}' oynatma isteği {ip} adresine gönderildi.")

def reboot_chromecast(ip):
    """Chromecast'i yeniden başlatır."""
    payload = {"params": "now"}
    result = send_request(ip, "setup/reboot", method="POST", json_data=payload)
    # if result:
    #     print(f"Cihaz ({ip}) yeniden başlatılıyor...")

def factory_reset_chromecast(ip):
    """Chromecast'i fabrika ayarlarına sıfırlar."""
    confirm = input("UYARI: Cihaz fabrika ayarlarına sıfırlanacak! Emin misiniz? (E/H): ").strip().upper()
    if confirm == 'E':
        payload = {"params": "fdr"}
        result = send_request(ip, "setup/reboot", method="POST", json_data=payload)
        # if result:
        #     print(f"Cihaz ({ip}) fabrika ayarlarına sıfırlanıyor...")
    else:
        print("İşlem iptal edildi.")


# Ana programı çalıştır
if __name__ == "__main__":
    # requests kütüphanesinin kurulu olduğundan emin olalım
    try:
        import requests
    except ImportError:
        print("HATA: 'requests' kütüphanesi bulunamadı.")
        print("Lütfen kurmak için 'pip install requests' komutunu çalıştırın.")
        sys.exit(1)

    main()
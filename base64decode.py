# base64_decoder.py

import base64
import binascii # Hata yakalama için

def decode_base64(encoded_string):
    """Verilen Base64 kodlu string'i çözer."""
    try:
        # Base64 string'ini byte'a çevirip çöz
        decoded_bytes = base64.b64decode(encoded_string)
        # Çözülen byte'ları okunabilir bir string'e çevir (UTF-8 varsayılan)
        try:
            decoded_string = decoded_bytes.decode('utf-8')
            return decoded_string
        except UnicodeDecodeError:
            # Eğer UTF-8 ile çözülemezse, byte olarak döndür veya başka bir encoding dene
            return f"UTF-8 ile çözülemedi. Byte sonucu: {decoded_bytes}"
    except binascii.Error as e:
        # Geçersiz Base64 girişi hatası
        return f"Hata: Geçersiz Base64 girişi! Detay: {e}"
    except Exception as e:
        # Diğer olası hatalar
        return f"Beklenmedik bir hata oluştu: {e}"

if __name__ == "__main__":
    print("--- Base64 Decoder ---")
    while True:
        try:
            # Kullanıcıdan giriş al
            base64_input = input("Lütfen Base64 kodlu metni girin (çıkmak için 'q' yazın): ")

            if base64_input.lower() == 'q':
                break

            if not base64_input:
                print("Giriş boş olamaz.")
                continue

            # Çözme fonksiyonunu çağır
            result = decode_base64(base64_input)

            # Sonucu yazdır
            print("\n--- Çözülen Metin ---")
            print(result)
            print("-" * 20 + "\n")

        except KeyboardInterrupt:
            print("\nÇıkılıyor...")
            break
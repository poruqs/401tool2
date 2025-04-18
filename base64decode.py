# -*- coding: utf-8 -*-
# base64decode.py (Geliştirilmiş Versiyon)

import base64
import binascii # Hata yakalama için
import sys
import os # Dosya işlemleri için

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = RESET = ""

def decode_base64(encoded_data):
    """Verilen Base64 kodlu veriyi çözer."""
    try:
        # Girdi string ise byte'a çevir (dosyadan okunduysa zaten byte olabilir)
        if isinstance(encoded_data, str):
            # Base64 standart karakter seti dışındakileri ve boşlukları temizle (isteğe bağlı)
            encoded_data = ''.join(filter(lambda char: char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=', encoded_data))
            encoded_bytes = encoded_data.encode('ascii') # Base64 ASCII kullanır
        else:
             encoded_bytes = encoded_data # Zaten byte ise

        # Padding kontrolü ve ekleme (gerekliyse)
        missing_padding = len(encoded_bytes) % 4
        if missing_padding:
            encoded_bytes += b'=' * (4 - missing_padding)

        # Base64 çözme
        decoded_bytes = base64.b64decode(encoded_bytes, validate=True)

        # Metin olarak çözmeyi dene (Önce UTF-8)
        try:
            decoded_string = decoded_bytes.decode('utf-8')
            print(f"{G}UTF-8 olarak çözüldü.{RESET}")
            return decoded_string # String olarak döndür
        except UnicodeDecodeError:
            # Başarısız olursa Latin-1 dene
            try:
                decoded_string = decoded_bytes.decode('iso-8859-1') # Latin-1
                print(f"{Y}UTF-8 ile çözülemedi, ISO-8859-1 (Latin-1) olarak denendi.{RESET}")
                return decoded_string # String olarak döndür
            except UnicodeDecodeError:
                # Bu da başarısız olursa, byte olarak kabul et
                print(f"{Y}Metin olarak çözülemedi (UTF-8/Latin-1). Sonuç binary (byte) veridir.{RESET}")
                return decoded_bytes # Byte olarak döndür

    except binascii.Error as e:
        print(f"{R}Hata: Geçersiz Base64 girişi!{RESET}")
        print(f"{R}Detay: {e}{RESET}")
        return None
    except Exception as e:
        print(f"{R}Beklenmedik bir kod çözme hatası oluştu: {e}{RESET}")
        return None

def get_input_data():
    """Kullanıcıdan Base64 verisini alır (manuel, çok satırlı veya dosyadan)."""
    while True:
        print("\nVeri Giriş Yöntemi:")
        print("  1: Manuel Giriş (Tek/Çok Satır)")
        print("  2: Dosyadan Oku")
        print("  q: Çıkış")
        choice = input(f"{Y}Seçiminiz [1, 2, q]: {RESET}").strip().lower()

        if choice == '1':
            print(f"{C}Base64 metnini yapıştırın.{RESET}")
            print(f"{C}(Bitirmek için yeni satırda sadece 'END' yazın veya boş bırakıp Enter'a basın):{RESET}")
            lines = []
            while True:
                try:
                    line = input()
                    # Kullanıcı bitirmek için 'END' yazabilir veya boş satır bırakabilir
                    if line.strip().upper() == 'END' or line == "":
                        break
                    lines.append(line)
                except EOFError: # Dosya sonu karakteri (Ctrl+D)
                    break
            if not lines:
                print(f"{R}Giriş yapılmadı.{RESET}")
                continue
            return "".join(lines) # Tüm satırları birleştir

        elif choice == '2':
            while True:
                filepath = input(f"{Y}Base64 verisini içeren dosyanın yolunu girin: {RESET}").strip()
                if not filepath:
                    print(f"{R}Dosya yolu boş olamaz.{RESET}")
                    continue
                try:
                    with open(filepath, 'rb') as f: # Byte olarak oku
                        print(f"{C}'{filepath}' okunuyor...{RESET}")
                        return f.read() # Byte olarak döndür
                except FileNotFoundError:
                    print(f"{R}Hata: Dosya bulunamadı: '{filepath}'{RESET}")
                except Exception as e:
                    print(f"{R}Hata: Dosya okunurken sorun oluştu: {e}{RESET}")
                # Dosya okuma başarısız olursa tekrar sor
                try_again = input(f"{Y}Başka bir dosya denemek ister misiniz? (e/h): {RESET}").strip().lower()
                if try_again != 'e':
                    return None # Kullanıcı istemezse None döndür

        elif choice == 'q':
            return None # Çıkış istendi
        else:
            print(f"{R}Geçersiz seçim.{RESET}")


def handle_output(decoded_result):
    """Çözülen veriyi ekrana yazdırır veya dosyaya kaydeder."""
    if decoded_result is None:
        return # Hata varsa bir şey yapma

    is_binary = isinstance(decoded_result, bytes)

    # Çok uzunsa uyarı ver ve önizleme göster
    output_preview = ""
    output_len = len(decoded_result)
    max_print_len = 2000 # Ekrana basılacak maksimum karakter/byte sayısı
    is_long = output_len > max_print_len

    if is_long:
        print(f"{Y}Uyarı: Çözülen veri çok uzun ({output_len} byte/karakter).{RESET}")
        if is_binary:
             # Byte verinin başını ve sonunu göster (repr ile)
             output_preview = f"{repr(decoded_result[:max_print_len//2])[:-1]} ... {repr(decoded_result[-max_print_len//2:])[1:]}"
        else:
             # String verinin başını ve sonunu göster
             output_preview = f"{decoded_result[:max_print_len//2]} ... {decoded_result[-max_print_len//2:]}"
        print(f"{C}--- Önizleme ---{RESET}\n{output_preview}\n{C}----------------{RESET}")
    else:
        # Kısa ise tamamını yazdırabiliriz
        if is_binary:
            print(f"{C}--- Çözülen Veri (Byte) ---{RESET}\n{decoded_result!r}\n{C}-------------------------{RESET}")
        else:
            print(f"{C}--- Çözülen Metin ---{RESET}\n{decoded_result}\n{C}---------------------{RESET}")


    # Kaydetme seçeneğini sor
    while True:
        save_choice = input(f"{Y}Sonucu dosyaya kaydetmek ister misiniz? (e/h): {RESET}").strip().lower()
        if save_choice == 'e':
            output_filename = input(f"{Y}Kaydedilecek dosya adı: {RESET}").strip()
            if not output_filename:
                 print(f"{R}Dosya adı boş olamaz.{RESET}")
                 continue
            try:
                # Veri tipine göre yazma modunu belirle
                if is_binary:
                    with open(output_filename, 'wb') as f:
                        f.write(decoded_result)
                    print(f"{G}Binary veri başarıyla '{output_filename}' dosyasına kaydedildi.{RESET}")
                else:
                    with open(output_filename, 'w', encoding='utf-8') as f:
                        f.write(decoded_result)
                    print(f"{G}Metin başarıyla '{output_filename}' dosyasına kaydedildi (UTF-8).{RESET}")
                break # Kaydetme başarılı, döngüden çık
            except IOError as e:
                print(f"{R}Hata: Dosya yazılamadı!{RESET}")
                print(f"{R}Detay: {e}{RESET}")
                # Tekrar sormak yerine döngüden çıkabilir veya tekrar sorabiliriz
                try_again_save = input(f"{Y}Başka bir dosya adı denemek ister misiniz? (e/h): {RESET}").strip().lower()
                if try_again_save != 'e':
                    break # Kullanıcı istemezse çık
            except Exception as e:
                 print(f"{R}Dosya kaydetme sırasında beklenmedik hata: {e}{RESET}")
                 break # Beklenmedik hatada çık
        elif save_choice == 'h':
            break # Kaydetmek istemiyorsa çık
        else:
            print(f"{R}Geçersiz seçim.{RESET}")


if __name__ == "__main__":
    print(f"{C}--- Gelişmiş Base64 Decoder ---{RESET}")
    while True:
        try:
            encoded_data = get_input_data()

            if encoded_data is None: # Kullanıcı çıkmak istedi veya dosya okunamadı
                break # Ana döngüden çık

            print(f"\n{C}Kod çözülüyor...{RESET}")
            decoded_result = decode_base64(encoded_data)

            handle_output(decoded_result)

            print("\n" + "="*30 + "\n") # İşlemler arası ayırıcı

        except KeyboardInterrupt:
            print("\nÇıkılıyor...")
            break
        except Exception as loop_err:
             print(f"{R}Ana döngüde hata: {loop_err}{RESET}")
             traceback.print_exc() # Hata izini yazdır

    print(f"{G}Program sonlandırıldı.{RESET}")
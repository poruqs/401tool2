import subprocess
import os
import sys
try:
    from colorama import init, Fore, Style, Back
    # Colorama'yı başlat
    init(autoreset=True)
    # Renkleri ve Stilleri tanımla
    BRIGHT = Style.BRIGHT
    DIM = Style.DIM
    R = Fore.RED      # Kırmızı
    G = Fore.GREEN    # Yeşil
    Y = Fore.YELLOW   # Sarı
    B = Fore.BLUE     # Mavi (Kutu için)
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE    # Beyaz/Varsayılan
    RESET = Style.RESET_ALL
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""


# Banner - Tamamı Kırmızı ve Parlak
banner = f"""
{R}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}
{R}{BRIGHT}██║  ██║██╔═████╗███║{RESET}
{R}{BRIGHT}███████║██║██╔██║╚██║{RESET}
{R}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}
{R}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}
{R}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}
"""

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Daha belirgin numaralar ve mavi kutu ile stilli menü."""
    clear_screen()
    print(banner)

    menu_width = 50 # Menü kutusunun genişliği
    title = "ANA MENÜ"

    # İç genişlik (kenarlıklar ve 1 boşluk padding hariç)
    inner_width = menu_width - 4

    # Mavi Üst Kenarlık
    print(f"{B}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
    # Başlık Satırı (Sarı Başlık)
    print(f"{B}{BRIGHT}║ {Y}{BRIGHT}{title.center(menu_width - 4)} {B}{BRIGHT}║{RESET}")
    # Mavi Ayırıcı Kenarlık
    print(f"{B}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")
    # Boş Satır
    print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")

    # Menü Öğeleri
    menu_items = {
        '1': "Call Bomb",
        '2': "SMS Bomb",
        '3': "DoS Saldırısı",
        '4': f"Netflix Checker {R}(BAKIMDA){W}", # <<< Değişiklik Burada
        '5': "Base64 Decode"
    }

    for key, value in menu_items.items():
        # Numara kısmı (Parlak Sarı)
        num_part = f"[{key}]"
        # Metin kısmı (renk kodlarını hesaba katmadan uzunluk hesapla)
        # Colorama kodlarını temizleyen basit bir fonksiyon (varsa)
        def strip_colors(s):
            import re
            return re.sub(r'\x1b\[[0-9;]*[mK]', '', s)

        text_part = value
        visible_text_part_len = len(strip_colors(text_part)) # Görünen metin uzunluğu

        # Numara ve metin için ayrılan toplam boşluk
        # Hizalama için formatlama
        num_str = f"{Y}{BRIGHT}{num_part}{W}" # Numara her zaman aynı renk ve stilde
        # Metnin yaslanacağı genişlik (görünen uzunluğa göre)
        text_width = inner_width - len(num_part) - 1 # -1 numara sonrası boşluk için
        # Metni (renk kodlarıyla birlikte) sola yasla, ama hizalama görünene göre olsun
        # Bu biraz karmaşık olabilir, basitçe sola yaslayalım, genellikle çalışır
        value_str = f" {text_part:<{text_width + (len(text_part) - visible_text_part_len)}}" # Renk kodlarının uzunluğunu ekle

        print(f"{B}{BRIGHT}║ {num_str}{value_str} {B}{BRIGHT}║{RESET}")


    # Boş Satır
    print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")
    # Ayırıcı
    print(f"{B}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")

    # Çıkış Seçeneği
    num_part_exit = "[0]"
    text_part_exit = "Çıkış"
    num_str_exit = f"{R}{BRIGHT}{num_part_exit}{W}" # Çıkış numarası Kırmızı
    text_width_exit = inner_width - len(num_part_exit) - 1
    value_str_exit = f" {text_part_exit:<{text_width_exit}}"
    print(f"{B}{BRIGHT}║ {num_str_exit}{value_str_exit} {B}{BRIGHT}║{RESET}")

    # Mavi Alt Kenarlık
    print(f"{B}{BRIGHT}{'╚' + '═' * (menu_width - 2) + '╝'}{RESET}")

    # Seçim istemi (Yeşil)
    try:
        choice = input(f"\n{G}{BRIGHT}>> Seçiminizi girin:{W} ")
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()


def run_script(script_name):
    """Belirtilen Python betiğini çalıştırır."""
    # Kullanıcı "BAKIMDA" olan bir seçeneği seçerse uyarı ver
    if script_name == "netflix_checker..py":
         print(f"\n{R}{BRIGHT}UYARI:{Y} Netflix Checker şu anda bakımdadır ve düzgün çalışmayabilir.{RESET}")
         # İsteğe bağlı olarak burada çalıştırmayı engelleyebilirsiniz:
         # input(f"{Y}Devam etmek için Enter tuşuna basın veya işlemi iptal etmek için Ctrl+C...{RESET}")
         time.sleep(2) # Kısa bir bekleme

    try:
        print(f"\n{C}{BRIGHT}--- '{script_name}' başlatılıyor ---{RESET}\n")
        time.sleep(0.5)
        python_executable = sys.executable
        subprocess.run([python_executable, script_name], check=True)
        print(f"\n{G}{BRIGHT}--- '{script_name}' başarıyla tamamlandı ---{RESET}")
    except FileNotFoundError:
        print(f"\n{R}{BRIGHT}HATA: '{script_name}' dosyası bulunamadı!{RESET}")
        print(f"{Y}Lütfen '{script_name}' dosyasının '{os.path.basename(__file__)}' ile aynı dizinde olduğundan emin olun.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"\n{R}{BRIGHT}HATA: '{script_name}' çalıştırılırken bir sorun oluştu.{RESET}")
        print(f"{Y}Betik muhtemelen bir hata verdi (Çıkış Kodu: {e.returncode}). Betiğin kendi hata mesajlarına bakın.{RESET}")
    except Exception as e:
        print(f"\n{R}{BRIGHT}Beklenmedik bir hata oluştu: {e}{RESET}")

    print(f"\n{Y}Devam etmek için Enter tuşuna basın...{RESET}")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()

# Ana program akışı
if __name__ == "__main__":
    import time

    while True:
        user_choice = show_menu()

        if user_choice == '1':
            run_script("call_bomb.py")
        elif user_choice == '2':
            run_script("sms_bomb.py")
        elif user_choice == '3':
            run_script("DoS.py")
        elif user_choice == '4':
            # Orijinal netflix dosya adı ('netflix_checker..py') kullanılıyor.
            run_script("netflix_checker.py")
        elif user_choice == '5':
            run_script("base64decode.py")
        elif user_choice == '0':
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}")
            time.sleep(0.5)
            break
        else:
            print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen menüdeki numaralardan birini girin.{RESET}")
            time.sleep(1.5)
import subprocess
import os
import sys
import time
import re

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
    B = Fore.BLUE     # Mavi
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE    # Beyaz/Varsayılan
    RESET = Style.RESET_ALL
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""

# Banner - Orijinal "401", Tamamı Parlak Yeşil ve Ortalamak için Sol Boşluk Eklendi
banner_padding = " " * 15 # Banner'ı sağa kaydırmak için boşluk
banner = f"""
{banner_padding}{G}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}
{banner_padding}{G}{BRIGHT}██║  ██║██╔═████╗███║{RESET}
{banner_padding}{G}{BRIGHT}███████║██║██╔██║╚██║{RESET}
{banner_padding}{G}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}
{banner_padding}{G}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}
{banner_padding}{G}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}
"""

# Renk kodlarını temizleyen fonksiyon
def strip_colors(s):
    """ANSI renk/stil kodlarını string'den temizler."""
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', s)

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Düzeltilmiş hizalama ve ortalanmış banner ile stilli menü."""
    clear_screen()
    print(banner) # Ortalanmış yeşil "401" banner

    menu_width = 55 # Menü kutusunun genişliği
    title = "ANA MENÜ"

    # İç genişlik (kenarlıklar '║' ve kenarlardaki 1'er boşluk için)
    inner_width = menu_width - 4

    # --- Menü Kutusu Başlangıcı (Mavi) ---
    print(f"{B}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
    # Başlık Satırı (Kırmızı Başlık, kutu içinde ortalı)
    print(f"{B}{BRIGHT}║ {R}{BRIGHT}{title.center(inner_width)} {B}{BRIGHT}║{RESET}")
    # Ayırıcı Kenarlık
    print(f"{B}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")
    # Boş Satır (Padding)
    print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")

    # Menü Öğeleri
    menu_items = {
        '1': "Call Bomb",
        '2': "SMS Bomb",
        '3': "DoS Saldırısı",
        '4': f"Netflix Checker {R}(BAKIMDA){W}", # Renk kodu içeriyor
        '5': "Base64 Decode"
    }

    # Menü öğelerini yazdır (Hizalama Mantığı)
    for key, value in menu_items.items():
        # 1. Renkli Numara Kısmı: "[1]" gibi
        num_part_colored = f"{Y}{BRIGHT}[{key}]{W}"
        # 2. Renksiz Numara Kısmı (uzunluk için): "[1]" gibi
        num_part_plain = f"[{key}]"

        # 3. Renkli Metin Kısmı: "Call Bomb" veya "Netflix...(BAKIMDA)" gibi
        text_part_colored = value
        # 4. Renksiz Metin Kısmı (uzunluk için)
        text_part_plain = strip_colors(text_part_colored)

        # 5. Görünen tam öğe metninin uzunluğu (renksiz): "[1] Call Bomb"
        visible_item_length = len(num_part_plain) + 1 + len(text_part_plain) # +1 aradaki boşluk için

        # 6. Sağ tarafa eklenecek boşluk sayısı
        # inner_width: kutu içindeki toplam kullanılabilir karakter sayısı
        padding_needed = inner_width - visible_item_length

        # 7. Yazdırılacak son satır: Renkli Numara + Boşluk + Renkli Metin + Hesaplanan Boşluk
        item_str_colored = f"{num_part_colored} {text_part_colored}"
        # Negatif boşluk olmamasını sağla
        final_padding = ' ' * max(0, padding_needed)

        print(f"{B}{BRIGHT}║ {item_str_colored}{final_padding} {B}{BRIGHT}║{RESET}")

    # Boş Satır (Padding)
    print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")
    # Ayırıcı
    print(f"{B}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")

    # Çıkış Seçeneği (Aynı hizalama mantığı ile)
    num_part_exit = "[0]"
    text_part_exit = "Çıkış"
    visible_exit_length = len(num_part_exit) + 1 + len(text_part_exit)
    padding_needed_exit = inner_width - visible_exit_length
    item_str_exit_colored = f"{R}{BRIGHT}{num_part_exit}{W} {text_part_exit}"
    final_padding_exit = ' ' * max(0, padding_needed_exit)
    print(f"{B}{BRIGHT}║ {item_str_exit_colored}{final_padding_exit} {B}{BRIGHT}║{RESET}")

    # Mavi Alt Kenarlık
    print(f"{B}{BRIGHT}{'╚' + '═' * (menu_width - 2) + '╝'}{RESET}")
    # --- Menü Kutusu Sonu ---

    # Seçim istemi (Yeşil)
    try:
        choice = input(f"\n{G}{BRIGHT}>> Seçiminizi girin:{W} ")
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()


def run_script(script_name):
    """Belirtilen Python betiğini çalıştırır."""
    if script_name == "netflix_checker..py":
         print(f"\n{R}{BRIGHT}UYARI:{Y} Netflix Checker şu anda bakımdadır ve düzgün çalışmayabilir.{RESET}")
         time.sleep(2)

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
            run_script("netflix_checker..py")
        elif user_choice == '5':
            run_script("base64decode.py")
        elif user_choice == '0':
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}")
            time.sleep(0.5)
            break
        else:
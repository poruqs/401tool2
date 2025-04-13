import subprocess
import os
import sys
import time # Gerekli modülleri başta import edelim
import re   # Gerekli modülleri başta import edelim

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

# Banner - Tamamı Parlak Yeşil
banner = f"""
{G}{BRIGHT}██╗  ██╗ ██████╗  ██╗   ████████╗ ██████╗   ██████╗  ██╗     {RESET}
{G}{BRIGHT}██║  ██║██╔═████╗███║   ╚═╗██╔═╝██╔═══██╗ ██╔═══██╗  ██║     {RESET}
{G}{BRIGHT}███████║██║██╔██║╚██║     ║██║  ██║   ██║ ██║   ██║  ██║     {RESET}
{G}{BRIGHT}╚════██║████╔╝██║ ██║     ║██║  ██║   ██║ ██║   ██║  ██║     {RESET}
{G}{BRIGHT}     ██║╚██████╔╝ ██║     ║██║  ██╚═══██║ ██╚═══██║  ██║     {RESET}
{G}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝     ╚═╝   ╚██████╔╝  ╚██████╔╝  ███████╗{RESET}
"""

# Renk kodlarını temizleyen fonksiyon (bir kere tanımla)
def strip_colors(s):
    """ANSI renk/stil kodlarını string'den temizler."""
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', s)

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Düzeltilmiş hizalama ile stilli menü."""
    clear_screen()
    print(banner)

    menu_width = 75 # Menü kutusunun genişliği
    title = "ANA MENÜ"

    # İç genişlik (kenarlıklar ve 2 boşluk padding hariç)
    inner_width = menu_width - 4 # Sol ve sağdaki 1'er boşluk için

    # Mavi Üst Kenarlık
    print(f"{B}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
    # Başlık Satırı (Kırmızı Başlık)
    print(f"{B}{BRIGHT}║ {R}{BRIGHT}{title.center(inner_width)} {B}{BRIGHT}║{RESET}")
    # Mavi Ayırıcı Kenarlık
    print(f"{B}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")
    # Boş Satır
    print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")

    # Menü Öğeleri
    menu_items = {
        '1': "Call Bomb",
        '2': "SMS Bomb",
        '3': "DoS Saldırısı",
        '4': f"Netflix Checker {R}(BAKIMDA){W}", # Renk kodu içeriyor
        '5': "Base64 Decode"
    }

    for key, value in menu_items.items():
        # Numara kısmı (Renkli ve düz metin)
        num_part_colored = f"{Y}{BRIGHT}[{key}]{W}"
        num_part_plain = f"[{key}]"

        # Metin kısmı (Renkli ve düz metin)
        text_part_colored = value
        text_part_plain = strip_colors(text_part_colored)

        # Görünen tam öğe metni (numara + boşluk + metin)
        visible_item_text = f"{num_part_plain} {text_part_plain}"
        visible_item_length = len(visible_item_text)

        # Gereken boşluk padding'ini hesapla
        padding_needed = inner_width - visible_item_length

        # Renkli öğeyi oluştur (Numara + Boşluk + Renkli Metin)
        item_str_colored = f"{num_part_colored} {text_part_colored}"

        # Satırı yazdır: Kenarlık + Boşluk + Renkli Öğe + Hesaplanan Boşluk + Kenarlık
        # Hesaplanan boşluğun negatif olmadığından emin ol
        print(f"{B}{BRIGHT}║ {item_str_colored}{' ' * max(0, padding_needed)} {B}{BRIGHT}║{RESET}")

    # Boş Satır
    print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")
    # Ayırıcı
    print(f"{B}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")

    # Çıkış Seçeneği (Hizalama düzeltmesi)
    num_part_exit = "[0]"
    text_part_exit = "Çıkış"
    visible_exit_text = f"{num_part_exit} {text_part_exit}"
    visible_exit_length = len(visible_exit_text)
    padding_needed_exit = inner_width - visible_exit_length
    item_str_exit_colored = f"{R}{BRIGHT}{num_part_exit}{W} {text_part_exit}"
    print(f"{B}{BRIGHT}║ {item_str_exit_colored}{' ' * max(0, padding_needed_exit)} {B}{BRIGHT}║{RESET}")


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
            print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen menüdeki numaralardan birini girin.{RESET}")
            time.sleep(1.5)
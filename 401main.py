import subprocess
import os
import sys
import time
import re

# Colorama import ve fallback mekanizması
try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True) # Renkleri otomatik sıfırla
    BRIGHT = Style.BRIGHT
    DIM = Style.DIM
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    B = Fore.BLUE
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE
    RESET = Style.RESET_ALL # Gerekirse diye dursun
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    # Colorama yoksa, tüm renk/stil değişkenlerini boş string yap
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""
    # class tanımları da Attribute hatası vermesin diye ekleyelim
    class Style: BRIGHT = ""; DIM = ""; RESET_ALL = ""
    class Fore: RED = ""; GREEN = ""; YELLOW = ""; BLUE = ""; MAGENTA = ""; CYAN = ""; WHITE = ""
    class Back: pass


# Banner - Orijinal "401", Tamamı Parlak Yeşil ve Ortalamak için Sol Boşluk Eklendi
banner_padding = " " * 15
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
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Hata ayıklaması yapılmış hizalama ile stilli menü."""
    clear_screen()
    print(banner)

    menu_width = 55
    title = "ANA MENÜ"
    inner_width = menu_width - 4 # ║ İçerik ║ için kullanılabilir alan

    try:
        # --- Menü Kutusu Başlangıcı (Mavi) ---
        print(f"{B}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
        print(f"{B}{BRIGHT}║ {R}{BRIGHT}{title.center(inner_width)} {B}{BRIGHT}║{RESET}") # Kırmızı Başlık
        print(f"{B}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")
        print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}") # Boşluk

        menu_items = {
            '1': "Call Bomb",
            '2': "SMS Bomb",
            '3': "DoS Saldırısı",
            '4': f"Netflix Checker {R}(BAKIMDA){W}",
            '5': "Base64 Decode"
        }

        for key, value in menu_items.items():
            num_part_colored = f"{Y}{BRIGHT}[{key}]{W}"
            num_part_plain = f"[{key}]"
            text_part_colored = value
            text_part_plain = strip_colors(text_part_colored)
            visible_item_length = len(num_part_plain) + 1 + len(text_part_plain)
            padding_needed = inner_width - visible_item_length
            item_str_colored = f"{num_part_colored} {text_part_colored}"
            final_padding = ' ' * max(0, padding_needed)
            print(f"{B}{BRIGHT}║ {item_str_colored}{final_padding} {B}{BRIGHT}║{RESET}")

        # Boş Satır ve Ayırıcı
        print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")
        print(f"{B}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")

        # Çıkış Seçeneği
        num_part_exit = "[0]"
        text_part_exit = "Çıkış"
        visible_exit_length = len(num_part_exit) + 1 + len(text_part_exit)
        padding_needed_exit = inner_width - visible_exit_length
        item_str_exit_colored = f"{R}{BRIGHT}{num_part_exit}{W} {text_part_exit}"
        final_padding_exit = ' ' * max(0, padding_needed_exit)
        print(f"{B}{BRIGHT}║ {item_str_exit_colored}{final_padding_exit} {B}{BRIGHT}║{RESET}")

        # Alt Kenarlık
        print(f"{B}{BRIGHT}{'╚' + '═' * (menu_width - 2) + '╝'}{RESET}")
        # --- Menü Kutusu Sonu ---

    except Exception as e:
        print(f"\n{R}MENÜ ÇİZİM HATASI:{RESET} {e}")
        return None # Hata durumunda None döndür

    # Seçim istemi
    try:
        choice = input(f"\n{G}{BRIGHT}>> Seçiminizi girin:{W} ")
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()
    except Exception as e:
        print(f"\n{R}GİRİŞ HATASI:{RESET} {e}")
        return None

def run_script(script_name):
    """Belirtilen Python betiğini çalıştırır."""
    if not script_name:
        print(f"{R}Çalıştırılacak betik adı alınamadı.{RESET}")
        time.sleep(2)
        return

    if script_name == "netflix_checker..py":
         print(f"\n{R}{BRIGHT}UYARI:{Y} Netflix Checker şu anda bakımdadır ve düzgün çalışmayabilir.{RESET}")
         time.sleep(2)

    try:
        print(f"\n{C}{BRIGHT}--- '{script_name}' başlatılıyor ---{RESET}\n")
        time.sleep(0.5)
        python_executable = sys.executable
        subprocess.run([python_executable, script_name], check=True, text=True, capture_output=False)
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

        if user_choice is None:
            print(f"{R}Menü gösterilirken bir hata oluştu, program sonlandırılıyor.{RESET}")
            time.sleep(3)
            break

        script_to_run = None
        if user_choice == '1':
            script_to_run = "call_bomb.py"
        elif user_choice == '2':
            script_to_run = "sms_bomb.py"
        elif user_choice == '3':
            script_to_run = "DoS.py"
        elif user_choice == '4':
            script_to_run = "netflix_checker..py"
        elif user_choice == '5':
            script_to_run = "base64decode.py"
        elif user_choice == '0':
            # Düzeltilmiş Satır:
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}") # <<< } eklendi
            time.sleep(0.5)
            break # Döngüden çık
        else:
            print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen menüdeki numaralardan birini girin.{RESET}")
            time.sleep(1.5)
            continue # Geçersiz seçimse run_script'e gitme, döngüye baştan başla

        # Sadece geçerli bir seçim yapıldıysa ve çıkış seçilmediyse run_script'i çağır
        if script_to_run:
             run_script(script_to_run)
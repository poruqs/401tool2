import subprocess
import os
import sys
try:
    from colorama import init, Fore, Style, Back
    # Colorama'yı başlat (Windows'ta renkleri etkinleştirir ve otomatik sıfırlar)
    init(autoreset=True)
    # Renkleri tanımla (daha kolay kullanım için)
    BRIGHT = Style.BRIGHT
    DIM = Style.DIM
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    B = Fore.BLUE
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE
    RESET = Style.RESET_ALL # init(autoreset=True) olsa da bazen gerekebilir
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    # Colorama yoksa renkleri boş string yap
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""


# Banner (İsteğe bağlı olarak renklendirilebilir)
# Farklı renklerde deneme yapabilirsiniz
banner = f"""
{C}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}
{M}{BRIGHT}██║  ██║██╔═████╗███║{RESET}
{Y}{BRIGHT}███████║██║██╔██║╚██║{RESET}
{G}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}
{B}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}
{R}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}
"""

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Stilli ve renkli menüyü gösterir."""
    clear_screen()
    print(banner)

    menu_width = 50 # Menü kutusunun genişliği
    title = "ANA MENÜ"

    # Üst Kenarlık
    print(f"{M}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
    # Başlık Satırı
    print(f"{M}{BRIGHT}║{Y}{BRIGHT}{title.center(menu_width - 2)}{M}{BRIGHT}║{RESET}")
    # Ayırıcı Kenarlık
    print(f"{M}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")
    # Boş Satır
    print(f"{M}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")

    # Menü Öğeleri
    menu_items = {
        '1': "Call Bomb",
        '2': "SMS Bomb",
        '3': "DoS Saldırısı",
        '4': "Netflix Checker",
        '5': "Base64 Decode"
    }

    for key, value in menu_items.items():
        # Öğeyi formatla: "[No] İsim" şeklinde ve ortalanmış boşluklarla
        item_text = f" [{key}] {value} "
        padding_total = menu_width - 2 - len(item_text)
        padding_left = padding_total // 2
        padding_right = padding_total - padding_left
        print(f"{M}{BRIGHT}║{' ' * padding_left}{Y}[{key}]{W} {value}{' ' * padding_right}║{RESET}")

    # Boş Satır
    print(f"{M}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")
    # Ayırıcı
    print(f"{M}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")
    # Çıkış Seçeneği
    exit_text = f" [0] Çıkış "
    padding_total = menu_width - 2 - len(exit_text)
    padding_left = padding_total // 2
    padding_right = padding_total - padding_left
    print(f"{M}{BRIGHT}║{' ' * padding_left}{R}[0]{W} Çıkış{' ' * padding_right}║{RESET}")

    # Alt Kenarlık
    print(f"{M}{BRIGHT}{'╚' + '═' * (menu_width - 2) + '╝'}{RESET}")

    # Seçim istemi
    try:
        choice = input(f"\n{G}{BRIGHT}>> Seçiminizi girin:{W} ")
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()


def run_script(script_name):
    """Belirtilen Python betiğini çalıştırır."""
    try:
        # Betik başlamadan önce bir mesaj göster
        print(f"\n{C}{BRIGHT}--- '{script_name}' başlatılıyor ---{RESET}\n")
        time.sleep(0.5) # Kısa bir bekleme
        python_executable = sys.executable
        # Betiği çalıştır
        subprocess.run([python_executable, script_name], check=True)
        # Betik bittikten sonra mesaj
        print(f"\n{G}{BRIGHT}--- '{script_name}' başarıyla tamamlandı ---{RESET}")
    except FileNotFoundError:
        print(f"\n{R}{BRIGHT}HATA: '{script_name}' dosyası bulunamadı!{RESET}")
        print(f"{Y}Lütfen '{script_name}' dosyasının '{os.path.basename(__file__)}' ile aynı dizinde olduğundan emin olun.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"\n{R}{BRIGHT}HATA: '{script_name}' çalıştırılırken bir sorun oluştu.{RESET}")
        print(f"{Y}Betik muhtemelen bir hata verdi (Çıkış Kodu: {e.returncode}). Betiğin kendi hata mesajlarına bakın.{RESET}")
    except Exception as e:
        print(f"\n{R}{BRIGHT}Beklenmedik bir hata oluştu: {e}{RESET}")

    # Devam etmek için bekle
    print(f"\n{Y}Devam etmek için Enter tuşuna basın...{RESET}")
    try:
        input() # Sadece Enter beklenir
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()

# Ana program akışı
if __name__ == "__main__":
    import time # run_script içinde kullanıldı, buraya da alalım

    while True:
        user_choice = show_menu()

        # Seçime göre betiği çalıştır
        if user_choice == '1':
            run_script("call_bomb.py")
        elif user_choice == '2':
            run_script("sms_bomb.py")
        elif user_choice == '3':
            run_script("DoS.py") # crash.py'nin yeni adı
        elif user_choice == '4':
            # Orijinal netflix dosya adı ('netflix_checker..py') kullanılıyor.
            # Eğer 'netflix_checker.py' olarak değiştirdiyseniz, aşağıdaki satırı güncelleyin.
            run_script("netflix_checker..py")
        elif user_choice == '5':
            run_script("base64decode.py")
        elif user_choice == '0':
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}")
            time.sleep(0.5)
            break
        else:
            print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen menüdeki numaralardan birini girin.{RESET}")
            time.sleep(1.5) # Hata mesajını görmek için bekle
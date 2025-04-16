# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re

# --- UYARI ---
# Bu araç seti çeşitli ağ ve güvenlik araçları içerir.
# Bazı araçlar (Call/SMS Bomb, Jammer, DoS/DDoS) yasa dışı amaçlarla kullanılır ise sorumluluk kullanıcınındır.
# Bu araçların kullanımından doğacak tüm sorumluluk kullanıcıya aittir.
# API'lere dayalı araçlar (Call Bomb) zamanla çalışmaz hale gelebilir.
# --- UYARI SONU ---

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
    M = Fore.MAGENTA # Eflatun
    C = Fore.CYAN    # Camgöbeği
    W = Fore.WHITE
    RESET = Style.RESET_ALL
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""
    class Style: BRIGHT = ""; DIM = ""; RESET_ALL = ""
    class Fore: RED = ""; GREEN = ""; YELLOW = ""; BLUE = ""; MAGENTA = ""; CYAN = ""; WHITE = ""
    class Back: pass


# Banner - Orijinal "401", Parlak Yeşil (Kullanıcının padding'i ile)
banner_padding = " " * 12 # Kullanıcının belirttiği padding
banner = f"""
{banner_padding}{G}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}
{banner_padding}{G}{BRIGHT}██║  ██║██╔═████╗███║{RESET}
{banner_padding}{G}{BRIGHT}███████║██║██╔██║╚██║{RESET}
{banner_padding}{G}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}
{banner_padding}{G}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}
{banner_padding}{G}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}
"""

# Renk kodlarını temizleyen fonksiyon (hizalama için)
def strip_colors(s):
    """ANSI renk/stil kodlarını string'den temizler."""
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Kullanıcının yapısı ve yeni renklerle güncellenmiş menü."""
    clear_screen()
    print(banner)

    menu_width = 55 # <<< Kullanıcının kodundaki genişlik
    title = "401 HACKING TOOL" # Kullanıcının başlığı
    inner_width = menu_width - 4 # İç genişlik: 51

    try:
        # --- Menü Kutusu Başlangıcı (EFLATUN - Magenta) ---
        print(f"{M}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
        # Başlık: Parlak Camgöbeği
        print(f"{M}{BRIGHT}║ {C}{BRIGHT}{title.center(inner_width)} {M}{BRIGHT}║{RESET}")
        print(f"{M}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")
        print(f"{M}{BRIGHT}║{' ' * (inner_width + 2)}║{RESET}") # Boşluk satırı

        # Menü Öğeleri (Kullanıcının yapısı temel alınarak, durumlar güncellendi)
        # Renkler: Numara: Cyan, Metin: Beyaz, Durum: Özel
        menu_items = {
            '1': f"Call Bomb",
            '2': f"SMS Bomb",
            '3': f"DoS Saldırısı {G}(Yenilendi){W}", # Yenilendi yerine daha açıklayıcı
            '4': f"Yedek DDoS {G}(Yeni DDoS aracı){W}", # Yeni araç yerine daha açıklayıcı
            '5': f"Netflix Checker {R}(KULLANIM DIŞI){W}",
            '6': f"Base64 Decode",
            '7': f"IP Toolkit",
            '8': f"Chromecast Hack {Y}(Yakında){W}", # Yeni araç yerine durumu belirt
            '9': f"Web Saldırı Araçları {C}(Yeni){W}", # Yeni araç yerine Framework
            '10': f"Instagram Araçları {C}(Yeni){W}", # Report yerine genel isim
            '11': f"Sosyal Medya Bulucu {C}(Yenilenecek){W}", # Yakında yerine Framework
            '12': f"Wi-Fi Jammer{R}{BRIGHT}(Yakında){W}", # Yakında yerine durumu
            '13': f"DDoS Araçları {C}(Yenilendi){W}" # Yenilendi yerine Framework
        }

        for key, value in menu_items.items():
            num_part_plain = f"[{key}]"
            # Numaralar: Parlak Camgöbeği
            num_part_colored = f"{C}{BRIGHT}{num_part_plain}{W}"

            text_part_colored = value # Metin (durum renkleri dahil)
            text_part_plain = strip_colors(text_part_colored) # Renksiz metin

            visible_item_length = len(num_part_plain) + 1 + len(text_part_plain)
            padding_needed = inner_width - visible_item_length
            item_str_colored = f"{num_part_colored} {text_part_colored}"
            final_padding = ' ' * max(0, padding_needed)

            # Menü satırı (Kutu: Eflatun)
            print(f"{M}{BRIGHT}║ {item_str_colored}{final_padding} {M}{BRIGHT}║{RESET}")

        # Boş Satır ve Ayırıcı (Kutu: Eflatun)
        print(f"{M}{BRIGHT}║{' ' * (inner_width + 2)}║{RESET}")
        print(f"{M}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")

        # Çıkış Seçeneği (Numara: Kırmızı)
        num_part_exit = "[0]"
        text_part_exit = "Çıkış"
        visible_exit_length = len(num_part_exit) + 1 + len(text_part_exit)
        padding_needed_exit = inner_width - visible_exit_length
        item_str_exit_colored = f"{R}{BRIGHT}{num_part_exit}{W} {text_part_exit}"
        final_padding_exit = ' ' * max(0, padding_needed_exit)
        # Menü satırı (Kutu: Eflatun)
        print(f"{M}{BRIGHT}║ {item_str_exit_colored}{final_padding_exit} {M}{BRIGHT}║{RESET}")

        # Alt Kenarlık (Kutu: Eflatun)
        print(f"{M}{BRIGHT}{'╚' + '═' * (menu_width - 2) + '╝'}{RESET}")
        # --- Menü Kutusu Sonu ---

    except Exception as e:
        print(f"\n{R}MENÜ ÇİZİM HATASI:{RESET} {e}")
        return None

    # Seçim istemi (Giriş: Yeşil)
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
    """Belirtilen Python betiğini çalıştırır (Menüyü temizleyerek)."""
    # Ekranı temizle
    clear_screen()

    if not script_name:
        print(f"{R}Çalıştırılacak betik adı belirtilmedi.{RESET}")
        time.sleep(2)
        print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
        try: input()
        except KeyboardInterrupt: sys.exit("\nÇıkılıyor...")
        return

    # Betik var mı diye kontrol et
    if not os.path.exists(script_name):
        print(f"\n{R}{BRIGHT}HATA: '{script_name}' dosyası bulunamadı!{RESET}")
        print(f"{Y}Lütfen '{script_name}' dosyasının '{os.path.basename(__file__)}' ile aynı dizinde olduğundan emin olun.{RESET}")
        time.sleep(3)
        print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
        try: input()
        except KeyboardInterrupt: sys.exit("\nÇıkılıyor...")
        return

    # Başlatma mesajı ve özel kontroller/uyarılar
    print(f"{C}{BRIGHT}--- '{script_name}' başlatılıyor ---{RESET}\n")
    time.sleep(0.5)
    script_cancelled = False

    if script_name == "netflix_checker.py":
         print(f"{R}{BRIGHT}UYARI:{Y} Netflix Checker kullanım dışıdır ve çalışmayacaktır.{RESET}")
         time.sleep(3)
         script_cancelled = True
    elif script_name == "call_bomb.py" or script_name == "sms_bomb.py":
         print(f"{Y}{BRIGHT}UYARI:{W} Bu aracın kullandığı API'ler güncel olmayabilir ve çalışmayabilir.{RESET}")
         print(f"{Y}Ayrıca, bu tür araçların kötüye kullanımı yasa dışıdır.{RESET}")
         time.sleep(2)
    elif script_name in ["DoS.py", "Basit_ddos.py", "DDoS.py"]:
         print(f"{R}{BRIGHT}UYARI:{W} DoS/DDoS araçlarının izinsiz kullanımı yasa dışıdır!{RESET}")
         print(f"{Y}Bu araçları sadece izinli ağlarda test amacıyla kullanın.{RESET}")
         time.sleep(2)
    elif script_name == "wifi_jammer.py":
         print(f"{R}{BRIGHT}!!! YASAL UYARI !!!{RESET}")
         print(f"{R}Wi-Fi Jammer/Deauther araçlarının kullanımı Türkiye dahil birçok ülkede YASA DIŞIDIR.{RESET}")
         print(f"{R}Bu seçeneği çalıştırmak ciddi yasal sonuçlar doğurabilir.{RESET}")
         print(f"{Y}Bu araçlar yalnızca eğitim ve yasal test amaçlıdır. Sorumluluk size aittir.{RESET}")
         try:
            confirm = input(f"{Y}Devam etmek ve '{script_name}' çalıştırmak istiyor musunuz? (e/H): {W}").strip().lower()
            if confirm != 'e':
                print(f"{G}İşlem iptal edildi.{RESET}")
                script_cancelled = True
            else:
                print(f"{R}YASADIŞI OLABİLECEK İŞLEM BAŞLATILIYOR... Sorumluluk sizindir.{RESET}")
                time.sleep(1)
         except KeyboardInterrupt:
             print("\nİptal edildi.")
             script_cancelled = True

    # Betiği çalıştırma (eğer iptal edilmediyse)
    if not script_cancelled:
        try:
            python_executable = sys.executable
            process = subprocess.run([python_executable, script_name], check=False, text=True, capture_output=False)

            if process.returncode == 0:
                 print(f"\n{G}{BRIGHT}--- '{script_name}' işlemi normal şekilde tamamlandı (Çıkış Kodu: 0) ---{RESET}")
            else:
                 print(f"\n{Y}{BRIGHT}--- '{script_name}' işlemi bir sonuçla tamamlandı (Çıkış Kodu: {process.returncode}) ---{RESET}")
                 print(f"{Y}Betik içinde bir hata oluşmuş veya işlem kullanıcı tarafından sonlandırılmış olabilir.{RESET}")

        except FileNotFoundError:
            print(f"\n{R}{BRIGHT}HATA: '{script_name}' veya Python yorumlayıcısı '{python_executable}' bulunamadı!{RESET}")
        except KeyboardInterrupt:
             print(f"\n{Y}İşlem kullanıcı tarafından kesildi ('{script_name}' çalışırken).{RESET}")
             time.sleep(1)
        except Exception as e:
            print(f"\n{R}{BRIGHT}Beklenmedik bir hata oluştu ('{script_name}' çalıştırılırken): {e}{RESET}")
            import traceback
            traceback.print_exc()

    # Her betik çağrısından sonra ana menüye dönmeden önce bekle
    print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()

# Ana program akışı
if __name__ == "__main__":
    try:
        import colorama
    except ImportError:
        pass

    while True:
        user_choice = show_menu()

        if user_choice is None:
            print(f"{R}Menü gösterilirken veya giriş alınırken bir hata oluştu, program sonlandırılıyor.{RESET}")
            time.sleep(3)
            break

        # Kullanıcının menü yapısına göre güncellenmiş script eşleştirmeleri
        script_to_run = None
        if user_choice == '1': script_to_run = "call_bomb.py"
        elif user_choice == '2': script_to_run = "sms_bomb.py"
        elif user_choice == '3': script_to_run = "DoS.py"
        elif user_choice == '4': script_to_run = "Basit_ddos.py"
        elif user_choice == '5': script_to_run = "netflix_checker.py"
        elif user_choice == '6': script_to_run = "base64decode.py"
        elif user_choice == '7': script_to_run = "iptool.py"
        elif user_choice == '8': script_to_run = "chromecast_hack.py" # Düzeltilmiş ad
        elif user_choice == '9': script_to_run = "web_saldırı.py"
        elif user_choice == '10': script_to_run = "insta_saldırı.py" # Kullanıcı report istese de bu betik çağrılıyor
        elif user_choice == '11': script_to_run = "sosyalmedya_bulma.py"
        elif user_choice == '12': script_to_run = "wifi_jammer.py"
        elif user_choice == '13': script_to_run = "DDoS.py"
        elif user_choice == '0':
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}")
            time.sleep(0.5)
            break
        else:
            print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen menüdeki numaralardan birini girin.{RESET}")
            time.sleep(1.5)
            continue

        if script_to_run:
             run_script(script_to_run)
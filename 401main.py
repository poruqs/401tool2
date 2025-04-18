# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re
import base64 # Gerekli olabilir diye kalsın
import codecs # Gerekli olabilir diye kalsın
import traceback # Hata ayıklama için

# --- Renk Tanımları (Senin 401main.py dosyasından) ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    BRIGHT = Style.BRIGHT
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    C = Fore.CYAN
    W = Fore.WHITE
    RESET = Style.RESET_ALL
    # Base64 kodundaki renk isimlerine karşılık gelenler
    pest1 = C  # Menü çerçevesi için
    yellow1 = Y
    red1 = R
    rosy1 = W  # Prompt için
    green1 = G
    coloursoff = RESET
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    BRIGHT = "\033[1m"
    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    C = "\033[96m"
    W = "\033[97m"
    RESET = "\033[0m"
    pest1 = C
    yellow1 = Y
    red1 = R
    rosy1 = W
    green1 = G
    coloursoff = RESET


# --- Banner (Senin 401 ASCII Banner'ın) ---
banner_padding = " " * 12
banner_lines = [
    f"{C}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}",
    f"{C}{BRIGHT}██║  ██║██╔═████╗███║{RESET}",
    f"{C}{BRIGHT}███████║██║██╔██║╚██║{RESET}",
    f"{C}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}",
    f"{C}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}",
    f"{C}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}"
]
author_text = f"{G}{BRIGHT}by 401HackTeam{RESET}"
version_text = f"{Y}Version: 1.1{RESET}"

# --- Menü Öğeleri (Senin güncel listen) ---
# Araçları ve çalıştırılacak dosyaları eşleştiren bir sözlük
tool_map = {
    '1': ("Call Bomb", "call_bomb.py"),
    '2': ("SMS Bomb", "sms_bomb.py"),
    '3': ("DoS Saldırısı", "DoS.py"),
    '4': ("Yedek DDoS", "Basit_ddos.py"),
    '5': ("Base64 Decode", "base64decode.py"),
    '6': ("Chromecast Hack", "choromecast_hack.py"),
    '7': ("Web Saldırı", "web_saldırı.py"),
    '8': ("Instagram Araçları", "insta_saldırı.py"),
    '9': ("Sosyal Medya Bulucu", "sosyalmedya_bulma.py"),
    '10': ("Wi-Fi Jammer", "wifi_jammer.py"),
    '11': ("DDoS Araçları", "DDoS.py"),
    '12': ("Ağ Tünelleme", "ag-tunelleme.py"),
    '13': ("Bilgi Toplayıcı", "bilgitoplayıcı.py"),
    '14': ("Bruteforce Aracı", "brutforce.py"),
    '15': ("GPS Spoofer", "gps-spoofer.py"),
    '16': ("Kamera Görüntüleme", "kamera_goruntuleme.py"),
    '17': ("Log/Phishing/FakeAPK", "keylogger.py"),
    '18': ("Konum Takip", "konum_takip.py"),
    '19': ("Özel Link Kısaltıcı", "ozellink_kısaltıcı.py"),
    '20': ("Pattern Kırıcı", "pattern-braker.py"),
    '21': ("SIM Klonlayıcı", "sim-clone.py"),
    '22': ("IP/Site Dönüştürücü", "webip_tool.py"),
    '23': ("WiFi Şifre Kırıcı", "wifipass_breaker.py"),
    '24': ("WhatsApp Analiz", "wp-analizer.py"),
    '25': ("Yedek Wi-Fi Jammer", "yedek_jammer.py")
}
# Çıkış seçeneği
exit_option = '0'
exit_text = "Çıkış"

# --- Yardımcı Fonksiyonlar ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================================================================
# SHOW_MENU (Base64 yapısına benzer, büyük input metni ile)
# ==================================================================
def show_menu_and_get_input():
    """Menüyü gösterir ve kullanıcıdan girdi alır."""
    clear_screen()

    # Banner ve alt bilgileri yazdır
    print()
    for line in banner_lines:
        print(f"{banner_padding}{line}")
    sub_padding = banner_padding + "   "
    print(f"{sub_padding}{author_text}")
    print(f"{sub_padding}{version_text}")
    print()

    # Menü metnini dinamik olarak oluştur
    # Base64'teki yapıya benzetmeye çalışalım (13 satır, 2 sütun)
    menu_lines = []
    items = list(tool_map.items())
    num_items = len(items)
    num_rows = 13 # Sabit 13 satır (25/2 ~ 13)

    for i in range(num_rows):
        # Sol Sütun
        left_key = str(i + 1)
        left_text = ""
        if left_key in tool_map:
            left_name = tool_map[left_key][0]
            left_text = f"{W}{left_key.rjust(2)}.{C} {left_name}{RESET}"
        # Sütun genişliğini ayarlamak için renksiz uzunluğu alıp boşluk ekleyebiliriz,
        # ama base64 stili daha çok hizalamaya dayanıyor gibiydi. Şimdilik basit tutalım.
        # Sol sütun için sabit bir genişlik (örneğin 30 karakter) belirleyelim
        left_text_len = len(re.sub(r'\x1b\[[0-9;]*[mK]', '', left_text))
        left_padding = ' ' * max(0, 30 - left_text_len)
        left_col = left_text + left_padding

        # Sağ Sütun
        right_key = str(i + 1 + num_rows) # 14, 15, ..., 26
        right_text = ""
        if right_key in tool_map:
            right_name = tool_map[right_key][0]
            right_text = f"{W}{right_key.rjust(2)}.{C} {right_name}{RESET}"
        # Sağ sütun için de padding eklenebilir ama gerek yok gibi.

        menu_lines.append(f"\t{pest1}|{coloursoff} {left_col}{pest1}|{coloursoff} {right_text}")

    # Çıkış seçeneğini ekle (Base64'teki gibi ayrı bir satırda)
    exit_line = f"\t{pest1}|{coloursoff} {W}{exit_option.rjust(2)}.{R} {exit_text}{RESET}"

    # Tüm menü metnini birleştir
    menu_string = "\n".join([
        f"\t{pest1}============================================================={coloursoff}", # Üst Çerçeve
        *menu_lines, # Araç Satırları
        # Base64'teki gibi bir boşluk satırı ekleyelim
        f"\t{pest1}|{coloursoff} {' ' * 58}{pest1}|{coloursoff}",
        exit_line.ljust(60 + len(pest1)*2 + len(coloursoff)*2) + f"{pest1}|{coloursoff}", # Çıkış Satırı (Hizalama için ljust)
        f"\t{pest1}============================================================={coloursoff}", # Alt Çerçeve
        f"\n{rosy1}Enter Your Option: {coloursoff}" # Prompt
    ])

    # Menüyü göster ve input al
    try:
        choice = input(menu_string)
        return choice.strip()
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()
    except Exception as e:
        print(f"\n{R}GİRİŞ HATASI ({type(e).__name__}):{RESET} {e}")
        traceback.print_exc()
        time.sleep(3)
        return None

# ==================================================================
# RUN_SCRIPT (Senin 401main.py dosyasından, Hata Yakalama ile)
# ==================================================================
def run_script(script_name):
    try: # run_script fonksiyonu için genel hata yakalama
        clear_screen()

        if not script_name:
            print(f"{R}Çalıştırılacak betik adı belirtilmedi.{RESET}")
            time.sleep(2)
            print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
            try: input()
            except KeyboardInterrupt: sys.exit("\nÇıkılıyor...")
            return

        script_path = os.path.join(os.path.dirname(__file__), script_name)
        if not os.path.exists(script_path):
            print(f"\n{R}{BRIGHT}HATA: '{script_name}' dosyası bulunamadı!{RESET}")
            print(f"{Y}Lütfen '{script_name}' dosyasının '{os.path.basename(__file__)}' ile aynı dizinde olduğundan emin olun.{RESET}")
            time.sleep(3)
            print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
            try: input()
            except KeyboardInterrupt: sys.exit("\nÇıkılıyor...")
            return

        print(f"{C}{BRIGHT}--- '{script_name}' başlatılıyor ---{RESET}\n")
        time.sleep(0.5)
        script_cancelled = False
        requires_root = False

        # --- YASAL UYARILAR ve ÖN KONTROLLER ---
        if script_name == "netflix_checker.py":
             print(f"{R}{BRIGHT}UYARI:{Y} Netflix Checker kullanım dışıdır.{RESET}"); time.sleep(3); script_cancelled = True
        elif script_name in ["call_bomb.py", "sms_bomb.py"]:
             print(f"{Y}{BRIGHT}UYARI:{W} API'ler güncel olmayabilir. Kötüye kullanım yasa dışıdır.{RESET}"); time.sleep(2)
        elif script_name in ["DoS.py", "Basit_ddos.py", "DDoS.py", "brutforce.py", "keylogger.py"]:
             print(f"{R}{BRIGHT}!!! YASAL UYARI !!!{RESET}")
             print(f"{R}İzinsiz kullanım YASA DIŞIDIR! Sadece izinli test yapın.{RESET}"); time.sleep(3)
        elif script_name in ["wifi_jammer.py", "yedek_jammer.py", "sim-clone.py", "gps-spoofer.py"]:
             print(f"{R}{BRIGHT}!!! YASAL UYARI ve GEREKSİNİMLER !!!{RESET}")
             print(f"{R}Bu aracın ({script_name}) kullanımı YASA DIŞIDIR!{RESET}")
             if script_name in ["wifi_jammer.py", "yedek_jammer.py"]: print(f"{Y}Özel donanım ve root yetkisi gerektirir.{RESET}"); requires_root = True
             if script_name == "sim-clone.py": print(f"{Y}'qcsuper' ve özel donanım/izinler gerektirir.{RESET}")
             if script_name == "gps-spoofer.py": print(f"{Y}'gpsd' ve konum izinleri gerektirir.{RESET}")
             print(f"{Y}Sadece eğitim amaçlıdır. Sorumluluk size aittir.{RESET}")
             try:
                confirm = input(f"{Y}Devam etmek istiyor musunuz? (e/H): {W}").strip().lower()
                if confirm != 'e': print(f"{G}İşlem iptal edildi.{RESET}"); script_cancelled = True
                else: print(f"{R}YASADIŞI OLABİLECEK İŞLEM BAŞLATILIYOR...{RESET}"); time.sleep(1)
             except KeyboardInterrupt: print("\nİptal edildi."); script_cancelled = True; time.sleep(1)
        elif script_name in ["kamera_goruntuleme.py", "bilgitoplayıcı.py", "konum_takip.py", "wifipass_breaker.py"]:
            print(f"{Y}UYARI:{W} Bu araç Termux API gerektirebilir.{RESET}"); time.sleep(2)
        elif script_name == "pattern-braker.py": print(f"{Y}UYARI:{W} PyOpenCL/NumPy ve GPU gerektirebilir.{RESET}"); time.sleep(2)
        elif script_name == "wp-analizer.py": print(f"{Y}UYARI:{W} Pandas/Pillow/Matplotlib ve WhatsApp DB erişimi gerektirir.{RESET}"); time.sleep(2)
        elif script_name == "ag-tunelleme.py": print(f"{Y}UYARI:{W} PyCryptodome/sshtunnel/paramiko gerektirir.{RESET}"); time.sleep(2)

        # Betiği çalıştırma
        if not script_cancelled:
            try:
                python_executable = sys.executable
                command = []
                if requires_root and os.name != 'nt':
                     try: is_root = (os.geteuid() == 0)
                     except AttributeError: is_root = False
                     if not is_root:
                         print(f"{Y}Root yetkisi gerekiyor, 'sudo' kullanılıyor...{RESET}")
                         command.append("sudo")
                command.extend([python_executable, script_path])

                print(f"{G}Komut çalıştırılıyor: {' '.join(command)}{RESET}")
                # Betiği çalıştır (Popen yerine run kullanmak daha basit olabilir)
                process = subprocess.run(command, check=False, text=True)

                if process.returncode != 0:
                     print(f"{Y}Uyarı: '{script_name}' betiği {process.returncode} çıkış kodu ile bitti.{RESET}")

            except FileNotFoundError:
                 print(f"{R}{BRIGHT}HATA: '{python_executable}' veya 'sudo' komutu bulunamadı.{RESET}")
                 traceback.print_exc()
            except PermissionError:
                 print(f"{R}{BRIGHT}HATA: '{script_name}' betiğini çalıştırma izni yok.{RESET}")
                 traceback.print_exc()
            except Exception as e:
                 print(f"\n{R}{BRIGHT}Betik çalıştırılırken hata oluştu ('{script_name}'):{RESET}\n{e}")
                 traceback.print_exc()

    except Exception as outer_run_err:
        print(f"\n{R}{BRIGHT}KRİTİK run_script HATASI:{RESET}")
        print(f"{R}Hata: {outer_run_err}{RESET}")
        traceback.print_exc()

    # Ana menüye dönmek için bekle
    print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()


# Ana program akışı
if __name__ == "__main__":
    try:
        # Colorama kontrolü
        try: import colorama
        except ImportError: pass

        while True:
            user_choice = show_menu_and_get_input() # Yeni menü fonksiyonunu çağır

            if user_choice is None:
                print(f"{Y}Giriş alınamadı veya menü hatası. Tekrar deneniyor...{RESET}")
                time.sleep(2)
                continue

            # Seçimi işle
            if user_choice == exit_option: # Çıkış ('0')
                clear_screen()
                print(f"\n{R}{BRIGHT}╔═══════════════════════════════════╗")
                print(f"║    {Y}401HackTeam Tool Kapatılıyor...{R}    ║")
                print(f"╚═══════════════════════════════════╝{RESET}\n")
                time.sleep(1)
                break # Döngüden çık
            elif user_choice in tool_map:
                tool_name, script_file = tool_map[user_choice]
                run_script(script_file)
            else:
                print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen listeden bir numara girin.{RESET}")
                time.sleep(1.5)
                # continue demeye gerek yok, döngü zaten devam edecek

    except KeyboardInterrupt: # Ana döngüde Ctrl+C yakala
        print("\n\nProgram sonlandırılıyor...")
    except Exception as main_err:
        print(f"\n{R}{BRIGHT}KRİTİK PROGRAM HATASI ({type(main_err).__name__}):{RESET} {main_err}")
        traceback.print_exc()
        input(f"{Y}Çıkmak için Enter'a basın...{RESET}")

    finally:
        print(f"{B}Program sonlandı.{RESET}")
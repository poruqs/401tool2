# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re
import base64
import codecs
import traceback # Hata ayıklama için
import shutil # Terminal genişliği için

# --- Renk Tanımları (er.jpg stiline uygun) ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    BRIGHT = Style.BRIGHT ; R = Fore.RED ; G = Fore.GREEN ; Y = Fore.YELLOW
    C = Fore.CYAN ; W = Fore.WHITE ; RESET = Style.RESET_ALL
    pest1 = C ; yellow1 = Y ; red1 = R ; rosy1 = Fore.MAGENTA
    green1 = G ; white1 = W ; coloursoff = RESET
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli ('pip install colorama').")
    BRIGHT = "\033[1m" ; R = "\033[91m" ; G = "\033[92m" ; Y = "\033[93m"
    C = "\033[96m" ; W = "\033[97m" ; RESET = "\033[0m"
    pest1 = C ; yellow1 = Y ; red1 = R ; rosy1 = "\033[95m" # Magenta
    green1 = G ; white1 = W ; coloursoff = RESET


# --- Banner (Senin 401 ASCII Banner'ın) ---
banner_lines = [
    f"{C}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}",
    f"{C}{BRIGHT}██║  ██║██╔═████╗███║{RESET}",
    f"{C}{BRIGHT}███████║██║██╔██║╚██║{RESET}",
    f"{C}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}",
    f"{C}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}",
    f"{C}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}"
]
author_text = f"{green1}by 401HackTeam{coloursoff}" # Yeşil
version_text = f"{yellow1}Version: 1.1{coloursoff}" # Sarı

# --- Menü Öğeleri (Senin güncel listen) ---
tool_map = {
    '1': ("Call Bomb", "call_bomb.py"), '2': ("SMS Bomb", "sms_bomb.py"),
    '3': ("DoS Saldırısı", "DoS.py"), '4': ("Yedek DDoS", "Basit_ddos.py"),
    '5': ("Base64 Decode", "base64decode.py"), '6': ("Chromecast Hack", "choromecast_hack.py"),
    '7': ("Web Saldırı", "web_saldırı.py"), '8': ("Instagram Araçları", "insta_saldırı.py"),
    '9': ("Sosyal Medya Bulucu", "sosyalmedya_bulma.py"), '10': ("Wi-Fi Jammer", "wifi_jammer.py"),
    '11': ("DDoS Araçları", "DDoS.py"), '12': ("Ağ Tünelleme", "ag-tunelleme.py"),
    '13': ("Bilgi Toplayıcı", "bilgitoplayıcı.py"), '14': ("Bruteforce Aracı", "brutforce.py"),
    '15': ("GPS Spoofer", "gps-spoofer.py"), '16': ("Kamera Görüntüleme", "kamera_goruntuleme.py"),
    '17': ("Log/Phishing/FakeAPK", "keylogger.py"), '18': ("Konum Takip", "konum_takip.py"),
    '19': ("Özel Link Kısaltıcı", "ozellink_kısaltıcı.py"), '20': ("Pattern Kırıcı", "pattern-braker.py"),
    '21': ("SIM Klonlayıcı", "sim-clone.py"), '22': ("IP/Site Dönüştürücü", "webip_tool.py"),
    '23': ("WiFi Şifre Kırıcı", "wifipass_breaker.py"), '24': ("WhatsApp Analiz", "wp-analizer.py"),
    '25': ("Yedek Wi-Fi Jammer", "yedek_jammer.py")
}
exit_option = '0'
exit_text = "Exit"

# --- Yardımcı Fonksiyonlar ---
def strip_colors(s):
    try: return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))
    except Exception as e: print(f"{R}strip_colors HATA: {e}{RESET}"); return str(s)

def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_width(default=80):
    try:
        columns, _ = shutil.get_terminal_size()
        return max(40, columns - 2) # Min 40 genişlik
    except OSError: return default

# ==================================================================
# TEK SÜTUNLU, ORTALANMIŞ, KOMPAKT MENÜ (DAR EKRANLAR İÇİN)
# ==================================================================
def show_menu_single_column_centered(terminal_width):
    """Dar ekranlar için tek sütunlu, ortalanmış menü."""
    try:
        # --- Genişlik Hesaplama ---
        max_item_len_no_color = 0
        for key, (name, _) in tool_map.items():
            item_text_for_len = f"{key.rjust(2)}. {name}"
            max_item_len_no_color = max(max_item_len_no_color, len(item_text_for_len))
        exit_text_for_len = f"{exit_option.rjust(2)}. {exit_text}"
        max_item_len_no_color = max(max_item_len_no_color, len(exit_text_for_len))

        inner_width = max_item_len_no_color + 2
        frame_width = inner_width + 2
        frame_char = "="
        frame_line = f"{pest1}{frame_char * frame_width}{coloursoff}"
        left_padding_str = " " * max(0, (terminal_width - frame_width) // 2)

        # --- Menüyü Yazdır ---
        print(f"{left_padding_str}{frame_line}") # Üst çerçeve
        for key, (name, _) in tool_map.items():
            item_text_raw = f"{yellow1}{key.rjust(2)}{white1}.{pest1}{name}{coloursoff}"
            item_len_no_color = len(strip_colors(item_text_raw))
            end_padding = ' ' * max(0, inner_width - item_len_no_color)
            print(f"{left_padding_str}{pest1}| {item_text_raw}{end_padding} {pest1}|{coloursoff}")

        exit_num_str = exit_option.rjust(2)
        exit_text_formatted = f"{yellow1}{exit_num_str}{white1}.{red1}{exit_text}{coloursoff}"
        exit_len_no_color = len(strip_colors(exit_text_formatted))
        exit_inner_padding = ' ' * max(0, inner_width - exit_len_no_color)
        print(f"{left_padding_str}{pest1}|{exit_inner_padding}{exit_text_formatted} {pest1}|{coloursoff}")
        print(f"{left_padding_str}{frame_line}") # Alt çerçeve

    except Exception as single_col_err:
        print(f"\n{R}Tek Sütunlu Menü Hatası: {single_col_err}{RESET}")
        traceback.print_exc()

# ==================================================================
# ADAPTİF MENÜ GÖSTERME FONKSİYONU
# ==================================================================
def show_adaptive_menu():
    """Ekran genişliğine göre çift veya tek sütunlu menü gösterir."""
    try:
        clear_screen()
        terminal_width = get_terminal_width()

        # --- Banner ve Alt Başlıkları Ortala ve Yazdır ---
        print("\n")
        for line in banner_lines:
             banner_len_no_color = len(strip_colors(line))
             banner_padding_str = " " * max(0, (terminal_width - banner_len_no_color) // 2)
             print(f"{banner_padding_str}{line}")
        author_len = len(strip_colors(author_text))
        version_len = len(strip_colors(version_text))
        print(f"{' ' * max(0, (terminal_width - author_len)//2)}{author_text}")
        print(f"{' ' * max(0, (terminal_width - version_len)//2)}{version_text}")
        print("\n")

        # --- Çift Sütun İçin Minimum Genişliği Hesapla ---
        items = list(tool_map.items())
        num_rows = 13 # Çift sütun için 13 satır gerekir (25 araç için)

        # Her sütundaki en uzun öğenin renksiz uzunluğunu bul
        max_len_col1_no_color = 0
        for i in range(num_rows): # Sol sütun (1-13)
            key = str(i + 1)
            if key in tool_map:
                item_text_for_len = f"{key.rjust(2)}. {tool_map[key][0]}"
                max_len_col1_no_color = max(max_len_col1_no_color, len(item_text_for_len))

        max_len_col2_no_color = 0
        for i in range(num_rows): # Sağ sütun (14-25)
            key = str(i + 1 + num_rows)
            if key in tool_map:
                item_text_for_len = f"{key.rjust(2)}. {tool_map[key][0]}"
                max_len_col2_no_color = max(max_len_col2_no_color, len(item_text_for_len))

        col_spacing = 3 # Sütun arası boşluk (minimal)
        required_inner_width = max_len_col1_no_color + col_spacing + max_len_col2_no_color
        required_frame_width = required_inner_width + 4 # | Boşluk İçerik Boşluk |

        # --- Karar Ver: Çift Sütun mu, Tek Sütun mu? ---
        if required_frame_width <= terminal_width:
            # ---- EKRAN YETERİNCE GENİŞ: ÇİFT SÜTUNLU GÖSTER ----
            print(f"{Y}[Bilgi] Ekran genişliği yeterli, çift sütunlu menü gösteriliyor.{RESET}")
            time.sleep(0.5) # Kullanıcı görsün diye kısa bekleme
            frame_char = "="
            frame_line = f"{pest1}{frame_char * required_frame_width}{coloursoff}"
            left_padding_str = " " * max(0, (terminal_width - required_frame_width) // 2)

            print(f"{left_padding_str}{frame_line}") # Üst çerçeve

            for i in range(num_rows):
                # Sol Sütun
                left_key = str(i + 1)
                left_text_raw = "" ; left_len_no_color = 0
                if left_key in tool_map:
                    left_name = tool_map[left_key][0]
                    left_text_raw = f"{yellow1}{left_key.rjust(2)}{white1}.{pest1}{left_name}{coloursoff}"
                    left_len_no_color = len(strip_colors(left_text_raw))
                left_padding = ' ' * max(0, max_len_col1_no_color - left_len_no_color)
                left_col_formatted = left_text_raw + left_padding

                # Sağ Sütun
                right_key = str(i + 1 + num_rows)
                right_text_raw = "" ; right_len_no_color = 0
                if right_key in tool_map:
                    right_name = tool_map[right_key][0]
                    right_text_raw = f"{yellow1}{right_key.rjust(2)}{white1}.{pest1}{right_name}{coloursoff}"
                    # Sağ sütun için padding hesaplamaya gerek yok, satır sonu halleder

                # Satırı Birleştir ve Hizala
                line_content = f"{left_col_formatted}{' ' * col_spacing}{right_text_raw}"
                line_len_no_color = len(strip_colors(line_content))
                end_padding = ' ' * max(0, required_inner_width - line_len_no_color)
                print(f"{left_padding_str}{pest1}| {line_content}{end_padding} {pest1}|{coloursoff}")

            # Çıkış Seçeneği
            exit_num_str = exit_option.rjust(2)
            exit_text_formatted = f"{yellow1}{exit_num_str}{white1}.{red1}{exit_text}{coloursoff}"
            exit_len_no_color = len(strip_colors(exit_text_formatted))
            exit_padding = ' ' * max(0, required_inner_width - exit_len_no_color)
            print(f"{left_padding_str}{pest1}|{exit_padding}{exit_text_formatted} {pest1}|{coloursoff}")

            print(f"{left_padding_str}{frame_line}") # Alt çerçeve

        else:
            # ---- EKRAN DAR: TEK SÜTUNLU GÖSTER ----
            print(f"{Y}[Bilgi] Ekran genişliği dar, tek sütunlu menü gösteriliyor.{RESET}")
            time.sleep(0.5) # Kullanıcı görsün diye kısa bekleme
            show_menu_single_column_centered(terminal_width) # Tek sütunlu fonksiyonu çağır

        # --- Prompt (Her iki durumda da gösterilir) ---
        try:
            prompt_text = f"{rosy1}Enter Your Option: {coloursoff}"
            prompt_len = len("Enter Your Option: ")
            prompt_padding_str = " " * max(0, (terminal_width - prompt_len) // 2)
            choice = input(f"\n{prompt_padding_str}{prompt_text}")
            return choice.strip()
        except KeyboardInterrupt: sys.exit("\n\nÇıkış yapılıyor...")
        except Exception as e: print(f"\n{R}GİRİŞ HATASI: {e}{RESET}"); traceback.print_exc(); time.sleep(3); return None

    # --- Hata Yakalama ---
    except Exception as menu_err:
        print(f"\n{R}{BRIGHT}KRİTİK ADAPTİF MENÜ HATASI:{RESET}\n{menu_err}"); traceback.print_exc()
        print(f"{Y}Menü görüntülenemedi.{RESET}"); time.sleep(5); sys.exit(1)


# ==================================================================
# RUN_SCRIPT (Değişiklik Yok)
# ==================================================================
def run_script(script_name):
    # Bu fonksiyon önceki cevapta olduğu gibi kalabilir.
    try:
        clear_screen()

        if not script_name:
            print(f"{R}Çalıştırılacak betik adı belirtilmedi.{RESET}")
            time.sleep(2); input(f"\n{Y}Ana menüye dönmek için Enter...{RESET}"); return
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        if not os.path.exists(script_path):
            print(f"\n{R}{BRIGHT}HATA: '{script_name}' bulunamadı!{RESET}")
            time.sleep(3); input(f"\n{Y}Ana menüye dönmek için Enter...{RESET}"); return

        print(f"{C}{BRIGHT}--- '{script_name}' başlatılıyor ---{RESET}\n"); time.sleep(0.5)
        script_cancelled = False; requires_root = False

        # --- YASAL UYARILAR (Önceki koddan alındı) ---
        if script_name == "netflix_checker.py": print(f"{R}{BRIGHT}UYARI:{Y} Netflix Checker kullanım dışıdır.{RESET}"); time.sleep(3); script_cancelled = True
        elif script_name in ["call_bomb.py", "sms_bomb.py"]: print(f"{Y}{BRIGHT}UYARI:{W} API'ler güncel olmayabilir. Kötüye kullanım yasa dışıdır.{RESET}"); time.sleep(2)
        elif script_name in ["DoS.py", "Basit_ddos.py", "DDoS.py", "brutforce.py", "keylogger.py"]: print(f"{R}{BRIGHT}!!! YASAL UYARI !!!{RESET}\n{R}İzinsiz kullanım YASA DIŞIDIR!{RESET}"); time.sleep(3)
        elif script_name in ["wifi_jammer.py", "yedek_jammer.py", "sim-clone.py", "gps-spoofer.py"]:
            print(f"{R}{BRIGHT}!!! YASAL UYARI ve GEREKSİNİMLER !!!{RESET}\n{R}Bu aracın kullanımı YASA DIŞIDIR!{RESET}")
            if script_name in ["wifi_jammer.py", "yedek_jammer.py"]: print(f"{Y}Özel donanım ve root yetkisi gerektirir.{RESET}"); requires_root = True
            if script_name == "sim-clone.py": print(f"{Y}'qcsuper' ve özel donanım/izinler gerektirir.{RESET}")
            if script_name == "gps-spoofer.py": print(f"{Y}'gpsd' ve konum izinleri gerektirir.{RESET}")
            print(f"{Y}Sadece eğitim amaçlıdır. Sorumluluk size aittir.{RESET}")
            try:
                confirm = input(f"{Y}Devam etmek istiyor musunuz? (e/H): {W}").strip().lower()
                if confirm != 'e': print(f"{G}İşlem iptal edildi.{RESET}"); script_cancelled = True
                else: print(f"{R}YASADIŞI OLABİLECEK İŞLEM BAŞLATILIYOR...{RESET}"); time.sleep(1)
            except KeyboardInterrupt: print("\nİptal edildi."); script_cancelled = True; time.sleep(1)
        elif script_name in ["kamera_goruntuleme.py", "bilgitoplayıcı.py", "konum_takip.py", "wifipass_breaker.py"]: print(f"{Y}UYARI:{W} Termux API gerektirebilir.{RESET}"); time.sleep(2)
        elif script_name == "pattern-braker.py": print(f"{Y}UYARI:{W} PyOpenCL/NumPy ve GPU gerektirebilir.{RESET}"); time.sleep(2)
        elif script_name == "wp-analizer.py": print(f"{Y}UYARI:{W} Pandas/Pillow/Matplotlib ve WhatsApp DB erişimi gerektirir.{RESET}"); time.sleep(2)
        elif script_name == "ag-tunelleme.py": print(f"{Y}UYARI:{W} PyCryptodome/sshtunnel/paramiko gerektirir.{RESET}"); time.sleep(2)

        # Betiği çalıştırma
        if not script_cancelled:
            try:
                python_executable = sys.executable; command = []
                if requires_root and os.name != 'nt':
                    try: is_root = (os.geteuid() == 0)
                    except AttributeError: is_root = False
                    if not is_root: print(f"{Y}Root yetkisi gerekiyor, 'sudo' kullanılıyor...{RESET}"); command.append("sudo")
                command.extend([python_executable, script_path])
                print(f"{G}Komut çalıştırılıyor: {' '.join(command)}{RESET}")
                process = subprocess.run(command, check=False, text=True)
                if process.returncode != 0: print(f"{Y}Uyarı: '{script_name}' betiği {process.returncode} çıkış kodu ile bitti.{RESET}")
            except FileNotFoundError: print(f"{R}{BRIGHT}HATA: '{python_executable}' veya 'sudo' bulunamadı.{RESET}"); traceback.print_exc()
            except PermissionError: print(f"{R}{BRIGHT}HATA: '{script_name}' çalıştırma izni yok.{RESET}"); traceback.print_exc()
            except Exception as e: print(f"\n{R}{BRIGHT}Betik çalıştırılırken hata oluştu:{RESET}\n{e}"); traceback.print_exc()
    except Exception as outer_run_err: print(f"\n{R}{BRIGHT}KRİTİK run_script HATASI:{RESET}\n{outer_run_err}"); traceback.print_exc()

    print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
    try: input()
    except KeyboardInterrupt: print("\n\nÇıkış yapılıyor..."); sys.exit()


# Ana program akışı
if __name__ == "__main__":
    try:
        try: import colorama
        except ImportError: pass

        while True:
            user_choice = show_adaptive_menu() # Adaptif menü fonksiyonunu çağır

            if user_choice is None: continue # Menüde hata olduysa döngüye devam et

            if user_choice == exit_option: # Çıkış ('0')
                clear_screen(); print(f"\n{R}{BRIGHT}╔═══════════════════════════════════╗\n║    {Y}401HackTeam Tool Kapatılıyor...{R}    ║\n╚═══════════════════════════════════╝{RESET}\n"); time.sleep(1); break
            elif user_choice in tool_map: run_script(tool_map[user_choice][1])
            else: print(f"\n{R}{BRIGHT}Geçersiz seçim!{RESET}"); time.sleep(1.5)

    except KeyboardInterrupt: print("\n\nProgram sonlandırılıyor...")
    except Exception as main_err: print(f"\n{R}{BRIGHT}KRİTİK HATA:{RESET}\n{main_err}"); traceback.print_exc(); input(f"{Y}Çıkmak için Enter...{RESET}")
    finally:
        # colorama kullanılıyorsa deinit yapmak iyi olabilir, ama autoreset=True ile gerek yok gibi.
        print(f"{RESET}Program sonlandı.") # Renkleri sıfırla
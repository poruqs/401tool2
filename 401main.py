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
    # colorama kütüphanesini kullanmayı dene
    from colorama import init, Fore, Style
    init(autoreset=True) # Her print sonrası renkleri sıfırla
    BRIGHT = Style.BRIGHT ; R = Fore.RED ; G = Fore.GREEN ; Y = Fore.YELLOW
    C = Fore.CYAN ; W = Fore.WHITE ; RESET = Style.RESET_ALL
    # Renk değişkenlerini tanımla
    pest1 = C ; yellow1 = Y ; red1 = R ; rosy1 = Fore.MAGENTA
    green1 = G ; white1 = W ; coloursoff = RESET
except ImportError:
    # colorama yoksa manuel ANSI kodlarını kullan
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
# Banner altı metinleri
author_text = f"{green1}by 401HackTeam{coloursoff}" # Yeşil
version_text = f"{yellow1}Version: 1.2{coloursoff}" # Sarı, Güncel versiyon

# --- Menü Öğeleri (Türkçe İsimler ve Çalıştırılacak Dosyalar) ---
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
    '17': ("Phishing Aracı", "keylogger.py"),
    '18': ("Konum Takip", "konum_takip.py"),
    '19': ("Özel Link Kısaltıcı", "ozellink_kısaltıcı.py"),
    '20': ("Pattern Kırıcı", "pattern-braker.py"),
    '21': ("SIM Klonlayıcı", "sim-clone.py"),
    '22': ("IP/Site Dönüştürücü", "webip_tool.py"),
    '23': ("WiFi Şifre Kırıcı", "wifipass_breaker.py"),
    '24': ("WhatsApp Analiz", "wp-analizer.py"),
    '25': ("Yedek Wi-Fi Jammer", "yedek_jammer.py")
}
exit_option = '0'
exit_text = "Exit"

# --- Yardımcı Fonksiyonlar ---
def strip_colors(s):
    """ANSI renk kodlarını string'den temizler."""
    try: return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))
    except Exception as e: print(f"{R}strip_colors ERROR: {e}{RESET}"); return str(s)

def clear_screen():
    """İşletim sistemine uygun ekran temizleme komutunu çalıştırır."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_width(default=80):
    """Terminal genişliğini alır, alamazsa varsayılanı döndürür."""
    try:
        columns, _ = shutil.get_terminal_size()
        return max(40, columns)
    except OSError:
        return default

# ==================================================================
# FİNAL MENÜ FONKSİYONU (Prompt Sola Hizalı)
# ==================================================================
def show_menu_final():
    """Menüyü 13/12 bölünmüş, çift sütunlu, sıkıştırılmış ve ortalanmış gösterir."""
    try:
        clear_screen()
        terminal_width = get_terminal_width()

        # --- Sabitler ve Hesaplamalar ---
        num_rows = 13 ; col_spacing = 2

        # --- Sütun Genişliklerini Hesapla ---
        max_len_col1_no_color = 0
        keys_col1 = [str(k) for k in range(1, num_rows + 1)]
        for key in keys_col1:
            if key in tool_map:
                item_text_for_len = f"{key.rjust(2)}. {tool_map[key][0]}"
                max_len_col1_no_color = max(max_len_col1_no_color, len(strip_colors(item_text_for_len)))

        max_len_col2_no_color = 0
        keys_col2 = [str(k) for k in range(num_rows + 1, num_rows * 2 + 1)]
        for key in keys_col2:
            if key in tool_map:
                item_text_for_len = f"{key.rjust(2)}. {tool_map[key][0]}"
                max_len_col2_no_color = max(max_len_col2_no_color, len(strip_colors(item_text_for_len)))

        # --- Çerçeve Boyutunu Hesapla ---
        required_inner_width = max_len_col1_no_color + col_spacing + max_len_col2_no_color
        frame_width = required_inner_width + 2
        frame_char = "="
        frame_line = f"{pest1}{frame_char * frame_width}{coloursoff}"
        left_padding_str = " " * max(0, (terminal_width - frame_width) // 2)

        # --- Banner/Başlık (Ortalanmış) ---
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

        # --- Menü Çerçevesi ve İçeriği (Ortalanmış) ---
        print(f"{left_padding_str}{frame_line}") # Üst çerçeve

        for i in range(num_rows):
            # Sol Sütun (1-13)
            left_key = str(i + 1)
            left_text_raw = "" ; left_len_no_color = 0
            if left_key in tool_map:
                left_name = tool_map[left_key][0]
                left_text_raw = f"{yellow1}{left_key.rjust(2)}{white1}.{pest1}{left_name}{coloursoff}"
                left_len_no_color = len(strip_colors(left_text_raw))
            left_padding = ' ' * max(0, max_len_col1_no_color - left_len_no_color)
            left_col_formatted = left_text_raw + left_padding

            # Sağ Sütun (14-25)
            right_key = str(i + 1 + num_rows)
            right_text_raw = ""
            if right_key in tool_map:
                right_name = tool_map[right_key][0]
                right_text_raw = f"{yellow1}{right_key.rjust(2)}{white1}.{pest1}{right_name}{coloursoff}"

            # Satırı Birleştir ve Hizala
            line_content = f"{left_col_formatted}{' ' * col_spacing}{right_text_raw}"
            line_len_no_color = len(strip_colors(line_content))
            end_padding = ' ' * max(0, required_inner_width - line_len_no_color)
            print(f"{left_padding_str}{pest1}|{line_content}{end_padding}{pest1}|{coloursoff}")

        # Çıkış Seçeneği (Sağa Yaslı)
        exit_num_str = exit_option.rjust(2)
        exit_text_formatted = f"{yellow1}{exit_num_str}{white1}.{red1}{exit_text}{coloursoff}"
        exit_len_no_color = len(strip_colors(exit_text_formatted))
        exit_padding = ' ' * max(0, required_inner_width - exit_len_no_color)
        print(f"{left_padding_str}{pest1}|{exit_padding}{exit_text_formatted}{pest1}|{coloursoff}")

        print(f"{left_padding_str}{frame_line}") # Alt çerçeve

        # --- Prompt (Sola, çerçeve ile hizalı) --- ### DEĞİŞİKLİK BURADA ###
        try:
            prompt_text = f"{rosy1}Enter Your Option: {coloursoff}"
            # Ortalamak yerine sol çerçeve padding'ini kullan
            choice = input(f"\n{left_padding_str}{prompt_text}") # prompt_padding_str kaldırıldı, left_padding_str kullanıldı
            return choice.strip()
        except KeyboardInterrupt: sys.exit(f"\n\n{Y}+401 hack tool kapatıldı...{RESET}")
        except Exception as e: print(f"\n{R}INPUT ERROR: {e}{RESET}"); traceback.print_exc(); time.sleep(3); return None

    # --- Hata Yakalama ---
    except Exception as menu_err:
        print(f"\n{R}{BRIGHT}CRITICAL MENU ERROR:{RESET}\n{menu_err}"); traceback.print_exc()
        print(f"{Y}Menu could not be displayed.{RESET}"); time.sleep(5); sys.exit(1)


# ==================================================================
# RUN_SCRIPT (Değişiklik Yok)
# ==================================================================
def run_script(script_name):
    # Bu fonksiyon önceki cevapta olduğu gibi İngilizce mesajlarla kalabilir.
    try:
        clear_screen()

        if not script_name:
            print(f"{R}Script name to run not specified.{RESET}")
            time.sleep(2); input(f"\n{Y}Press Enter to return to main menu...{RESET}"); return
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        if not os.path.exists(script_path):
            print(f"\n{R}{BRIGHT}ERROR: Script '{script_name}' not found in the current directory!{RESET}")
            print(f"{Y}Please ensure '{script_name}' is in the same folder as the main script.{RESET}")
            time.sleep(3); input(f"\n{Y}Press Enter to return to main menu...{RESET}"); return

        print(f"{C}{BRIGHT}--- Starting '{script_name}' ---{RESET}\n"); time.sleep(0.5)
        script_cancelled = False; requires_root = False

        # --- LEGAL WARNINGS & PRE-CHECKS ---
        if script_name == "netflix_checker.py": print(f"{R}{BRIGHT}WARNING:{Y} Netflix Checker is deprecated.{RESET}"); time.sleep(3); script_cancelled = True
        elif script_name in ["call_bomb.py", "sms_bomb.py"]: print(f"{Y}{BRIGHT}WARNING:{W} APIs might be outdated. Misuse is illegal.{RESET}"); time.sleep(2)
        elif script_name in ["DoS.py", "Basit_ddos.py", "DDoS.py", "brutforce.py", "keylogger.py"]: print(f"{R}{BRIGHT}!!! LEGAL WARNING !!!{RESET}\n{R}Unauthorized use is ILLEGAL! Only perform authorized tests.{RESET}"); time.sleep(3)
        elif script_name in ["wifi_jammer.py", "yedek_jammer.py", "sim-clone.py", "gps-spoofer.py"]:
            print(f"{R}{BRIGHT}!!! LEGAL WARNING & REQUIREMENTS !!!{RESET}\n{R}Use of this tool ({script_name}) is ILLEGAL!{RESET}")
            if script_name in ["wifi_jammer.py", "yedek_jammer.py"]: print(f"{Y}Requires special hardware and root privileges.{RESET}"); requires_root = True
            if script_name == "sim-clone.py": print(f"{Y}Requires 'qcsuper' and special hardware/permissions.{RESET}")
            if script_name == "gps-spoofer.py": print(f"{Y}Requires 'gpsd' and location permissions.{RESET}")
            print(f"{Y}For educational purposes only. Responsibility is yours.{RESET}")
            try:
                confirm = input(f"{Y}Do you want to continue? (y/N): {W}").strip().lower()
                if confirm != 'y': print(f"{G}Operation cancelled.{RESET}"); script_cancelled = True
                else: print(f"{R}POTENTIALLY ILLEGAL OPERATION STARTING...{RESET}"); time.sleep(1)
            except KeyboardInterrupt: print("\nCancelled."); script_cancelled = True; time.sleep(1)
        elif script_name in ["kamera_goruntuleme.py", "bilgitoplayıcı.py", "konum_takip.py", "wifipass_breaker.py"]: print(f"{Y}WARNING:{W} May require Termux API.{RESET}"); time.sleep(2)
        elif script_name == "pattern-braker.py": print(f"{Y}WARNING:{W} May require PyOpenCL/NumPy and GPU.{RESET}"); time.sleep(2)
        elif script_name == "wp-analizer.py": print(f"{Y}WARNING:{W} Requires Pandas/Pillow/Matplotlib and WhatsApp DB access.{RESET}"); time.sleep(2)
        elif script_name == "ag-tunelleme.py": print(f"{Y}WARNING:{W} Requires PyCryptodome/sshtunnel/paramiko.{RESET}"); time.sleep(2)

        # Execute Script
        if not script_cancelled:
            try:
                python_executable = sys.executable; command = []
                if requires_root and os.name != 'nt':
                    try: is_root = (os.geteuid() == 0)
                    except AttributeError: is_root = False
                    if not is_root: print(f"{Y}Root privileges required, using 'sudo'...{RESET}"); command.append("sudo")
                command.extend([python_executable, script_path])
                print(f"{G}Executing command: {' '.join(command)}{RESET}")
                process = subprocess.run(command, check=False, text=True, encoding='utf-8')
                if process.returncode != 0: print(f"{Y}Warning: script '{script_name}' finished with exit code {process.returncode}.{RESET}")
            except FileNotFoundError: print(f"{R}{BRIGHT}ERROR: '{python_executable}' or 'sudo' not found.{RESET}"); traceback.print_exc()
            except PermissionError: print(f"{R}{BRIGHT}ERROR: Permission denied to execute '{script_name}'.{RESET}"); traceback.print_exc()
            except Exception as e: print(f"\n{R}{BRIGHT}Error occurred while running script:{RESET}\n{e}"); traceback.print_exc()
    except Exception as outer_run_err: print(f"\n{R}{BRIGHT}CRITICAL run_script ERROR:{RESET}\n{outer_run_err}"); traceback.print_exc()

    print(f"\n{Y}Press Enter to return to main menu...{RESET}")
    try: input()
    except KeyboardInterrupt: print(f"\n\n{Y}+401 hack tool kapatıldı...{RESET}"); sys.exit()


# Ana Program Akışı
if __name__ == "__main__":
    try:
        try: import colorama
        except ImportError: pass

        while True:
            user_choice = show_menu_final() # Menüyü çağır

            if user_choice is None: continue # Menü/Giriş hatası

            if user_choice == exit_option: # Çıkış ('0')
                print(f"\n{Y}+401 hack tool kapatıldı...{RESET}")
                time.sleep(0.5)
                break # Döngüyü sonlandır
            elif user_choice in tool_map:
                script_file_to_run = tool_map[user_choice][1]
                run_script(script_file_to_run)
            else:
                print(f"\n{R}{BRIGHT}Invalid choice!{RESET}")
                time.sleep(1.5)

    except KeyboardInterrupt:
        print(f"\n\n{Y}+401 hack tool kapatıldı...{RESET}")
    except Exception as main_err:
        print(f"\n{R}{BRIGHT}CRITICAL ERROR:{RESET}\n{main_err}")
        traceback.print_exc()
        input(f"\n{Y}Press Enter to exit...{RESET}")
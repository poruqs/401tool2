# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re
import math
import base64
import codecs
import traceback # Hata detayları için eklendi

# --- Renk Tanımları (Colorama veya Manuel ANSI Kodları) ---
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
    pest1 = C
    yellow1 = Y
    red1 = R
    rosy1 = W
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


# --- Banner ---
banner_padding = " " * 12
banner_lines = [
    f"{C}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}",
    f"{C}{BRIGHT}██║  ██║██╔═████╗███║{RESET}",
    f"{C}{BRIGHT}███████║██║██╔██║╚██║{RESET}",
    f"{C}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}",
    f"{C}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}",
    f"{C}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}"
]

# --- Menü Öğeleri ---
menu_items = {
    '1': "Call Bomb", '2': "SMS Bomb", '3': "DoS Saldırısı", '4': "Yedek DDoS",
    '5': "Base64 Decode", '6': "Chromecast Hack", '7': "Web Saldırı", '8': "Instagram Araçları",
    '9': "Sosyal Medya Bulucu", '10': "Wi-Fi Jammer", '11': "DDoS Araçları", '12': "Ağ Tünelleme",
    '13': "Bilgi Toplayıcı", '14': "Bruteforce Aracı", '15': "GPS Spoofer", '16': "Kamera Görüntüleme",
    '17': "Log/Phishing/FakeAPK", '18': "Konum Takip", '19': "Özel Link Kısaltıcı", '20': "Pattern Kırıcı",
    '21': "SIM Klonlayıcı", '22': "IP/Site Dönüştürücü", '23': "WiFi Şifre Kırıcı", '24': "WhatsApp Analiz",
    '25': "Yedek Wi-Fi Jammer"
}

# --- Yardımcı Fonksiyonlar ---
def strip_colors(s):
    try:
        return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))
    except Exception as e:
        print(f"{R}strip_colors HATA: {e}{RESET}") # Hata olursa bildir
        return str(s) # Hata durumunda orijinal string'i döndür

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================================================================
# SHOW_MENU (Hata Yakalama Eklenmiş)
# ==================================================================
def show_menu():
    try:
        clear_screen()

        # --- Banner ve Alt Başlıkları Yazdır ---
        print()
        for line in banner_lines:
            print(f"{banner_padding}{line}")
        sub_padding = banner_padding + "   "
        print(f"{sub_padding}{G}{BRIGHT}by 401HackTeam{RESET}")
        print(f"{sub_padding}{Y}Version: 1.1{RESET}")
        print()

        # --- Menü Çerçevesi ve İçerik ---
        menu_width = 74
        col1_max_len = 26
        col_spacing = 4
        inner_padding = 1
        inner_width = menu_width - (inner_padding * 2) - 2

        print(f"{pest1}{'-' * menu_width}{coloursoff}") # Üst Çizgi

        num_items = len(menu_items)
        num_rows = math.ceil(num_items / 2)

        for i in range(num_rows):
            try: # Satır oluşturma işlemini dene
                idx1 = i + 1
                key1 = str(idx1)
                item1_text = ""
                item1_len_no_color = 0 # Renksiz uzunluğu sakla
                if key1 in menu_items:
                    item1_raw = f"{W}{key1.rjust(2)}.{C} {menu_items[key1]}{RESET}"
                    item1_len_no_color = len(strip_colors(item1_raw))
                    item1_text = item1_raw + ' ' * max(0, col1_max_len - item1_len_no_color)
                else:
                    item1_text = ' ' * col1_max_len
                    item1_len_no_color = col1_max_len

                idx2 = i + 1 + num_rows
                key2 = str(idx2)
                item2_text = ""
                item2_len_no_color = 0 # Renksiz uzunluğu sakla
                if key2 in menu_items:
                    item2_raw = f"{W}{key2.rjust(2)}.{C} {menu_items[key2]}{RESET}"
                    item2_len_no_color = len(strip_colors(item2_raw))
                    item2_text = item2_raw
                # else: İkinci sütun boşsa uzunluk 0'dır

                # Toplam satır içeriği (renkli)
                line_content_raw = f"{item1_text}{' ' * col_spacing}{item2_text}"
                # Toplam satır içeriği (renksiz) - Doğru hesaplama önemli
                line_len_no_color = item1_len_no_color + col_spacing + item2_len_no_color
                final_padding = ' ' * max(0, inner_width - line_len_no_color)

                # Satırı yazdır
                print(f"{pest1}|{coloursoff}{' ' * inner_padding}{line_content_raw}{final_padding}{' ' * inner_padding}{pest1}|{coloursoff}")

            except Exception as row_err:
                print(f"\n{R}HATA: Menü satırı oluşturulamadı (Satır {i}): {row_err}{RESET}")
                traceback.print_exc() # Detaylı hatayı yazdır
                # Hata durumunda menü gösterimini durdurabilir veya devam edebiliriz.
                # Şimdilik devam edelim ki diğer satırlar görünsün.

        # --- Ayırıcı ve Çıkış ---
        print(f"{pest1}{'-' * menu_width}{coloursoff}")

        try: # Çıkış satırını oluşturma ve yazdırma
            exit_text = f"{W} 0. {R}Çıkış{RESET}"
            exit_len_no_color = len(strip_colors(exit_text))
            exit_padding = ' ' * max(0, inner_width - exit_len_no_color)
            print(f"{pest1}|{coloursoff}{' ' * inner_padding}{exit_text}{exit_padding}{' ' * inner_padding}{pest1}|{coloursoff}")
        except Exception as exit_err:
            print(f"\n{R}HATA: Çıkış satırı oluşturulamadı: {exit_err}{RESET}")
            traceback.print_exc()

        print(f"{pest1}{'-' * menu_width}{coloursoff}") # Alt Çizgi

        # --- Prompt ---
        try:
            choice = input(f"\n{rosy1}Enter Your Option: {coloursoff}")
            return choice
        except KeyboardInterrupt:
            print("\n\nÇıkış yapılıyor...")
            sys.exit()
        except Exception as e:
            print(f"\n{R}GİRİŞ HATASI ({type(e).__name__}):{RESET} {e}")
            traceback.print_exc() # Detaylı hatayı yazdır
            time.sleep(3)
            return None # Hata durumunda None döndür

    except Exception as menu_err:
        print(f"\n{R}{BRIGHT}KRİTİK show_menu HATASI:{RESET}")
        print(f"{R}Hata: {menu_err}{RESET}")
        traceback.print_exc() # Detaylı hata izini yazdır
        print(f"{Y}Menü görüntülenemedi. Program sonlandırılacak.{RESET}")
        time.sleep(5)
        sys.exit(1) # Hata ile çık

# ==================================================================
# RUN_SCRIPT (Hata Yakalama ve Detaylandırma ile)
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
        # (Bu kısım öncekiyle aynı kalabilir)
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
                     try:
                         is_root = (os.geteuid() == 0)
                     except AttributeError:
                         is_root = False
                     if not is_root:
                         print(f"{Y}Root yetkisi gerekiyor, 'sudo' kullanılıyor...{RESET}")
                         command.append("sudo")
                command.extend([python_executable, script_path])

                print(f"{G}Komut çalıştırılıyor: {' '.join(command)}{RESET}")
                # Betiği çalıştır ve çıktısını anlık olarak göster
                process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                # Alt sürecin çıktısını anlık olarak oku ve yazdır
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip()) # Satır sonu karakterlerini temizle

                # Sürecin bitmesini bekle ve dönüş kodunu al
                return_code = process.poll()

                if return_code != 0:
                     print(f"{Y}Uyarı: '{script_name}' betiği {return_code} çıkış kodu ile bitti.{RESET}")

            except FileNotFoundError:
                 print(f"{R}{BRIGHT}HATA: '{python_executable}' veya 'sudo' komutu bulunamadı.{RESET}")
                 print(f"{Y}Python'un ve (gerekiyorsa) sudo'nun sistem PATH'inde olduğundan emin olun.{RESET}")
                 traceback.print_exc() # Hata detayını yazdır
            except PermissionError:
                 print(f"{R}{BRIGHT}HATA: '{script_name}' betiğini çalıştırma izni yok.{RESET}")
                 print(f"{Y}'chmod +x {script_name}' komutunu deneyebilirsiniz (gerekliyse).{RESET}")
                 traceback.print_exc() # Hata detayını yazdır
            except Exception as e:
                 print(f"\n{R}{BRIGHT}Betik çalıştırılırken hata oluştu ('{script_name}'):{RESET}\n{e}")
                 traceback.print_exc() # Hata detayını yazdır

    except Exception as outer_run_err:
        print(f"\n{R}{BRIGHT}KRİTİK run_script HATASI:{RESET}")
        print(f"{R}Hata: {outer_run_err}{RESET}")
        traceback.print_exc() # Hata detayını yazdır

    # Ana menüye dönmek için bekle (her durumda)
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
            user_choice = None
            try:
                user_choice = show_menu()

                if user_choice is None:
                    print(f"{Y}Menü hatası nedeniyle devam edilemiyor. Tekrar deneniyor...{RESET}")
                    time.sleep(2)
                    continue

                # --- Script Eşleştirme (Öncekiyle Aynı) ---
                script_to_run = None
                if user_choice == '1': script_to_run = "call_bomb.py"
                elif user_choice == '2': script_to_run = "sms_bomb.py"
                elif user_choice == '3': script_to_run = "DoS.py"
                elif user_choice == '4': script_to_run = "Basit_ddos.py"
                elif user_choice == '5': script_to_run = "base64decode.py"
                elif user_choice == '6': script_to_run = "choromecast_hack.py"
                elif user_choice == '7': script_to_run = "web_saldırı.py"
                elif user_choice == '8': script_to_run = "insta_saldırı.py"
                elif user_choice == '9': script_to_run = "sosyalmedya_bulma.py"
                elif user_choice == '10': script_to_run = "wifi_jammer.py"
                elif user_choice == '11': script_to_run = "DDoS.py"
                elif user_choice == '12': script_to_run = "ag-tunelleme.py"
                elif user_choice == '13': script_to_run = "bilgitoplayıcı.py"
                elif user_choice == '14': script_to_run = "brutforce.py"
                elif user_choice == '15': script_to_run = "gps-spoofer.py"
                elif user_choice == '16': script_to_run = "kamera_goruntuleme.py"
                elif user_choice == '17': script_to_run = "keylogger.py"
                elif user_choice == '18': script_to_run = "konum_takip.py"
                elif user_choice == '19': script_to_run = "ozellink_kısaltıcı.py"
                elif user_choice == '20': script_to_run = "pattern-braker.py"
                elif user_choice == '21': script_to_run = "sim-clone.py"
                elif user_choice == '22': script_to_run = "webip_tool.py"
                elif user_choice == '23': script_to_run = "wifipass_breaker.py"
                elif user_choice == '24': script_to_run = "wp-analizer.py"
                elif user_choice == '25': script_to_run = "yedek_jammer.py"
                elif user_choice == '0':
                    clear_screen()
                    print(f"\n{R}{BRIGHT}╔═══════════════════════════════════╗")
                    print(f"║    {Y}401HackTeam Tool Kapatılıyor...{R}    ║")
                    print(f"╚═══════════════════════════════════╝{RESET}\n")
                    time.sleep(1)
                    break
                else:
                    print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen listeden bir numara girin.{RESET}")
                    time.sleep(1.5)
                    continue

                if script_to_run:
                     run_script(script_to_run)

            except KeyboardInterrupt:
                print("\n\nÇıkış yapılıyor...")
                break
            except Exception as loop_err:
                print(f"\n{R}{BRIGHT}ANA DÖNGÜ HATASI ({type(loop_err).__name__}):{RESET} {loop_err}")
                traceback.print_exc() # Detaylı hata izini yazdır
                input(f"{Y}Devam etmek için Enter'a basın...{RESET}")

    except Exception as main_err:
        print(f"\n{R}{BRIGHT}KRİTİK PROGRAM HATASI ({type(main_err).__name__}):{RESET} {main_err}")
        traceback.print_exc() # Detaylı hata izini yazdır
        input(f"{Y}Çıkmak için Enter'a basın...{RESET}")

    finally:
        print(f"{B}Program sonlandı.{RESET}")
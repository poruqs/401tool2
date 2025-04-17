# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re
import math
import base64 # Base64 kodunu burada çözmeyeceğiz ama import kalsın
import codecs # Base64 kodunu burada çözmeyeceğiz ama import kalsın

# --- Renk Tanımları (Colorama veya Manuel ANSI Kodları) ---
# Colorama varsa onu kullanalım, yoksa manuel kodlar
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
    # er.jpg'deki renkleri eşleştirmek için ek renkler (varsayılanlar kullanılacak)
    pest1 = C  # Cyan
    yellow1 = Y # Yellow
    red1 = R    # Red
    rosy1 = W   # White (Prompt için)
    green1 = G  # Green
    coloursoff = RESET # Reset
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    BRIGHT = "\033[1m" # Kalın
    R = "\033[91m" # Kırmızı
    G = "\033[92m" # Yeşil
    Y = "\033[93m" # Sarı
    C = "\033[96m" # Cyan
    W = "\033[97m" # Beyaz
    RESET = "\033[0m" # Sıfırla
    # Manuel ANSI kodları
    pest1 = C
    yellow1 = Y
    red1 = R
    rosy1 = W
    green1 = G
    coloursoff = RESET


# --- Banner (Sizin istediğiniz, Tamamı Cyan, Sola Yaslı) ---
banner_padding = " " * 12
banner_lines = [
    f"{C}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}",
    f"{C}{BRIGHT}██║  ██║██╔═████╗███║{RESET}",
    f"{C}{BRIGHT}███████║██║██╔██║╚██║{RESET}",
    f"{C}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}",
    f"{C}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}",
    f"{C}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}"
]

# --- Menü Öğeleri (Sizin listeniz, Açıklamasız) ---
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
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================================================================
# SHOW_MENU (Base64'teki yapıya ve er.jpg stiline göre SIFIRDAN)
# ==================================================================
def show_menu():
    """er.jpg stiline göre birebir menü."""
    clear_screen()

    # --- Banner ve Alt Başlıkları Yazdır ---
    print()
    for line in banner_lines:
        print(f"{banner_padding}{line}")
    sub_padding = banner_padding + "   "
    print(f"{sub_padding}{G}{BRIGHT}by 401HackTeam{RESET}") # Yeşil
    print(f"{sub_padding}{Y}Version: 1.1{RESET}")      # Sarı
    print()

    # --- Menü Çerçevesi ve İçerik ---
    # er.jpg'deki genişliği ve hizalamayı manuel olarak ayarlayalım
    # Bu değerler görsel incelemeye dayanır, terminale göre değişebilir
    menu_width = 74          # Toplam çerçeve genişliği
    col1_max_len = 26        # İlk sütun için ayrılan maksimum karakter (Numara + İsim)
    col2_start_offset = 4    # İkinci sütunun başlamadan önceki boşluk sayısı
    inner_padding = 1        # Kenar | ile içerik arasındaki boşluk

    # İçeriğin yazılacağı alanın genişliği
    inner_width = menu_width - (inner_padding * 2) - 2 # | boşluk içerik boşluk |

    print(f"{pest1}{'-' * menu_width}{coloursoff}") # Üst Çizgi (Cyan)

    num_items = len(menu_items)
    num_rows = math.ceil(num_items / 2)

    for i in range(num_rows):
        idx1 = i * 2
        key1 = str(idx1 + 1)
        item1_text = ""
        if key1 in menu_items:
            # Format: Beyaz Numara. Cyan İsim
            item1_raw = f"{W}{key1.rjust(2)}.{C} {menu_items[key1]}{RESET}"
            item1_len = len(strip_colors(item1_raw))
            # İlk sütun için ayrılan alana sığdır ve sağını boşlukla doldur
            item1_text = item1_raw + ' ' * max(0, col1_max_len - item1_len)
        else:
            item1_text = ' ' * col1_max_len # Eğer öğe yoksa boşluk

        idx2 = i * 2 + 1
        key2 = str(idx2 + 1)
        item2_text = ""
        if key2 in menu_items:
            # Format: Beyaz Numara. Cyan İsim
            item2_raw = f"{W}{key2.rjust(2)}.{C} {menu_items[key2]}{RESET}"
            # İkinci sütunun kalan genişliğini hesapla (explicit padding yok)
            item2_text = item2_raw
        #else: # İkinci sütunda öğe yoksa boş bırakılabilir, satır sonu padding halleder

        # Satırı oluştur ve hizala
        line_content = f"{item1_text}{' ' * col_spacing}{item2_text}"
        line_len = len(strip_colors(line_content))
        final_padding = ' ' * max(0, inner_width - line_len)

        print(f"{pest1}|{coloursoff}{' ' * inner_padding}{line_content}{final_padding}{' ' * inner_padding}{pest1}|{coloursoff}")

    # --- Ayırıcı ve Çıkış ---
    print(f"{pest1}{'-' * menu_width}{coloursoff}")

    exit_text = f"{W} 0. {R}Çıkış{RESET}" # Beyaz Numara, Kırmızı Metin
    exit_len = len(strip_colors(exit_text))
    exit_padding = ' ' * max(0, inner_width - exit_len)
    print(f"{pest1}|{coloursoff}{' ' * inner_padding}{exit_text}{exit_padding}{' ' * inner_padding}{pest1}|{coloursoff}")

    print(f"{pest1}{'-' * menu_width}{coloursoff}") # Alt Çizgi

    # --- Prompt ---
    try:
        choice = input(f"\n{rosy1}Enter Your Option: {coloursoff}") # Beyaz Prompt
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()
    except Exception as e:
        print(f"\n{R}GİRİŞ HATASI:{RESET} {e}")
        return None
# ==================================================================
#               SHOW_MENU FONKSİYONU BİTİŞİ
# ==================================================================

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
    script_path = os.path.join(os.path.dirname(__file__), script_name) # Betiğin tam yolunu al
    if not os.path.exists(script_path):
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
    requires_root = False # Bazı scriptler root gerektirebilir

    # --- YASAL UYARILAR ve ÖN KONTROLLER (Kullanıcı bilgilendirme için önemli) ---
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
         except KeyboardInterrupt: print("\nİptal edildi."); script_cancelled = True
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
                 if not is_root: command.append("sudo")
            command.extend([python_executable, script_path])
            process = subprocess.run(command, check=False, text=True)
            # ... (Çıkış kodu kontrolü aynı kalabilir) ...

        except Exception as e:
             print(f"\n{R}{BRIGHT}Betik çalıştırılırken hata oluştu ('{script_name}'): {e}{RESET}")
             # import traceback; traceback.print_exc() # Detaylı hata için

    # Ana menüye dönmek için bekle
    print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
    try: input()
    except KeyboardInterrupt: print("\n\nÇıkış yapılıyor..."); sys.exit()


# Ana program akışı
if __name__ == "__main__":
    # Colorama kontrolü
    try: import colorama
    except ImportError: pass

    while True:
        user_choice = show_menu() # YENİ show_menu çağrılır

        if user_choice is None: print(f"{R}Menü hatası, çıkılıyor.{RESET}"); time.sleep(3); break

        # Script eşleştirmeleri (Numaralar güncel)
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
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}"); time.sleep(0.5); break
        else:
            print(f"\n{R}{BRIGHT}Geçersiz seçim!{RESET}"); time.sleep(1.5); continue

        if script_to_run:
             run_script(script_to_run)
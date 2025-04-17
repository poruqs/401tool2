# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re
import math

# --- UYARI ---
# Bu araç seti çeşitli ağ ve güvenlik araçları içerir.
# Bazı araçlar (Call/SMS Bomb, Jammer, DoS/DDoS, Bruteforce, SIM Clone, GPS Spoofer vb.)
# yasa dışı amaçlarla kullanılır ise sorumluluk kullanıcınındır.
# Bu araçların kullanımından doğacak tüm sorumluluk kullanıcıya aittir.
# API'lere dayalı araçlar (Call Bomb, SMS Bomb, Link Kısaltıcı) zamanla çalışmaz hale gelebilir.
# Bazı araçlar özel donanım, izinler (root), bağımlılıklar veya Termux API gerektirebilir.
# Lütfen araçları kullanmadan önce README dosyasını okuyun.
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


# Banner - Tamamı Cyan, Bitişik Stil, Sola Yaslı
banner_padding = " " * 12 # Sabit sol boşluk
banner_lines = [
    f"{C}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}",
    f"{C}{BRIGHT}██║  ██║██╔═████╗███║{RESET}",
    f"{C}{BRIGHT}███████║██║██╔██║╚██║{RESET}",
    f"{C}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}",
    f"{C}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}",
    f"{C}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}"
]

# Renk kodlarını temizleyen fonksiyon
def strip_colors(s):
    """ANSI renk/stil kodlarını string'den temizler."""
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

# ==============================================================
#               SHOW_MENU FONKSİYONU (Birebir Stil Hedefi)
# ==============================================================
def show_menu():
    """(er.jpg) stiline göre birebir menü."""
    clear_screen()

    # --- Banner ve Alt Başlıkları Yazdır (Sola Yaslı) ---
    print()
    for line in banner_lines:
        print(f"{banner_padding}{line}")

    sub_padding = banner_padding + "   " # Banner'dan biraz içeride
    print(f"{sub_padding}{G}{BRIGHT}by 401HackTeam{RESET}")
    print(f"{sub_padding}{Y}Version: 1.1{RESET}")
    print()

    # --- Menü Öğeleri (Açıklamasız Liste) ---
    menu_items = {
        '1': "Call Bomb", '2': "SMS Bomb", '3': "DoS Saldırısı", '4': "Yedek DDoS",
        '5': "Base64 Decode", '6': "Chromecast Hack", '7': "Web Saldırı", '8': "Instagram Araçları",
        '9': "Sosyal Medya Bulucu", '10': "Wi-Fi Jammer", '11': "DDoS Araçları", '12': "Ağ Tünelleme",
        '13': "Bilgi Toplayıcı", '14': "Bruteforce Aracı", '15': "GPS Spoofer", '16': "Kamera Görüntüleme",
        '17': "Log/Phishing/FakeAPK", '18': "Konum Takip", '19': "Özel Link Kısaltıcı", '20': "Pattern Kırıcı",
        '21': "SIM Klonlayıcı", '22': "IP/Site Dönüştürücü", '23': "WiFi Şifre Kırıcı", '24': "WhatsApp Analiz",
        '25': "Yedek Wi-Fi Jammer"
    }

    try:
        # --- Düzen Hesaplamaları ---
        menu_items_list = list(menu_items.items())
        num_items = len(menu_items_list)
        num_cols = 2
        num_rows = math.ceil(num_items / num_cols)

        # Sütun 1 için maksimum genişliği hesapla ("XX. İsim" formatında)
        max_col1_width = 0
        for i in range(num_rows):
            idx1 = i * 2
            if idx1 < num_items:
                key1 = str(idx1 + 1)
                value1 = menu_items.get(key1, "")
                item_str_plain = f"{key1.rjust(2)}. {value1}" # rjust ile 2 haneye tamamla
                max_col1_width = max(max_col1_width, len(item_str_plain))

        # Sütun 2 için maksimum genişliği hesapla
        max_col2_width = 0
        for i in range(num_rows):
            idx2 = i * 2 + 1
            if idx2 < num_items:
                key2 = str(idx2 + 1)
                value2 = menu_items.get(key2, "")
                item_str_plain = f"{key2.rjust(2)}. {value2}" # rjust ile 2 haneye tamamla
                max_col2_width = max(max_col2_width, len(item_str_plain))

        col_spacing = 4 # Sütunlar arası sabit boşluk (er.jpg'ye benzer)

        # İçeriğin sığacağı toplam genişlik
        inner_width = max_col1_width + col_spacing + max_col2_width
        # Çerçevenin toplam genişliği (| Boşluk İçerik Boşluk |)
        menu_width = inner_width + 4

        # --- Basit Kutu ve İçerik Çizimi (Hassas Padding) ---
        print(f"{C}{'-' * menu_width}{RESET}") # Üst kenar

        for i in range(num_rows):
            # --- Sol Sütun Öğesi ---
            idx1 = i * 2
            item1_text_padded = "" # İçerik + padding
            if idx1 < num_items:
                key1 = str(idx1 + 1)
                value1 = menu_items.get(key1, "")
                # Renkli formatla (Beyaz No. Cyan Metin)
                item1_colored = f"{W}{key1.rjust(2)}.{C} {value1}{RESET}"
                item1_plain_len = len(strip_colors(item1_colored))
                # Sağa boşluk ekleyerek max_col1_width'e tamamla
                padding = ' ' * max(0, max_col1_width - item1_plain_len)
                item1_text_padded = item1_colored + padding
            else:
                # Boşsa sütunu max_col1_width kadar boşlukla doldur
                item1_text_padded = ' ' * max_col1_width

            # --- Sağ Sütun Öğesi ---
            idx2 = i * 2 + 1
            item2_text_padded = "" # İçerik + padding
            if idx2 < num_items:
                 key2 = str(idx2 + 1)
                 value2 = menu_items.get(key2, "")
                 # Renkli formatla (Beyaz No. Cyan Metin)
                 item2_colored = f"{W}{key2.rjust(2)}.{C} {value2}{RESET}"
                 item2_plain_len = len(strip_colors(item2_colored))
                 # Sağa boşluk ekleyerek max_col2_width'e tamamla
                 padding = ' ' * max(0, max_col2_width - item2_plain_len)
                 item2_text_padded = item2_colored + padding
            else:
                 # Boşsa sütunu max_col2_width kadar boşlukla doldur
                 item2_text_padded = ' ' * max_col2_width

            # --- Satırı Yazdır ---
            # | boşluk Sütun1(Dolu) boşluk(Sabit) Sütun2(Dolu) boşluk |
            print(f"{C}| {RESET}{item1_text_padded}{' ' * col_spacing}{item2_text_padded} {C}|{RESET}")

        # --- Ayırıcı ve Çıkış ---
        print(f"{C}{'-' * menu_width}{RESET}")

        exit_text_colored = f"{W} 0. {R}Çıkış{RESET}" # Beyaz No, Kırmızı Metin
        exit_plain_len = len(strip_colors(exit_text_colored))
        # Sola yasla ve iç genişliğe tamamla (sağdaki boşlukları ekle)
        final_padding_exit = ' ' * max(0, inner_width - exit_plain_len)
        print(f"{C}| {RESET}{exit_text_colored}{final_padding_exit} {C}|{RESET}")

        print(f"{C}{'-' * menu_width}{RESET}") # Alt
        # --- Menü Kutusu Sonu ---

    except Exception as e:
        print(f"\n{R}MENÜ ÇİZİM HATASI:{RESET} {e}")
        import traceback
        traceback.print_exc()
        return None

    # --- Seçim İstemi ---
    try:
        choice = input(f"\n{W}Enter Your Option: {RESET}") # Örnekteki gibi istem
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()
    except Exception as e:
        print(f"\n{R}GİRİŞ HATASI:{RESET} {e}")
        return None
# ==============================================================
#               SHOW_MENU FONKSİYONU BİTİŞİ
# ==============================================================


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

    # --- YASAL UYARILAR ve ÖN KONTROLLER ---
    # (Uyarılar burada kalmalı, menüde olmasa bile kullanıcıyı bilgilendirir)
    if script_name == "netflix_checker.py":
         print(f"{R}{BRIGHT}UYARI:{Y} Netflix Checker kullanım dışıdır ve çalışmayacaktır.{RESET}")
         time.sleep(3); script_cancelled = True
    elif script_name in ["call_bomb.py", "sms_bomb.py"]:
         print(f"{Y}{BRIGHT}UYARI:{W} Bu aracın kullandığı API'ler güncel olmayabilir ve çalışmayabilir.{RESET}")
         print(f"{Y}Ayrıca, bu tür araçların kötüye kullanımı yasa dışıdır.{RESET}"); time.sleep(2)
    elif script_name in ["DoS.py", "Basit_ddos.py", "DDoS.py", "brutforce.py", "keylogger.py"]:
         print(f"{R}{BRIGHT}!!! YASAL UYARI !!!{RESET}")
         print(f"{R}Bu aracın ({script_name}) izinsiz sistemlere karşı kullanımı YASA DIŞIDIR!{RESET}")
         print(f"{Y}Sadece izinli test ortamlarında veya kendi sistemlerinizde kullanın."); time.sleep(3)
    elif script_name in ["wifi_jammer.py", "yedek_jammer.py", "sim-clone.py", "gps-spoofer.py"]:
         print(f"{R}{BRIGHT}!!! YASAL UYARI ve GEREKSİNİMLER !!!{RESET}")
         print(f"{R}Bu aracın ({script_name}) kullanımı Türkiye dahil birçok ülkede YASA DIŞIDIR.{RESET}")
         print(f"{R}Ciddi yasal sonuçlar doğurabilir.{RESET}")
         if script_name in ["wifi_jammer.py", "yedek_jammer.py"]:
            print(f"{Y}Ayrıca, özel Wi-Fi adaptörü ve root/sudo yetkisi gerektirir.{RESET}"); requires_root = True
         if script_name == "sim-clone.py": print(f"{Y}Ayrıca, 'qcsuper' aracı ve özel donanım/izinler gerektirir.{RESET}")
         if script_name == "gps-spoofer.py": print(f"{Y}Ayrıca, 'gpsd' servisi ve konum izinleri/ayarları gerektirir.{RESET}")
         print(f"{Y}Bu araçlar yalnızca eğitim amaçlıdır. Sorumluluk size aittir.{RESET}")
         try:
            confirm = input(f"{Y}Devam etmek istiyor musunuz? (e/H): {W}").strip().lower()
            if confirm != 'e': print(f"{G}İşlem iptal edildi.{RESET}"); script_cancelled = True
            else: print(f"{R}YASADIŞI OLABİLECEK İŞLEM BAŞLATILIYOR...{RESET}"); time.sleep(1)
         except KeyboardInterrupt: print("\nİptal edildi."); script_cancelled = True
    elif script_name in ["kamera_goruntuleme.py", "bilgitoplayıcı.py", "konum_takip.py", "wifipass_breaker.py"]:
        print(f"{Y}UYARI:{W} Bu araç Termux API veya komutları gerektirebilir.{RESET}"); time.sleep(2)
    elif script_name == "pattern-braker.py":
         print(f"{Y}UYARI:{W} Bu araç PyOpenCL/NumPy ve GPU gerektirebilir.{RESET}"); time.sleep(2)
    elif script_name == "wp-analizer.py":
         print(f"{Y}UYARI:{W} Bu araç Pandas/Pillow/Matplotlib ve WhatsApp DB erişimi gerektirir.{RESET}"); time.sleep(2)
    elif script_name == "ag-tunelleme.py":
         print(f"{Y}UYARI:{W} Bu araç PyCryptodome/sshtunnel/paramiko gerektirir.{RESET}"); time.sleep(2)

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
            process = subprocess.run(command, check=False, text=True) # stdout/stderr doğrudan akar
            # (Çıkış kodu kontrolü ve mesajları öncekiyle aynı)

        except Exception as e: # Genel hata yakalama
             print(f"\n{R}{BRIGHT}Betik çalıştırılırken hata oluştu ('{script_name}'): {e}{RESET}")
             # import traceback # Gerekirse detaylı hata için traceback'i etkinleştirin
             # traceback.print_exc()

    # Ana menüye dönmek için bekle
    print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
    try: input()
    except KeyboardInterrupt: print("\n\nÇıkış yapılıyor..."); sys.exit()


# Ana program akışı
if __name__ == "__main__":
    try:
        import colorama
    except ImportError:
        pass # Uyarı zaten verildi

    while True:
        user_choice = show_menu() # YENİ show_menu fonksiyonunu çağır

        if user_choice is None: # Menü çiziminde hata olursa
            print(f"{R}Menü hatası, çıkılıyor.{RESET}"); time.sleep(3); break

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
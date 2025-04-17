# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re
import math

# --- UYARI ---
# (Uyarı metni öncekiyle aynı)
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


# Banner - Tamamı Cyan, Bitişik Stil
banner_lines = [
    f"{C}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}",
    f"{C}{BRIGHT}██║  ██║██╔═████╗███║{RESET}",
    f"{C}{BRIGHT}███████║██║██╔██║╚██║{RESET}",
    f"{C}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}",
    f"{C}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}",
    f"{C}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}"
]

# Renk kodlarını temizleyen fonksiyon (hizalama için)
def strip_colors(s):
    """ANSI renk/stil kodlarını string'den temizler."""
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """İstenilen stile (er.jpg) BİREBİR benzeyen menü (Manuel Hizalama)."""
    clear_screen()

    # Menü Öğeleri (Açıklamasız)
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
        # --- Sabit Genişlik ve Hizalama Ayarları ---
        menu_width = 76 # Sabit toplam genişlik (ayarlanabilir)
        # İç genişlik: Kenarlar | ve 1 boşluk sağ/sol için 4 karakter çıkar
        inner_width = menu_width - 4
        col_spacing = 4 # Sütunlar arası boşluk
        # Her sütun için içerik genişliği (eşit bölünmüş)
        col_width = (inner_width - col_spacing) // 2

        # --- Banner ve Alt Başlıkları Ortala ---
        print()
        for line in banner_lines:
            line_plain_len = len(strip_colors(line))
            padding_len = max(0, (menu_width - line_plain_len) // 2)
            print(f"{' ' * padding_len}{line}")

        sub_head1 = f"{G}{BRIGHT}by 401HackTeam{RESET}"
        sub_head1_len = len(strip_colors(sub_head1))
        padding1 = max(0, (menu_width - sub_head1_len) // 2)
        print(f"{' ' * padding1}{sub_head1}")

        sub_head2 = f"{Y}Version: 1.1{RESET}"
        sub_head2_len = len(strip_colors(sub_head2))
        padding2 = max(0, (menu_width - sub_head2_len) // 2)
        print(f"{' ' * padding2}{sub_head2}")
        print()

        # --- Basit Kutu ve İçerik Çizimi (Manuel Padding) ---
        print(f"{C}{'-' * menu_width}{RESET}") # Üst kenar

        menu_items_list = list(menu_items.items())
        num_items = len(menu_items_list)
        num_rows = math.ceil(num_items / 2)

        for i in range(num_rows):
            # Sol Sütun Öğesi
            idx1 = i * 2
            item1_colored = ""
            item1_plain_len = 0
            if idx1 < num_items:
                key1 = str(idx1 + 1)
                value1 = menu_items.get(key1, "")
                item1_colored = f"{W}{key1.rjust(2)}.{C} {value1}{RESET}"
                item1_plain_len = len(f"{key1.rjust(2)}. {value1}")
            # Manuel padding ekle (col_width'e tamamla)
            item1_formatted = item1_colored + ' ' * max(0, col_width - item1_plain_len)

            # Sağ Sütun Öğesi
            idx2 = i * 2 + 1
            item2_colored = ""
            item2_plain_len = 0
            if idx2 < num_items:
                 key2 = str(idx2 + 1)
                 value2 = menu_items.get(key2, "")
                 item2_colored = f"{W}{key2.rjust(2)}.{C} {value2}{RESET}"
                 item2_plain_len = len(f"{key2.rjust(2)}. {value2}")
            # Manuel padding ekle (col_width'e tamamla)
            # Not: Sağdaki son sütunun padding'i aslında satır sonunda otomatik ayarlanacak,
            # ama tutarlılık için burada da ekleyebiliriz veya boş bırakabiliriz.
            # Şimdilik ekleyelim, ancak sağ kenara taşmamasına dikkat edelim.
            item2_formatted = item2_colored + ' ' * max(0, col_width - item2_plain_len)


            # Satırı birleştir ve yazdır (| Boşluk Sütun1 Boşluk Sütun2 Boşluk |)
            # İki sütunun toplam uzunluğu ve aradaki boşluk
            # Not: itemX_formatted zaten col_width kadar boşluk içeriyor olabilir.
            # Bu yüzden strip_colors ile gerçek içeriği alıp padding eklemek daha doğru.
            item1_clean_colored = item1_colored # Padding eklenmemiş hali
            item1_clean_plain_len = item1_plain_len
            padding1 = ' ' * max(0, col_width - item1_clean_plain_len)

            item2_clean_colored = item2_colored # Padding eklenmemiş hali
            item2_clean_plain_len = item2_plain_len
            padding2 = ' ' * max(0, col_width - item2_clean_plain_len) # Bu sağdaki boşluk

            # Satırı oluştur: Öğe1 + Padding1 + Aralik + Öğe2 + Padding2
            line_content = f"{item1_clean_colored}{padding1}{' ' * col_spacing}{item2_clean_colored}{padding2}"
            line_plain_len = len(strip_colors(line_content))

            # Çok nadir de olsa hesaplama hatası olursa diye son kontrol
            final_padding = ' ' * max(0, inner_width - line_plain_len)


            print(f"{C}| {RESET}{item1_clean_colored}{padding1}{' ' * col_spacing}{item2_clean_colored}{final_padding} {C}|{RESET}")


        # Ayırıcı ve Çıkış
        print(f"{C}{'-' * menu_width}{RESET}")

        exit_text_colored = f"{W} 0. {R}Çıkış{RESET}" # Beyaz No, Kırmızı Metin
        exit_plain_len = len(strip_colors(exit_text_colored))
        # Çıkışı sola yasla ve sona kadar boşluk ekle
        final_padding_exit = ' ' * max(0, inner_width - exit_plain_len)
        print(f"{C}| {RESET}{exit_text_colored}{final_padding_exit} {C}|{RESET}")

        print(f"{C}{'-' * menu_width}{RESET}") # Alt
        # --- Menü Kutusu Sonu ---

    except Exception as e:
        print(f"\n{R}MENÜ ÇİZİM HATASI:{RESET} {e}")
        import traceback
        traceback.print_exc()
        return None

    # Seçim istemi
    try:
        choice = input(f"\n{W}Enter Your Option: {RESET}") # Örnekteki gibi istem
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit()
    except Exception as e:
        print(f"\n{R}GİRİŞ HATASI:{RESET} {e}")
        return None

def run_script(script_name):
    """Belirtilen Python betiğini çalıştırır (Menüyü temizleyerek)."""
    # (Bu fonksiyonun içeriği önceki cevaplardakiyle aynı kalabilir)
    # ... (önceki cevaplardaki run_script içeriği) ...
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
    if script_name == "netflix_checker.py": # Gerçi bu kaldırıldı ama yine de dursun
         print(f"{R}{BRIGHT}UYARI:{Y} Netflix Checker kullanım dışıdır ve çalışmayacaktır.{RESET}")
         time.sleep(3)
         script_cancelled = True
    elif script_name in ["call_bomb.py", "sms_bomb.py"]:
         print(f"{Y}{BRIGHT}UYARI:{W} Bu aracın kullandığı API'ler güncel olmayabilir ve çalışmayabilir.{RESET}")
         print(f"{Y}Ayrıca, bu tür araçların kötüye kullanımı yasa dışıdır.{RESET}")
         time.sleep(2)
    elif script_name in ["DoS.py", "Basit_ddos.py", "DDoS.py", "brutforce.py", "keylogger.py"]:
         print(f"{R}{BRIGHT}!!! YASAL UYARI !!!{RESET}")
         print(f"{R}Bu aracın ({script_name}) izinsiz sistemlere karşı kullanımı YASA DIŞIDIR!{RESET}")
         print(f"{Y}Sadece izinli test ortamlarında veya kendi sistemlerinizde kullanın.{RESET}")
         print(f"{Y}Tüm sorumluluk size aittir.{RESET}")
         time.sleep(3)
    elif script_name in ["wifi_jammer.py", "yedek_jammer.py", "sim-clone.py", "gps-spoofer.py"]:
         print(f"{R}{BRIGHT}!!! YASAL UYARI ve GEREKSİNİMLER !!!{RESET}")
         print(f"{R}Bu aracın ({script_name}) kullanımı Türkiye dahil birçok ülkede YASA DIŞIDIR.{RESET}")
         print(f"{R}Ciddi yasal sonuçlar doğurabilir.{RESET}")
         if script_name in ["wifi_jammer.py", "yedek_jammer.py"]:
            print(f"{Y}Ayrıca, özel Wi-Fi adaptörü (Monitor Modu/Paket Enjeksiyonu destekli) ve root/sudo yetkisi gerektirir.{RESET}")
            requires_root = True
         if script_name == "sim-clone.py":
             print(f"{Y}Ayrıca, 'qcsuper' aracının kurulu olması ve özel donanım/izinler gerektirir.{RESET}")
         if script_name == "gps-spoofer.py":
             print(f"{Y}Ayrıca, 'gpsd' servisinin çalışması ve konum izinleri/ayarları gerektirir.{RESET}")
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
    elif script_name in ["kamera_goruntuleme.py", "bilgitoplayıcı.py", "konum_takip.py", "wifipass_breaker.py"]:
        print(f"{Y}UYARI:{W} Bu araç ('{script_name}') Termux API veya özel Termux komutları gerektirebilir.{RESET}")
        print(f"{Y}Termux ortamında değilseniz veya Termux API kurulu/izinli değilse çalışmayabilir.{RESET}")
        time.sleep(2)
    elif script_name == "pattern-braker.py":
         print(f"{Y}UYARI:{W} Bu araç ('{script_name}') PyOpenCL ve NumPy kütüphanelerini gerektirir.{RESET}")
         print(f"{Y}Ayrıca OpenCL destekli bir GPU ve sürücülerinin kurulu olması gerekebilir.{RESET}")
         time.sleep(2)
    elif script_name == "wp-analizer.py":
         print(f"{Y}UYARI:{W} Bu araç ('{script_name}') Pandas, Pillow, Matplotlib kütüphanelerini gerektirir.{RESET}")
         print(f"{Y}Ayrıca WhatsApp mesaj veritabanına ('msgstore.db') erişim gerektirir.{RESET}")
         time.sleep(2)
    elif script_name == "ag-tunelleme.py":
         print(f"{Y}UYARI:{W} Bu araç ('{script_name}') PyCryptodome, sshtunnel, paramiko kütüphanelerini gerektirir.{RESET}")
         print(f"{Y}Kurulumları 'pip install pycryptodome sshtunnel paramiko' ile yapabilirsiniz.{RESET}")
         time.sleep(2)

    # Betiği çalıştırma (eğer iptal edilmediyse)
    if not script_cancelled:
        try:
            python_executable = sys.executable
            command = []
            # Root gerektiren scriptler için sudo ekle (Linux/macOS)
            if requires_root and os.name != 'nt':
                 # Check if already root
                 try:
                     is_root = (os.geteuid() == 0)
                 except AttributeError: # Windows'ta geteuid yok
                     is_root = False

                 if not is_root:
                     print(f"{Y}Bu betik root yetkisi gerektiriyor. 'sudo' ile çalıştırılacak...{RESET}")
                     command.append("sudo")
                 else:
                     print(f"{C}Zaten root olarak çalıştırılıyor.{RESET}")

            command.extend([python_executable, script_path]) # script_path tam yolu içeriyor

            # subprocess.run kullanarak betiği çalıştır
            process = subprocess.run(command, check=False, text=True, capture_output=False) # capture_output=False stdout/stderr doğrudan görünsün

            if process.returncode == 0:
                 print(f"\n{G}{BRIGHT}--- '{script_name}' işlemi normal şekilde tamamlandı (Çıkış Kodu: 0) ---{RESET}")
            else:
                 print(f"\n{Y}{BRIGHT}--- '{script_name}' işlemi bir sonuçla tamamlandı (Çıkış Kodu: {process.returncode}) ---{RESET}")
                 print(f"{Y}Betik içinde bir hata oluşmuş veya işlem kullanıcı tarafından sonlandırılmış olabilir.{RESET}")
                 if process.returncode == 1 and requires_root and os.name != 'nt':
                     try:
                         is_root = (os.geteuid() == 0)
                     except AttributeError:
                         is_root = False
                     if not is_root:
                        print(f"{R}İpucu: Root yetkisi alamamış olabilirsiniz. Ana betiği 'sudo python3 {os.path.basename(__file__)}' ile çalıştırmayı deneyin.{RESET}")


        except FileNotFoundError:
            print(f"\n{R}{BRIGHT}HATA: Python yorumlayıcısı '{python_executable}' veya 'sudo' (gerekliyse) bulunamadı!{RESET}")
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
        pass # Uyarı zaten verildi

    while True:
        user_choice = show_menu()

        if user_choice is None:
            print(f"{R}Menü gösterilirken veya giriş alınırken bir hata oluştu, program sonlandırılıyor.{RESET}")
            time.sleep(3)
            break

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
        # ---
        elif user_choice == '0':
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}")
            time.sleep(0.5)
            break
        else:
            print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen menüdeki numaralardan birini girin.{RESET}")
            time.sleep(1.5)
            continue # Döngünün başına dön

        # Eğer geçerli bir script seçildiyse çalıştır
        if script_to_run:
             run_script(script_to_run)
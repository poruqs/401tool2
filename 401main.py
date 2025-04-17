# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re
import math # Sütun hesaplaması için eklendi

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
    """Kullanıcının yapısı, yeni renkler ve YAN YANA (2 SÜTUNLU) düzen ile güncellenmiş menü (IP Toolkit kaldırıldı)."""
    clear_screen()
    print(banner)

    menu_width = 76 # Yan yana sığdırmak için genişlik
    title = "401 HACKING TOOL v2.1 (IP Tool Kaldırıldı)" # Başlığı güncelledim
    inner_width = menu_width - 4 # İç genişlik

    # Menü Öğeleri (Güncellenmiş Liste - IP Toolkit olmadan)
    menu_items = {
        # IP Toolkit (eski 6) kaldırıldı, numaralar kaydırıldı
        '1': f"Call Bomb {R}(API Sorunlu){W}",
        '2': f"SMS Bomb",
        '3': f"DoS Saldırısı",
        '4': f"Yedek DDoS",
        '5': f"Base64 Decode",
        '6': f"Chromecast Hack {R}(API Sorunlu){W}", # Eski 7
        '7': f"Web Saldırı Araçları {C}(Yeni){W}", # Eski 8
        '8': f"Instagram Araçları {C}(Yeni){W}", # Eski 9
        '9': f"Sosyal Medya Bulucu {C}(Yeni){W}", # Eski 10
        '10': f"Wi-Fi Jammer {C}(Yeni){W}", # Eski 11
        '11': f"DDoS Tool", # Eski 12
        '12': f"Ağ Tünelleme (SSH/DNS) {C}(Yeni){W}", # Eski 13
        '13': f"Bilgi Toplayıcı {C}(Yeni){W}", # Eski 14
        '14': f"Bruteforce Aracı {C}(Yeni){W}", # Eski 15
        '15': f"GPS Spoofer {C}(Yeni){W}", # Eski 16
        '16': f"Kamera Görüntüleme {R}(BAKIMDA){W}", # Eski 17
        '17': f"Phishing Tool {C}(Yeni){W}", # Eski 18
        '18': f"Konum Takip {C}(Yeni){W}", # Eski 19
        '19': f"Özel Link Kısaltıcı {C}(Yeni){W}", # Eski 20
        '20': f"Pattern Kırıcı {R}(BAKIMDA){W}", # Eski 21
        '21': f"SIM Klonlayıcı {C}(Yeni){W}", # Eski 22
        '22': f"IP/Site Dönüştürücü {C}(Yeni){W}", # Eski 23
        '23': f"WiFi Şifre Kırıcı {C}(Yeni){W}", # Eski 24
        '24': f"WhatsApp Analiz Aracı {C}(Yeni){W}", # Eski 25
        '25': f"Yedek Wi-Fi Jammer {C}(Yeni){W}" # Eski 26
    }

    try:
        # --- Menü Kutusu Başlangıcı (EFLATUN - Magenta) ---
        print(f"{M}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
        # Başlık: Parlak Camgöbeği
        print(f"{M}{BRIGHT}║ {C}{BRIGHT}{title.center(inner_width)} {M}{BRIGHT}║{RESET}")
        print(f"{M}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")

        # --- Sütunlu Menü Öğeleri ---
        menu_items_list = list(menu_items.items())
        num_items = len(menu_items_list)
        num_cols = 2  # İki sütunlu yapı
        # Her sütundaki öğe sayısı (yukarı yuvarla)
        items_per_col = math.ceil(num_items / num_cols)

        # Sütunlar arası boşluk
        col_spacing = 4

        # Her sütunun içeriği için kullanılabilir genişlik
        available_width_for_cols = inner_width - (num_cols - 1) * col_spacing
        col_content_width = available_width_for_cols // num_cols

        # Sütunları satır satır yazdır
        for i in range(items_per_col):
            row_parts_colored = []
            row_parts_plain_len = 0

            # Mevcut satır için her sütunu oluştur
            for col_index in range(num_cols):
                item_index = i + col_index * items_per_col
                if item_index < num_items:
                    key, value = menu_items_list[item_index]
                    num_part_plain = f"[{key}]"
                    # Numaralar: Parlak Camgöbeği, Metin: Beyaz (veya özel renk)
                    num_part_colored = f"{C}{BRIGHT}{key.rjust(2)}{W}" # Numaraları sağa yasla (2 haneli varsayımı)
                    text_part_colored = f" {value}" # Metin ve durum etiketleri
                    text_part_plain = f" {strip_colors(text_part_colored)}"

                    # Renkli ve renksiz öğe stringleri
                    item_str_colored = f"{num_part_colored}{text_part_colored}"
                    item_str_plain = f"[{key.rjust(2)}]{text_part_plain}" # Uzunluk hesaplama için renksiz
                    visible_item_length = len(item_str_plain)

                    # Sütun genişliğine göre padding ekle
                    padding_needed = col_content_width - visible_item_length
                    final_padding = ' ' * max(0, padding_needed)

                    row_parts_colored.append(f"{item_str_colored}{final_padding}")
                    row_parts_plain_len += col_content_width # Sütun genişliğini ekle
                else:
                    # Bu sütunda/satırda öğe yoksa boşluk ekle
                    row_parts_colored.append(' ' * col_content_width)
                    row_parts_plain_len += col_content_width # Sütun genişliğini ekle

            # Sütunları aralarına boşluk koyarak birleştir
            line_content_colored = f"{' ' * col_spacing}".join(row_parts_colored)
            # Toplam uzunluk için sütunlar arası boşluğu ekle
            row_parts_plain_len += (num_cols - 1) * col_spacing

            # Satırın sonuna, kutu sınırına kadar padding ekle
            final_line_padding_needed = inner_width - row_parts_plain_len
            final_line_padding = ' ' * max(0, final_line_padding_needed)

            # Satırı kutu içinde yazdır
            print(f"{M}{BRIGHT}║ {line_content_colored}{final_line_padding} {M}{BRIGHT}║{RESET}")

        # --- Menü Öğeleri Sonu ---

        # Boş Satır ve Ayırıcı (Kutu: Eflatun)
        print(f"{M}{BRIGHT}║{' ' * (inner_width + 2)}║{RESET}")
        print(f"{M}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")

        # Çıkış Seçeneği (Numara: Kırmızı) - Sola Yaslı
        num_part_exit = "[0]"
        text_part_exit = "Çıkış"
        item_str_exit_colored = f"{R}{BRIGHT}{num_part_exit}{W} {text_part_exit}"
        visible_exit_length = len(strip_colors(item_str_exit_colored))
        padding_needed_exit = inner_width - visible_exit_length
        final_padding_exit = ' ' * max(0, padding_needed_exit)
        # Menü satırı (Kutu: Eflatun)
        print(f"{M}{BRIGHT}║ {item_str_exit_colored}{final_padding_exit} {M}{BRIGHT}║{RESET}")

        # Alt Kenarlık (Kutu: Eflatun)
        print(f"{M}{BRIGHT}{'╚' + '═' * (menu_width - 2) + '╝'}{RESET}")
        # --- Menü Kutusu Sonu ---

    except Exception as e:
        print(f"\n{R}MENÜ ÇİZİM HATASI:{RESET} {e}")
        import traceback
        traceback.print_exc() # Detaylı hata için
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
                 if os.geteuid() != 0:
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
                 if process.returncode == 1 and requires_root and os.name != 'nt' and os.geteuid() != 0:
                     print(f"{R}İpucu: Root yetkisi alamamış olabilirsiniz. Ana betiği 'sudo python3 401main.py' ile çalıştırmayı deneyin.{RESET}")

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

        # Script eşleştirmeleri (Numaralar güncellendi)
        script_to_run = None
        if user_choice == '1': script_to_run = "call_bomb.py"
        elif user_choice == '2': script_to_run = "sms_bomb.py"
        elif user_choice == '3': script_to_run = "DoS.py"
        elif user_choice == '4': script_to_run = "Basit_ddos.py"
        elif user_choice == '5': script_to_run = "base64decode.py" # Eski 6
        # 6 (IP Toolkit) kaldırıldı
        elif user_choice == '6': script_to_run = "choromecast_hack.py" # Eski 7
        elif user_choice == '7': script_to_run = "web_saldırı.py" # Eski 8
        elif user_choice == '8': script_to_run = "insta_saldırı.py" # Eski 9
        elif user_choice == '9': script_to_run = "sosyalmedya_bulma.py" # Eski 10
        elif user_choice == '10': script_to_run = "wifi_jammer.py" # Eski 11
        elif user_choice == '11': script_to_run = "DDoS.py" # Eski 12
        elif user_choice == '12': script_to_run = "ag-tunelleme.py" # Eski 13
        elif user_choice == '13': script_to_run = "bilgitoplayıcı.py" # Eski 14
        elif user_choice == '14': script_to_run = "brutforce.py" # Eski 15
        elif user_choice == '15': script_to_run = "gps-spoofer.py" # Eski 16
        elif user_choice == '16': script_to_run = "kamera_goruntuleme.py" # Eski 17
        elif user_choice == '17': script_to_run = "keylogger.py" # Eski 18
        elif user_choice == '18': script_to_run = "konum_takip.py" # Eski 19
        elif user_choice == '19': script_to_run = "ozellink_kısaltıcı.py" # Eski 20
        elif user_choice == '20': script_to_run = "pattern-braker.py" # Eski 21
        elif user_choice == '21': script_to_run = "sim-clone.py" # Eski 22
        elif user_choice == '22': script_to_run = "webip_tool.py" # Eski 23
        elif user_choice == '23': script_to_run = "wifipass_breaker.py" # Eski 24
        elif user_choice == '24': script_to_run = "wp-analizer.py" # Eski 25
        elif user_choice == '25': script_to_run = "yedek_jammer.py" # Eski 26
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
# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import re

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
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE
    RESET = Style.RESET_ALL
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli.")
    print("Lütfen 'pip install colorama' komutu ile yükleyin.")
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""
    # Fallback class'ları tanımla ki kod hata vermesin
    class Style: BRIGHT = ""; DIM = ""; RESET_ALL = ""
    class Fore: RED = ""; GREEN = ""; YELLOW = ""; BLUE = ""; MAGENTA = ""; CYAN = ""; WHITE = ""
    class Back: pass


# Banner - Orijinal "401", Parlak Yeşil
banner_padding = " " * 12
banner = f"""
{banner_padding}{G}{BRIGHT}██╗  ██╗ ██████╗  ██╗{RESET}
{banner_padding}{G}{BRIGHT}██║  ██║██╔═████╗███║{RESET}
{banner_padding}{G}{BRIGHT}███████║██║██╔██║╚██║{RESET}
{banner_padding}{G}{BRIGHT}╚════██║████╔╝██║ ██║{RESET}
{banner_padding}{G}{BRIGHT}     ██║╚██████╔╝ ██║{RESET}
{banner_padding}{G}{BRIGHT}     ╚═╝ ╚═════╝  ╚═╝{RESET}
"""

# Renk kodlarını temizleyen fonksiyon
def strip_colors(s):
    """ANSI renk/stil kodlarını string'den temizler."""
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', str(s))

def clear_screen():
    """Ekranı temizler."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Genişletilmiş menü."""
    clear_screen()
    print(banner)

    menu_width = 55 # <<< Menü kutusunun genişliği artırıldı
    title = "401 MULTI TOOL"
    inner_width = menu_width - 4 # İç genişlik

    try:
        # --- Menü Kutusu Başlangıcı (Mavi) ---
        print(f"{B}{BRIGHT}{'╔' + '═' * (menu_width - 2) + '╗'}{RESET}")
        print(f"{B}{BRIGHT}║ {R}{BRIGHT}{title.center(inner_width)} {B}{BRIGHT}║{RESET}") # Kırmızı Başlık
        print(f"{B}{BRIGHT}{'╠' + '═' * (menu_width - 2) + '╣'}{RESET}")
        print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}") # Boşluk

        # Genişletilmiş Menü Öğeleri
        menu_items = {
            '1': f"Call Bomb",
            '2': f"SMS Bomb",
            '3': f"DoS Saldırısı {Y}(YENİLENDİ!){W}",
            '4': f"Netflix Checker {R}(BAKIMDA){W}",
            '5': f"Base64 Decode {Y}(YENİ!){W}",
            '6': f"IP Toolkit {C}(YENİ!){W}",
            '7': f"Chromecast Hack {M}(YENİ!){W}",
            '8': f"Web Saldırı Araçları {R}(Tamamlanmadı){W}",
            '9': f"Instagram Saldırı Araçları {R}(Tamamlanmadı){W}",
            '10': f"Sosyal Medya Bulucu Araçlar {R}(Tamamlanmadı){W}",
            '11': f"Wi-Fi Jammer/Deauth Araçları {R}{BRIGHT}(YASADIŞI!,Tamamlanmadı){W}",
            '12': f"DDoS Saldırı Araçları {R}(YENİ!,BAKIMDA!){W}"
        }

        for key, value in menu_items.items():
            # İki haneli sayılar için hizalama ayarı
            num_part_plain = f"[{key}]"
            num_part_colored = f"{Y}{BRIGHT}{num_part_plain}{W}"

            text_part_colored = value
            text_part_plain = strip_colors(text_part_colored)
            # Görünür uzunluğu hesapla (renk kodları hariç)
            visible_item_length = len(num_part_plain) + 1 + len(text_part_plain)
            padding_needed = inner_width - visible_item_length
            item_str_colored = f"{num_part_colored} {text_part_colored}"
            final_padding = ' ' * max(0, padding_needed)

            print(f"{B}{BRIGHT}║ {item_str_colored}{final_padding} {B}{BRIGHT}║{RESET}")

        # Boş Satır ve Ayırıcı
        print(f"{B}{BRIGHT}║{' ' * (menu_width - 2)}║{RESET}")
        print(f"{B}{BRIGHT}╟{'─' * (menu_width - 2)}╢{RESET}")

        # Çıkış Seçeneği
        num_part_exit = "[0]"
        text_part_exit = "Çıkış"
        visible_exit_length = len(num_part_exit) + 1 + len(text_part_exit)
        padding_needed_exit = inner_width - visible_exit_length
        item_str_exit_colored = f"{R}{BRIGHT}{num_part_exit}{W} {text_part_exit}"
        final_padding_exit = ' ' * max(0, padding_needed_exit)
        print(f"{B}{BRIGHT}║ {item_str_exit_colored}{final_padding_exit} {B}{BRIGHT}║{RESET}")

        # Alt Kenarlık
        print(f"{B}{BRIGHT}{'╚' + '═' * (menu_width - 2) + '╝'}{RESET}")
        # --- Menü Kutusu Sonu ---

    except Exception as e:
        print(f"\n{R}MENÜ ÇİZİM HATASI:{RESET} {e}")
        # Hata durumunda None döndürerek ana döngünün çıkmasını sağla
        return None

    # Seçim istemi
    try:
        choice = input(f"\n{G}{BRIGHT}>> Seçiminizi girin:{W} ")
        return choice
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit() # Ctrl+C ile doğrudan çık
    except Exception as e:
        print(f"\n{R}GİRİŞ HATASI:{RESET} {e}")
        # Hata durumunda None döndür
        return None

def run_script(script_name):
    """Belirtilen Python betiğini çalıştırır."""
    if not script_name:
        print(f"{R}Çalıştırılacak betik adı belirtilmedi.{RESET}")
        time.sleep(2)
        return

    # Özel Uyarılar
    if script_name == "netflix_checker.py":
         print(f"\n{R}{BRIGHT}UYARI:{Y} Netflix Checker şu anda bakımdadır ve düzgün çalışmayabilir.{RESET}")
         time.sleep(2)
    elif script_name == "wifi_jammer.py":
         print(f"\n{R}{BRIGHT}!!! YASAL UYARI !!!{RESET}")
         print(f"{R}Wi-Fi Jammer/Deauther araçlarının kullanımı Türkiye dahil birçok ülkede YASA DIŞIDIR.{RESET}")
         print(f"{R}Bu seçeneği çalıştırmak ciddi yasal sonuçlar doğurabilir.{RESET}")
         print(f"{Y}Bu araçlar yalnızca eğitim ve yasal test amaçlıdır. Sorumluluk size aittir.{RESET}")
         try:
            confirm = input(f"{Y}Devam etmek istiyor musunuz? (e/H): {W}").strip().lower()
            if confirm != 'e':
                print(f"{G}İşlem iptal edildi.{RESET}")
                time.sleep(1)
                return # Fonksiyondan çık, betiği çalıştırma
         except KeyboardInterrupt:
             print("\nİptal edildi.")
             return

    try:
        print(f"\n{C}{BRIGHT}--- '{script_name}' başlatılıyor ---{RESET}\n")
        time.sleep(0.5) # Kullanıcıya mesajı görmesi için kısa bir süre ver
        python_executable = sys.executable # Mevcut Python yorumlayıcısını kullan
        # Betiği çalıştır
        # capture_output=False: Betiğin çıktıları doğrudan terminalde görünür
        # check=True: Betik hata ile biterse (sıfır olmayan çıkış kodu) hata verir
        process = subprocess.run([python_executable, script_name], check=False, text=True, capture_output=False)

        # Framework betikleri genellikle kendi içlerinde döngüye girer veya kullanıcıdan input bekler.
        # Bu nedenle, işlem bittikten sonra otomatik 'başarıyla tamamlandı' mesajı her zaman uygun olmayabilir.
        # Sadece çıkış koduna göre basit bir mesaj verelim.
        if process.returncode == 0:
             print(f"\n{G}{BRIGHT}--- '{script_name}' işlemi tamamlandı (Çıkış Kodu: 0) ---{RESET}")
        else:
             print(f"\n{Y}{BRIGHT}--- '{script_name}' işlemi bir sonuçla tamamlandı (Çıkış Kodu: {process.returncode}) ---{RESET}")
             print(f"{Y}Betik içinde bir hata oluşmuş veya işlem kullanıcı tarafından sonlandırılmış olabilir.{RESET}")

    except FileNotFoundError:
        print(f"\n{R}{BRIGHT}HATA: '{script_name}' dosyası bulunamadı!{RESET}")
        print(f"{Y}Lütfen '{script_name}' dosyasının '{os.path.basename(__file__)}' ile aynı dizinde olduğundan emin olun.{RESET}")
    except subprocess.CalledProcessError as e: # check=True kullanıldığında bu hata yakalanır
        print(f"\n{R}{BRIGHT}HATA: '{script_name}' çalıştırılırken bir sorun oluştu.{RESET}")
        print(f"{Y}Betik muhtemelen bir hata verdi (Çıkış Kodu: {e.returncode}). Betiğin kendi hata mesajlarına bakın.{RESET}")
    except KeyboardInterrupt:
         print(f"\n{Y}İşlem kullanıcı tarafından kesildi.{RESET}")
         # Ana döngüye dönmeden önce biraz bekleme
         time.sleep(1)
         # Gerekirse burada ek temizlik yapılabilir
    except Exception as e:
        print(f"\n{R}{BRIGHT}Beklenmedik bir hata oluştu: {e}{RESET}")

    # Her betik çağrısından sonra ana menüye dönmeden önce bekle
    print(f"\n{Y}Ana menüye dönmek için Enter tuşuna basın...{RESET}")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nÇıkış yapılıyor...")
        sys.exit() # Doğrudan çık

# Ana program akışı
if __name__ == "__main__":
    while True:
        user_choice = show_menu()

        if user_choice is None:
            # show_menu içinde bir hata oluştu veya giriş alınamadı
            print(f"{R}Menü gösterilirken veya giriş alınırken bir hata oluştu, program sonlandırılıyor.{RESET}")
            time.sleep(3)
            break

        script_to_run = None
        if user_choice == '1':
            script_to_run = "call_bomb.py"
        elif user_choice == '2':
            script_to_run = "sms_bomb.py"
        elif user_choice == '3':
            script_to_run = "DoS.py" # Basit UDP Flood
        elif user_choice == '4':
            script_to_run = "netflix_checker.py" # İsim düzeltildi
        elif user_choice == '5':
            script_to_run = "base64decode.py"
        elif user_choice == '6':
            script_to_run = "iptool.py"
        elif user_choice == '7':
            script_to_run = "choromecast_hack.py" # İsim kontrol edildi
        elif user_choice == '8':
            script_to_run = "web_saldırı.py"
        elif user_choice == '9':
            script_to_run = "insta_saldırı.py"
        elif user_choice == '10':
            script_to_run = "sosyalmedya_bulma.py"
        elif user_choice == '11':
            script_to_run = "wifi_jammer.py"
        elif user_choice == '12':
            script_to_run = "DDoS.py" # Framework olan
        elif user_choice == '0':
            print(f"\n{B}{BRIGHT}Programdan çıkılıyor...{RESET}")
            time.sleep(0.5)
            break # Döngüden çık
        else:
            print(f"\n{R}{BRIGHT}Geçersiz seçim! Lütfen menüdeki numaralardan birini girin.{RESET}")
            time.sleep(1.5)
            # Geçersiz seçimse döngüye devam et (run_script çağrılmaz)
            continue

        # Sadece geçerli bir seçim yapıldıysa ve script atanmışsa run_script'i çağır
        if script_to_run:
             run_script(script_to_run)
        # 'else' kısmına gerek yok, çünkü geçersiz seçim 'continue' ile atlandı,
        # '0' seçimi 'break' ile döngüden çıktı.
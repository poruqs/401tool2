# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
from platform import system
from traceback import print_exc
from typing import Callable, List, Tuple, Any

# --- !!! ÇOK ÖNEMLİ YASAL UYARI !!! ---
# BU BETİK, WI-FI JAMMING VE DEAUTHENTICATION GİBİ YASA DIŞI EYLEMLER
# GERÇEKLEŞTİREBİLEN ARAÇLARI YÖNETMEK İÇİN BİR ARAYÜZ SAĞLAR.
# BU ARAÇLARIN İZİNSİZ KULLANIMI TÜRKİYE DAHİL ÇOĞU ÜLKEDE KESİNLİKLE
# YASAKTIR VE ÇOK CİDDİ YASAL SONUÇLARI (PARA/HAPİS CEZASI) OLABİLİR.
# BU TÜR ARAÇLAR ACİL DURUM İLETİŞİMİNİ ENGELLEYEBİLİR.
# BU KOD SADECE EĞİTİM AMAÇLIDIR VE KESİNLİKLE İZİNSİZ KULLANILMAMALIDIR.
# TÜM SORUMLULUK KULLANICIYA AİTTİR. GELİŞTİRİCİ SORUMLU TUTULAMAZ.
#
# ÇALIŞTIRMAK İÇİN UYUMLU DONANIM (MONİTÖR MODU/INJECTION DESTEKLİ WIFI KARTI),
# DOĞRU SÜRÜCÜLER, LINUX İŞLETİM SİSTEMİ VE ROOT YETKİSİ (SUDO) GEREKLİDİR.
# "MÜKEMMEL ÇALIŞMA" GARANTİSİ VERİLEMEZ.
# --- UYARI SONU ---


# Opsiyonel Colorama kurulumu ve renk tanımları
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
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
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli ('pip install colorama'). Renksiz devam ediliyor.")
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""
    class Style: BRIGHT = ""; DIM = ""; RESET_ALL = ""
    class Fore: RED = ""; GREEN = ""; YELLOW = ""; BLUE = ""; MAGENTA = ""; CYAN = ""; WHITE = ""

# === Yardımcı Fonksiyonlar ===

def clear_screen():
    """Terminal ekranını temizler."""
    # root yetkisiyle çalıştırıldığında 'clear' komutu bazen sorun çıkarabilir,
    # alternatif olarak escape kodu denenebilir ama os.system daha yaygın.
    os.system("cls" if system() == "Windows" else "clear")

def pause():
    """Devam etmek için Enter beklenir."""
    try:
        input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit()

# --- Yardımcı Fonksiyon: Aracın kurulu olup olmadığını kontrol et ---
def is_tool_installed(tool_name):
    """Basitçe komutun sistem PATH'inde olup olmadığını kontrol eder."""
    import shutil
    return shutil.which(tool_name) is not None

# === Temel Sınıflar (Framework Yapısı) ===
# (Bu sınıflar önceki framework betiklerindeki ile aynıdır)

class HackingTool(object):
    """Tek bir aracı temsil eden temel sınıf."""
    TITLE: str = "Başlıksız Araç"
    DESCRIPTION: str = "Açıklama Yok"
    INSTALL_COMMANDS: List[str] = []
    INSTALLATION_DIR: str = ""
    UNINSTALL_COMMANDS: List[str] = []
    RUN_COMMANDS: List[str] = []
    OPTIONS: List[Tuple[str, Callable]] = []
    PROJECT_URL: str = ""
    REQUIRES_ROOT: bool = True # Bu tür araçlar genellikle root gerektirir
    REQUIRES_LINUX: bool = True # Genellikle Linux gerekir
    REQUIRES_MONITOR_MODE: bool = True # Monitör modu gerekir

    def __init__(self, options: list = None, installable: bool = True, runnable: bool = True):
        options = options or []
        self.OPTIONS = []
        if installable and self.INSTALL_COMMANDS:
            self.OPTIONS.append(('Install', self.install))
        if runnable: # Çalıştırılabilirse Run ekle (özel run veya RUN_COMMANDS)
            self.OPTIONS.append(('Run', self.run))
        self.OPTIONS.extend(options)
        if self.UNINSTALL_COMMANDS:
             self.OPTIONS.append(('Uninstall', self.uninstall))

    def _check_prerequisites(self):
        """Temel önkoşulları kontrol eder."""
        if self.REQUIRES_ROOT and os.geteuid() != 0:
             print(f"{R}HATA: Bu işlem root yetkisi gerektirir. Lütfen 'sudo python3 ...' ile çalıştırın.{RESET}")
             return False
        if self.REQUIRES_LINUX and system() != "Linux":
             print(f"{R}HATA: Bu araç genellikle sadece Linux sistemlerde çalışır.{RESET}")
             return False
        if self.REQUIRES_MONITOR_MODE:
             # Monitör modunu programatik olarak kontrol etmek zordur.
             # Kullanıcıyı uyarmak daha iyidir.
             print(f"{Y}UYARI: Bu aracın çalışması için monitör modu ve paket enjeksiyonu destekleyen{RESET}")
             print(f"{Y}uyumlu bir Wi-Fi adaptörü ve doğru sürücüler gereklidir.{RESET}")
             # İsteğe bağlı: airmon-ng gibi araçların varlığını kontrol et
             # if not is_tool_installed("airmon-ng"):
             #      print(f"{Y}UYARI: 'airmon-ng' bulunamadı, Wi-Fi kartı uyumluluğunu kontrol edemeyebilirsiniz.{RESET}")
        return True

    def _execute_commands(self, command_list: List[str], target_dir: str = None):
        """Verilen komut listesini belirtilen dizinde sırayla çalıştırır."""
        # Önkoşul kontrolü (her komut çalıştırmadan önce yapılabilir)
        # if not self._check_prerequisites(): return False

        if not isinstance(command_list, (list, tuple)):
            print(f"{R}HATA: Komut listesi geçersiz.{RESET}")
            return False

        print(f"{C}--- Komutlar Çalıştırılıyor ---{RESET}")
        success = True
        effective_cwd = target_dir or self.INSTALLATION_DIR or None
        if effective_cwd and not os.path.isdir(effective_cwd):
             print(f"{Y}Uyarı: Hedef dizin '{effective_cwd}' mevcut değil. Komutlar mevcut dizinde çalıştırılacak.{RESET}")
             effective_cwd = None

        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")
            try:
                # sudo gerektiren komutlar için shell=True riskli olabilir ama 'cd &&' için bazen gerekli.
                # Komutların güvenilir repolardan geldiğini varsayıyoruz.
                subprocess.run(command, shell=True, check=True, cwd=effective_cwd)
            except FileNotFoundError as e:
                 print(f"{R}HATA: Komut veya program bulunamadı: {e}{RESET}")
                 print(f"{Y}Komut: '{command}'{RESET}")
                 print(f"{Y}Gerekli programın (örn: git, pip, gcc, bash) kurulu ve PATH'de olduğundan emin olun.{RESET}")
                 success = False; break
            except subprocess.CalledProcessError as e:
                print(f"{R}HATA: Komut hata ile sonlandı (Kod: {e.returncode}): {command}{RESET}")
                success = False; break
            except Exception as e:
                 print(f"{R}Komut çalıştırılırken beklenmedik hata: {command}\nHata: {e}{RESET}")
                 success = False; break

        status = f"{G}Başarılı{RESET}" if success else f"{R}Başarısız{RESET}"
        print(f"{C}--- Komutlar Tamamlandı (Durum: {status}) ---{RESET}")
        return success

    def show_info(self):
        """Aracın bilgilerini ve YASAL UYARILARI gösterir."""
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}") # Başlığı renkli yazdır
        # Açıklamadaki renk kodlarını hesaba kat
        clean_desc = self.DESCRIPTION # Zaten renkli olabilir
        print(clean_desc)
        # --- ZORUNLU YASAL UYARI ---
        print(f"\n{R}{BRIGHT}{'='*20} YASAL UYARI {'='*20}{RESET}")
        print(f"{R}BU ARACIN VEYA BENZERİ Wİ-Fİ JAMMER/DEAUTHENTICATOR ARAÇLARININ KULLANIMI")
        print(f"{R}TÜRKİYE DAHİL BİRÇOK ÜLKEDE KESİNLİKLE YASA DIŞIDIR.")
        print(f"{R}İZİNSİZ KULLANIM CİDDİ YASAL YAPTIRIMLARA YOL AÇABİLİR.")
        print(f"{R}ACİL DURUM İLETİŞİMİNİ VE AĞLARI ENGELLEYEBİLİR.")
        print(f"{Y}Bu araç sadece eğitim amaçlıdır. Tüm sorumluluk size aittir.{RESET}")
        print(f"{Y}Çalıştırmak için uyumlu donanım, sürücü ve root yetkisi gerekir.{RESET}")
        print(f"{R}{BRIGHT}{'='*55}{RESET}")

        if self.PROJECT_URL:
            print(f"\n{C}Proje Sayfası:{W} {self.PROJECT_URL}{RESET}")
        print("-" * (len(strip_colors(self.TITLE)) + 6)) # Başlığın renksiz uzunluğuna göre çizgi

    def show_options(self, parent=None):
        """Aracın seçeneklerini gösterir ve seçimi işler (Çalıştırma için ekstra onay)."""
        clear_screen()
        self.show_info() # Bilgi ve yasal uyarıları göster
        print(f"\n{Y}Seçenekler:{RESET}")
        valid_indices = list(range(1, len(self.OPTIONS) + 1))
        for index, option in enumerate(self.OPTIONS):
            option_name = option[0]
            # 'Run' seçeneğini özel olarak işaretle
            if option_name.lower() == 'run':
                 option_name += f" {R}{BRIGHT}(YASADIŞI! ÇOK RİSKLİ!){RESET}"
            print(f"  [{index + 1}] {option_name}")

        extra_options = {}
        if self.PROJECT_URL:
            extra_options[98] = "Proje Sayfasını Aç"
            print(f"  [{98}] {extra_options[98]}")

        parent_title = getattr(parent, 'TITLE', 'Ana Menü') if parent is not None else 'Çıkış'
        extra_options[99] = f"Geri ({parent_title})"
        print(f"  [{99}] {extra_options[99]}")

        option_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None

        try:
            option_index = int(option_index_str)
            if option_index in valid_indices:
                selected_option_name = self.OPTIONS[option_index - 1][0]
                selected_function = self.OPTIONS[option_index - 1][1]

                # === ÇALIŞTIRMA (RUN) İÇİN EKSTRA ONAY VE KONTROL ===
                if selected_option_name.lower() == 'run':
                    print(f"\n{R}{BRIGHT}!!! SON UYARI VE ONAY !!!{RESET}")
                    print(f"{R}'{self.TITLE}' aracını çalıştırmak üzeresiniz.")
                    print(f"{R}Bu işlemin yasa dışı olduğunu ve ciddi sonuçları olabileceğini anlıyor musunuz?")
                    print(f"{Y}Ayrıca uyumlu Wi-Fi kartı, sürücü ve root yetkisine sahip misiniz?{RESET}")
                    try:
                        confirm = input(f"{Y}Tüm riskleri ve yasal sorumluluğu kabul ediyorsanız ve devam etmek istiyorsanız 'EVET ONAYLIYORUM' yazın: {W}").strip()
                        if confirm != 'EVET ONAYLIYORUM':
                            print(f"{G}İşlem iptal edildi.{RESET}")
                            time.sleep(2)
                            # Menüyü tekrar gösterelim ki kullanıcı başka bir şey seçebilsin
                            return self.show_options(parent=parent)
                        else:
                             print(f"\n{R}!!! ONAY VERİLDİ - YASADIŞI İŞLEM BAŞLATILIYOR !!!{RESET}")
                             print(f"{R}!!! TÜM SORUMLULUK SİZE AİTTİR !!!{RESET}")
                             time.sleep(2)
                             # Onay alındıktan sonra önkoşulları kontrol et
                             if not self._check_prerequisites():
                                 # Önkoşullar sağlanmadıysa çalıştırma
                                 pause()
                                 return self.show_options(parent=parent)
                             # Önkoşullar TAMAM, asıl fonksiyonu çağır
                             ret_code = selected_function()
                    except KeyboardInterrupt:
                         print("\nOnay iptal edildi.")
                         return self.show_options(parent=parent) # Menüye dön
                else:
                    # 'Run' dışındaki seçenekler (Install, Uninstall vb.) için doğrudan fonksiyonu çağır
                    # Kurulum vs. öncesi de önkoşul kontrolü yapılabilir
                    if selected_option_name.lower() == 'install':
                         if not self._check_prerequisites(): # Temel kontroller (root/linux)
                              pause()
                              return self.show_options(parent=parent)
                    ret_code = selected_function()

                # Fonksiyon 99 (Geri) döndürmediyse Enter bekle
                if ret_code != 99: pause()

            elif option_index in extra_options:
                if option_index == 98:
                    self.show_project_page()
                    pause()
                elif option_index == 99:
                    if parent is None: sys.exit(print(f"{B}Çıkılıyor...{RESET}"))
                    return 99 # Bir üst menüye dön
            else:
                print(f"{R}Geçersiz seçenek.{RESET}")
                time.sleep(1)
        except (ValueError, TypeError):
             print(f"{R}Lütfen geçerli bir numara girin.{RESET}")
             time.sleep(1)
        except KeyboardInterrupt:
             print("\nİşlem iptal edildi.")
             return None # Ana menüye dön
        except Exception:
            print(f"{R}Bir hata oluştu!{RESET}")
            print_exc()
            pause()

        # 'Geri' (99) veya 'İptal' (None) değilse menüyü tekrar göster
        if ret_code != 99 and ret_code is not None:
            return self.show_options(parent=parent)
        else:
             return ret_code # 99 veya None ise yukarı taşı

    def before_install(self):
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")
        # Kurulum için de yasal uyarıyı gösterelim
        print(f"{Y}UYARI: Kurulacak araç ('{self.TITLE}') yasa dışı amaçlarla kullanılabilir.{RESET}")
        print(f"{Y}Sorumluluk tamamen size aittir.{RESET}")
        # Önkoşul kontrolü install içinde _execute_commands'dan önce yapılabilir veya burada.
        # if not self._check_prerequisites(): return False # Veya install içinde kontrol et

    def install(self):
        """Kurulum metodu."""
        self.before_install()
        # Kurulum komutlarını çalıştırmadan önce temel kontroller
        if not self._check_prerequisites():
             # Temel koşullar (root/linux) sağlanmadıysa kurma
             return False
        success = self._execute_commands(self.INSTALL_COMMANDS, target_dir=None)
        self.after_install(success)
        return success

    def after_install(self, success):
        if success:
            print(f"\n{G}{self.TITLE} kurulumu tamamlandı (hatalar için yukarıyı kontrol edin).{RESET}")
        else:
            print(f"\n{R}{self.TITLE} kurulumu başarısız oldu.{RESET}")

    def before_uninstall(self) -> bool:
        confirm = input(f"{Y}UYARI: {self.TITLE} kaldırılacak. Emin misiniz? [e/H]: {W}").strip().lower()
        return confirm == 'e'

    def uninstall(self):
        if self.before_uninstall():
            print(f"\n{C}{self.TITLE} kaldırılıyor...{RESET}")
            success = self._execute_commands(self.UNINSTALL_COMMANDS)
            self.after_uninstall(success)
            return success
        else:
            print("Kaldırma işlemi iptal edildi.")
            return False

    def after_uninstall(self, success):
        if success:
             print(f"\n{G}{self.TITLE} kaldırıldı.{RESET}")
        else:
            print(f"\n{R}Kaldırma işlemi başarısız oldu.{RESET}")


    def before_run(self):
        # Çalıştırma öncesi uyarı ve onay show_options içinde yapıldı.
        # Burası sadece çalıştırma mesajını verir.
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")
        print(f"{R}!!! YASADIŞI KULLANIMDAN KAÇININ !!!{RESET}")

    def run(self):
        """Varsayılan çalıştırma metodu (show_options'da onay alındıktan sonra çağrılır)."""
        self.before_run()
        success = False
        # RUN_COMMANDS varsa bunları INSTALLATION_DIR içinde çalıştır
        if self.RUN_COMMANDS:
             success = self._execute_commands(self.RUN_COMMANDS, target_dir=self.INSTALLATION_DIR)
        else:
            # Eğer alt sınıf run metodunu override etmediyse ve RUN_COMMANDS boşsa,
            # bu genellikle bir hatadır veya araç manuel çalıştırma gerektiriyordur.
            print(f"{Y}Bu araç için RUN_COMMANDS tanımlanmamış ve 'run' metodu override edilmemiş.{RESET}")
            print(f"{Y}Araç manuel olarak çalıştırılmalı veya betikte bir eksiklik var.{RESET}")
        self.after_run(success)
        return success

    def after_run(self, success):
        if success:
             print(f"\n{G}{self.TITLE} çalıştırıldı (veya tamamlandı).{RESET}")
        else:
             print(f"\n{R}{self.TITLE} çalıştırma işlemi başarısız oldu veya hata verdi.{RESET}")


class HackingToolsCollection(HackingTool):
    """Birden fazla aracı veya koleksiyonu gruplayan sınıf."""
    TITLE: str = "Başlıksız Koleksiyon"
    DESCRIPTION: str = "Açıklama Yok"
    TOOLS: List[Any[HackingTool, 'HackingToolsCollection']] = []
    REQUIRES_ROOT: bool = True # Koleksiyonun geneli root gerektirir
    REQUIRES_LINUX: bool = True
    REQUIRES_MONITOR_MODE: bool = True

    def __init__(self, title: str = "", description: str = "", tools: list = None):
        # Koleksiyonun kendisi kurulmaz/çalışmaz, sadece alt araçları listeler
        super().__init__(installable=False, runnable=False)
        self.TITLE = title or self.TITLE
        self.DESCRIPTION = description or self.DESCRIPTION
        self.TOOLS = tools or []

    def show_info(self):
        """Koleksiyon bilgilerini ve genel uyarıyı gösterir."""
        print(f"\n{M}{BRIGHT}=== {self.TITLE} ==={RESET}")
        # Koleksiyon açıklamasına da genel YASAL UYARI ekleyelim
        print(f"{R}{BRIGHT}UYARI: Bu koleksiyondaki araçlar Wi-Fi Jamming/Deauth içindir ve kullanımları YASAKTIR!{RESET}")
        print(f"{R}Donanım, sürücü, izin ve yasal sorumluluk gerektirirler.{RESET}")
        if self.DESCRIPTION:
            print(self.DESCRIPTION)
        print("=" * (len(strip_colors(self.TITLE)) + 6))

    def show_options(self, parent = None):
        """Koleksiyon içindeki araçları listeler."""
        clear_screen()
        self.show_info() # Bilgi ve genel uyarıyı göster
        print(f"\n{Y}Araçlar:{RESET}")
        valid_indices = list(range(len(self.TOOLS)))
        for index, tool in enumerate(self.TOOLS):
            # Araçların başlığını al (renkli olabilir)
            tool_title = getattr(tool, 'TITLE', f'İsimsiz Araç {index}')
            # Araç başlığı zaten uyarı içeriyorsa tekrar eklemeye gerek yok
            print(f"  [{index}] {tool_title}") # 0'dan başlatalım indeksi

        parent_title = getattr(parent, 'TITLE', 'Ana Menü') if parent is not None else 'Çıkış'
        print(f"\n  [{99}] Geri ({parent_title})")

        tool_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None

        try:
            tool_index = int(tool_index_str)
            if tool_index in valid_indices:
                selected_tool = self.TOOLS[tool_index]
                # Seçilen aracın kendi menüsünü göster (orada detaylı uyarılar ve onaylar olacak)
                ret_code = selected_tool.show_options(parent=self)
            elif tool_index == 99:
                if parent is None: sys.exit(print(f"{B}Çıkılıyor...{RESET}"))
                return 99 # Bir üst menüye dön
            else:
                print(f"{R}Geçersiz seçenek.{RESET}")
                time.sleep(1)
        except (ValueError, TypeError):
             print(f"{R}Lütfen geçerli bir numara girin.{RESET}")
             time.sleep(1)
        except KeyboardInterrupt:
             print("\nİşlem iptal edildi.")
             return None # Ana menüye dön
        except Exception:
            print(f"{R}Bir hata oluştu!{RESET}")
            print_exc()
            pause()

        # Eğer alt menüden 'Geri' (99) veya 'İptal' (None) gelinmediyse, bu menüyü tekrar göster
        if ret_code != 99 and ret_code is not None:
            return self.show_options(parent=parent)
        else:
             return ret_code # 99 veya None ise yukarı taşı


# === Wi-Fi Jamming/Deauthentication Araç Tanımlamaları ===

class WifiJammerNG(HackingTool):
    # Başlıkta uyarıyı güçlendir
    TITLE = f"WifiJammer-NG {R}{BRIGHT}(YASADIŞI!){RESET}"
    DESCRIPTION = "Yakındaki TÜM Wi-Fi istemcilerini ve erişim noktalarını sürekli olarak jammer (sinyal bozar)."
    INSTALLATION_DIR = "wifijammer-ng"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/MisterBianco/wifijammer-ng.git {INSTALLATION_DIR}",
        # Pip bağımlılıkları (sudo gerekebilir/gerekmeyebilir)
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install -r requirements.txt"
    ]
    # RUN_COMMANDS önce kullanım örneği gösterir, sonra aracı çalıştırmayı dener.
    # Bu araç interaktif veya argüman gerektirebilir, bu yüzden basit çalıştırma başarısız olabilir.
    RUN_COMMANDS = [
        'echo "\n--- Kullanım Örneği (Arayüzü ve Kanalı Belirtmeniz GEREKİR!) ---"',
        'echo "sudo python wifijammer.py --accesspoint <AP_MAC> -c <Kanal> -i <ArayüzAdı>"',
        'echo "Tüm ağları jam etmek için: sudo python wifijammer.py -m -c <Kanal> -i <ArayüzAdı>"',
        'echo "------------------------------------------------------------------\n"',
        # Doğrudan çalıştırma (kullanıcıdan parametre girmesini bekler veya hata verir)
        f"sudo {sys.executable} wifijammer.py"
    ]
    PROJECT_URL = "https://github.com/MisterBianco/wifijammer-ng"
    # Root, Linux, Monitor Modu gerektirir (varsayılanlar True)

class KawaiiDeauther(HackingTool):
    TITLE = f"KawaiiDeauther {R}{BRIGHT}(YASADIŞI!){RESET}"
    DESCRIPTION = (
        "Wi-Fi istemcilerine/routerlarına deauth/jam saldırıları yapmayı ve test amacıyla\n"
        "birçok sahte AP (Erişim Noktası) yaymayı hedefleyen bir araç kiti.\n"
        f"{Y}(Bash betiği ile çalışır){RESET}"
    )
    INSTALLATION_DIR = "KawaiiDeauther"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/aryanrtm/KawaiiDeauther.git {INSTALLATION_DIR}",
        # Kurulum betiğini çalıştır
        f"cd {INSTALLATION_DIR} && sudo bash install.sh"
    ]
    # Çalıştırma için ana betiği kullanır (interaktif olmalı)
    RUN_COMMANDS = ["sudo bash KawaiiDeauther.sh"]
    PROJECT_URL = "https://github.com/aryanrtm/KawaiiDeauther"
    # Root, Linux, Monitor Modu gerektirir

    def install(self):
        # Bash kontrolü
        if not is_tool_installed("bash"):
             print(f"{R}HATA: 'bash' komutu bulunamadı. Kurulum ve çalıştırma için gereklidir.{RESET}")
             return False
        return super().install()

    def run(self):
        # Bash kontrolü
        if not is_tool_installed("bash"):
             print(f"{R}HATA: 'bash' komutu bulunamadığı için araç çalıştırılamıyor.{RESET}")
             return False
        # Kurulum dizini kontrolü
        if not os.path.isdir(self.INSTALLATION_DIR) or not os.path.isfile(os.path.join(self.INSTALLATION_DIR, "KawaiiDeauther.sh")):
            print(f"{R}HATA: '{self.INSTALLATION_DIR}' veya içindeki 'KawaiiDeauther.sh' bulunamadı.{RESET}")
            print(f"{Y}Lütfen önce aracı kurun ('Install' seçeneği).{RESET}")
            return False
        return super().run()


# === Ana Koleksiyon Tanımı ===
class WifiJammingTools(HackingToolsCollection):
    # Başlıkta uyarıyı ZORUNLU hale getirelim
    TITLE = f"!!! Wi-Fi Deauthenticate/Jamming Araçları {R}{BRIGHT}(YASADIŞI!) !!!{RESET}"
    DESCRIPTION = (f"{R}{BRIGHT}UYARI: BU ARAÇLARIN KULLANIMI ÇOĞU ÜLKEDE YASA DIŞIDIR VE ÖNERİLMEZ!{RESET}\n"
                   f"{Y}Sadece yasal izinle, kontrollü test ortamlarında ve eğitim amacıyla kullanılmalıdır.{RESET}")
    TOOLS = [
        WifiJammerNG(),
        KawaiiDeauther()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    # --- BETİK BAŞLANGICINDA ZORUNLU UYARI GÖSTER ---
    clear_screen()
    print(f"{R}{BRIGHT}############################################################{RESET}")
    print(f"{R}{BRIGHT}# {Y}{BRIGHT}           !!! ÖNEMLİ YASAL UYARI !!!           {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}#----------------------------------------------------------#{RESET}")
    print(f"{R}{BRIGHT}# {W}Bu betik, Wi-Fi Jamming ve Deauthentication gibi       {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {W}potansiyel olarak {R}YASA DIŞI{W} araçları yönetir.         {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {R}Bu araçların İZİNSİZ kullanımı Türkiye dahil birçok    {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {R}ülkede YASAKTIR ve ciddi yasal sonuçları olabilir.     {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {W}Bu tür araçlar sadece YASAL İZİNLE, KONTROLLÜ TEST     {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {W}ORTAMLARINDA ve EĞİTİM amacıyla kullanılmalıdır.       {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {Y}Çalıştırmak için uyumlu donanım, sürücü, Linux ve root {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {Y}yetkisi gereklidir. Çalışma garantisi yoktur.          {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}#----------------------------------------------------------#{RESET}")
    print(f"{R}{BRIGHT}# {W}Bu betiği kullanarak tüm riskleri ve yasal             {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {W}sorumluluğu KABUL ETMİŞ sayılırsınız. Yanlış           {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}# {W}kullanımdan geliştirici KESİNLİKLE sorumlu tutulamaz.  {R}{BRIGHT} #{RESET}")
    print(f"{R}{BRIGHT}############################################################{RESET}")
    print("\n")

    # Kullanıcıdan başlangıç onayı al
    try:
        confirm = input(f"{Y}Yukarıdaki uyarıları okuyup anladınız mı? Riskleri kabul ediyor musunuz?\nDevam etmek için 'evet anladim' yazın: {W}").strip().lower()
        if confirm != 'evet anladim':
            print(f"{R}Onay verilmedi, programdan çıkılıyor.{RESET}")
            sys.exit(0)
        else:
            print(f"{G}Uyarılar anlaşıldı. Araç menüsü yükleniyor...{RESET}")
            time.sleep(1.5)
    except KeyboardInterrupt:
         print("\nÇıkılıyor...")
         sys.exit(0)

    # Ana koleksiyonu oluştur ve menüyü başlat
    main_collection = WifiJammingTools()
    try:
         # Root kontrolünü menüyü göstermeden önce yapalım
         if not main_collection._check_prerequisites():
              print(f"{R}Gerekli önkoşullar sağlanamadığı için devam edilemiyor.{RESET}")
              sys.exit(1)
         # Önkoşullar tamamsa menüyü göster
         main_collection.show_options()
    except KeyboardInterrupt:
         print(f"\n{B}Program kullanıcı tarafından sonlandırıldı.{RESET}")
    except Exception:
         print(f"\n{R}Kritik bir hata oluştu!{RESET}")
         print_exc()
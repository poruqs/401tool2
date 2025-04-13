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
    os.system("cls" if system() == "Windows" else "clear")

def pause():
    """Devam etmek için Enter beklenir."""
    try:
        input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit()

# === Temel Sınıflar (core.py yerine buraya entegre edildi) ===

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

    def __init__(self, options: list = None, installable: bool = True, runnable: bool = True):
        options = options or []
        self.OPTIONS = []
        if installable and self.INSTALL_COMMANDS:
            self.OPTIONS.append(('Install', self.install))
        if runnable or self.RUN_COMMANDS:
            self.OPTIONS.append(('Run', self.run))
        self.OPTIONS.extend(options)
        if self.UNINSTALL_COMMANDS:
             self.OPTIONS.append(('Uninstall', self.uninstall))

    def _execute_commands(self, command_list: List[str], target_dir: str = None):
        """Verilen komut listesini belirtilen dizinde sırayla çalıştırır."""
        if not isinstance(command_list, (list, tuple)):
            print(f"{R}HATA: Komut listesi geçersiz.{RESET}")
            return False

        print(f"{C}--- Komutlar Çalıştırılıyor ---{RESET}")
        success = True
        effective_cwd = target_dir if (target_dir and os.path.isdir(target_dir)) else None

        for command in command_list:
            # Güvenlik Notu: shell=True risklidir, özellikle sudo ile!
            # Komutların güvenilir kaynaklardan geldiğinden emin olunmalı.
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")

            try:
                # 'cd ... && ...' gibi yapılar için shell=True gerekli olabilir
                subprocess.run(command, shell=True, check=True, cwd=effective_cwd)
            except FileNotFoundError as e:
                 print(f"{R}HATA: Komut veya program bulunamadı: {e}{RESET}")
                 print(f"{Y}Komut: '{command}'{RESET}")
                 success = False
                 break
            except subprocess.CalledProcessError as e:
                print(f"{R}HATA: Komut hata ile sonlandı (Kod: {e.returncode}): {command}{RESET}")
                success = False
                break
            except Exception as e:
                 print(f"{R}Komut çalıştırılırken beklenmedik hata: {command}\nHata: {e}{RESET}")
                 success = False
                 break

        status = f"{G}Başarılı{RESET}" if success else f"{R}Başarısız{RESET}"
        print(f"{C}--- Komutlar Tamamlandı (Durum: {status}) ---{RESET}")
        return success

    def show_info(self):
        """Aracın bilgilerini gösterir."""
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        clean_desc = self.DESCRIPTION.replace('\n\b', '\n').replace(' | boxes | lolcat', '')
        print(clean_desc)
        # ÖNEMLİ YASAL UYARI EKLEYELİM
        if "jammer" in self.TITLE.lower() or "deauth" in self.TITLE.lower():
             print(f"\n{R}{BRIGHT}!!! YASAL UYARI !!!{RESET}")
             print(f"{R}Bu tür araçların (Wi-Fi Jammer/Deauther) kullanımı Türkiye dahil birçok ülkede YASA DIŞIDIR.{RESET}")
             print(f"{R}Bu aracı çalıştırmak ciddi yasal sonuçlar doğurabilir ve iletişimi engelleyebilir.{RESET}")
             print(f"{Y}Bu kod yalnızca eğitim amaçlıdır, KESİNLİKLE ÇALIŞTIRMAYINIZ!{RESET}")

        if self.PROJECT_URL:
            print(f"\n{C}Proje Sayfası:{W} {self.PROJECT_URL}{RESET}")
        print("-" * (len(self.TITLE) + 6))


    def show_options(self, parent=None):
        """Aracın seçeneklerini gösterir ve seçimi işler."""
        clear_screen()
        self.show_info()
        print(f"\n{Y}Seçenekler:{RESET}")
        valid_indices = list(range(1, len(self.OPTIONS) + 1))
        for index, option in enumerate(self.OPTIONS):
            # Çalıştırma seçeneği ise ekstra uyarı ekle
            option_name = option[0]
            if option_name.lower() == 'run' and ("jammer" in self.TITLE.lower() or "deauth" in self.TITLE.lower()):
                 option_name += f" {R}{BRIGHT}(YASADIŞI!){RESET}"
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

                # Çalıştırma seçildiyse ve tehlikeli bir araçsa son bir uyarı ver
                if selected_option_name.lower() == 'run' and ("jammer" in self.TITLE.lower() or "deauth" in self.TITLE.lower()):
                    print(f"\n{R}{BRIGHT}!!! SON UYARI !!!{RESET}")
                    print(f"{R}Wi-Fi Jammer/Deauther çalıştırmak YASAKTIR ve ciddi sonuçları vardır.{RESET}")
                    confirm = input(f"{Y}Riskleri anladığınızı ve tüm sorumluluğu aldığınızı onaylamak için 'EVET' yazın: {W}").strip()
                    if confirm != 'EVET':
                        print(f"{G}İşlem iptal edildi.{RESET}")
                        time.sleep(2)
                        # Menüyü tekrar gösterelim
                        return self.show_options(parent=parent)
                    else:
                         print(f"{R}YASADIŞI İŞLEM BAŞLATILIYOR...{RESET}") # Yine de uyarıyoruz

                ret_code = selected_function()
                if ret_code != 99: pause()

            elif option_index in extra_options:
                if option_index == 98:
                    self.show_project_page()
                    pause()
                elif option_index == 99:
                    if parent is None: sys.exit(print(f"{B}Çıkılıyor...{RESET}"))
                    return 99
            else:
                print(f"{R}Geçersiz seçenek.{RESET}")
                time.sleep(1)
        except (ValueError, TypeError):
             print(f"{R}Lütfen geçerli bir numara girin.{RESET}")
             time.sleep(1)
        except Exception:
            print(f"{R}Bir hata oluştu!{RESET}")
            print_exc()
            pause()

        if ret_code != 99:
            return self.show_options(parent=parent)
        else:
             return 99

    def before_install(self):
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")
        # Jammer/Deauther kurulumu için de uyarı eklenebilir
        if "jammer" in self.TITLE.lower() or "deauth" in self.TITLE.lower():
            print(f"{Y}UYARI: Kurulacak araç yasadışı amaçlarla kullanılabilir. Sorumluluk size aittir.{RESET}")

    def install(self):
        self.before_install()
        self._execute_commands(self.INSTALL_COMMANDS, target_dir=None)
        self.after_install()

    def after_install(self):
        print(f"\n{G}{self.TITLE} kurulumu tamamlandı (hatalar için yukarıyı kontrol edin).{RESET}")

    def before_uninstall(self) -> bool:
        confirm = input(f"{Y}UYARI: {self.TITLE} kaldırılacak. Emin misiniz? [e/H]: {W}").strip().lower()
        return confirm == 'e'

    def uninstall(self):
        if self.before_uninstall():
            print(f"\n{C}{self.TITLE} kaldırılıyor...{RESET}")
            self._execute_commands(self.UNINSTALL_COMMANDS)
            self.after_uninstall()

    def after_uninstall(self):
        print(f"\n{G}{self.TITLE} kaldırıldı.{RESET}")

    def before_run(self):
        # Bu tehlikeli araçlar için çalıştırma öncesi uyarı zaten show_options içinde var
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")

    def run(self):
        """Varsayılan çalıştırma metodu. RUN_COMMANDS listesini çalıştırır."""
        # Çalıştırma öncesi kontroller ve uyarılar show_options içinde yapıldı
        self.before_run()
        if not self.RUN_COMMANDS:
            print(f"{Y}Bu araç için özel bir 'run' metodu veya RUN_COMMANDS tanımlanmamış.{RESET}")
        else:
             self._execute_commands(self.RUN_COMMANDS, target_dir=self.INSTALLATION_DIR)
        self.after_run()

    def after_run(self):
        pass

    def show_project_page(self):
        if self.PROJECT_URL:
            try:
                print(f"{C}Proje sayfası açılıyor: {self.PROJECT_URL}{RESET}")
                webbrowser.open_new_tab(self.PROJECT_URL)
            except Exception as e:
                print(f"{R}Tarayıcı açılırken hata: {e}{RESET}")
        else:
            print(f"{Y}Proje URL'si belirtilmemiş.{RESET}")


class HackingToolsCollection(HackingTool):
    """Birden fazla aracı veya koleksiyonu gruplayan sınıf."""
    TITLE: str = "Başlıksız Koleksiyon"
    DESCRIPTION: str = "Açıklama Yok"
    TOOLS: List[Any[HackingTool, 'HackingToolsCollection']] = []

    def __init__(self, title: str = "", description: str = "", tools: list = None):
        super().__init__(installable=False, runnable=False)
        self.TITLE = title or self.TITLE
        self.DESCRIPTION = description or self.DESCRIPTION
        self.TOOLS = tools or []

    def show_info(self):
        """Koleksiyon bilgilerini gösterir."""
        print(f"\n{M}{BRIGHT}=== {self.TITLE} ==={RESET}")
        # Koleksiyon açıklamasına da genel uyarı ekleyelim
        if "wifi" in self.TITLE.lower() or "deauth" in self.TITLE.lower():
             print(f"{R}{BRIGHT}UYARI: Bu koleksiyondaki araçların kullanımı YASADIŞIDIR!{RESET}")
        if self.DESCRIPTION:
            print(self.DESCRIPTION)
        print("=" * (len(self.TITLE) + 6))

    def show_options(self, parent = None):
        """Koleksiyon içindeki araçları listeler."""
        clear_screen()
        self.show_info()
        print(f"\n{Y}Araçlar:{RESET}")
        valid_indices = list(range(len(self.TOOLS)))
        for index, tool in enumerate(self.TOOLS):
            tool_title = getattr(tool, 'TITLE', f'İsimsiz Araç {index}')
            # Tehlikeli araçları menüde de işaretle
            if "jammer" in tool_title.lower() or "deauth" in tool_title.lower():
                 tool_title += f" {R}{BRIGHT}(YASADIŞI!){RESET}"
            print(f"  [{index}] {tool_title}")

        parent_title = getattr(parent, 'TITLE', 'Ana Menü') if parent is not None else 'Çıkış'
        print(f"\n  [{99}] Geri ({parent_title})")

        tool_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None

        try:
            tool_index = int(tool_index_str)
            if tool_index in valid_indices:
                selected_tool = self.TOOLS[tool_index]
                ret_code = selected_tool.show_options(parent=self)
            elif tool_index == 99:
                if parent is None: sys.exit(print(f"{B}Çıkılıyor...{RESET}"))
                return 99
            else:
                print(f"{R}Geçersiz seçenek.{RESET}")
                time.sleep(1)
        except (ValueError, TypeError):
             print(f"{R}Lütfen geçerli bir numara girin.{RESET}")
             time.sleep(1)
        except Exception:
            print(f"{R}Bir hata oluştu!{RESET}")
            print_exc()
            pause()

        if ret_code != 99:
            return self.show_options(parent=parent)
        else:
             return 99

# === Wi-Fi Jamming/Deauthentication Araç Tanımlamaları ===

class WifiJammerNG(HackingTool):
    TITLE = "WifiJammer-NG"
    DESCRIPTION = "Yakındaki tüm Wi-Fi istemcilerini ve erişim noktalarını sürekli olarak jammer (sinyal bozar)."
    INSTALLATION_DIR = "wifijammer-ng"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/MisterBianco/wifijammer-ng.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install -r requirements.txt"
    ]
    # RUN_COMMANDS ilk önce yardım/kullanım örneğini gösterir (styling kaldırıldı)
    # İkinci komut aracı doğrudan çalıştırır.
    RUN_COMMANDS = [
        'echo "Kullanım Örneği: python wifijammer.py --accesspoint <AP_MAC> -c <Kanal> -i <Arayüz>"',
        f"sudo {sys.executable} wifijammer.py" # Bu interaktif olabilir veya argüman gerektirebilir
    ]
    PROJECT_URL = "https://github.com/MisterBianco/wifijammer-ng"


class KawaiiDeauther(HackingTool):
    TITLE = "KawaiiDeauther"
    DESCRIPTION = (
        "Wi-Fi istemcilerine/routerlarına jam uygulamayı ve test amacıyla\n"
        "birçok sahte AP yaymayı hedefleyen bir pentest araç kiti."
    )
    INSTALLATION_DIR = "KawaiiDeauther"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/aryanrtm/KawaiiDeauther.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo bash install.sh"
    ]
    RUN_COMMANDS = ["sudo bash KawaiiDeauther.sh"] # İnteraktif bir betik olmalı
    PROJECT_URL = "https://github.com/aryanrtm/KawaiiDeauther"


class WifiJammingTools(HackingToolsCollection):
    TITLE = f"Wi-Fi Deauthenticate/Jamming Araçları {R}{BRIGHT}(YASADIŞI!){RESET}"
    DESCRIPTION = f"{R}{BRIGHT}UYARI: BU ARAÇLARIN KULLANIMI ÇOĞU ÜLKEDE YASA DIŞIDIR VE ÖNERİLMEZ!{RESET}"
    TOOLS = [
        WifiJammerNG(),
        KawaiiDeauther()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    # ÖNEMLİ UYARI GÖSTER
    clear_screen()
    print(f"{R}{BRIGHT}############################################################{RESET}")
    print(f"{R}{BRIGHT}#                      YASAL UYARI                         #{RESET}")
    print(f"{R}{BRIGHT}#----------------------------------------------------------#{RESET}")
    print(f"{R}{BRIGHT}# Bu betik, Wi-Fi Jamming ve Deauthentication gibi         #{RESET}")
    print(f"{R}{BRIGHT}# potansiyel olarak yasa dışı araçları yönetmek için       #{RESET}")
    print(f"{R}{BRIGHT}# bir arayüz sağlar. Bu araçların İZİNSİZ kullanımı        #{RESET}")
    print(f"{R}{BRIGHT}# Türkiye dahil birçok ülkede YASAKTIR ve ciddi yasal      #{RESET}")
    print(f"{R}{BRIGHT}# sonuçları olabilir. Bu tür araçlar sadece yasal          #{RESET}")
    print(f"{R}{BRIGHT}# izinle, kontrollü test ortamlarında kullanılmalıdır.     #{RESET}")
    print(f"{R}{BRIGHT}#                                                          #{RESET}")
    print(f"{R}{BRIGHT}# Bu betiği kullanarak tüm sorumluluğu kabul etmiş         #{RESET}")
    print(f"{R}{BRIGHT}# sayılırsınız. Yanlış kullanımdan geliştirici sorumlu     #{RESET}")
    print(f"{R}{BRIGHT}# tutulamaz.                                               #{RESET}")
    print(f"{R}{BRIGHT}############################################################{RESET}")
    print("\n")
    confirm = input(f"{Y}Yukarıdaki uyarıları okuyup anladınız mı? Devam etmek için 'evet' yazın: {W}").strip().lower()

    if confirm == 'evet':
        main_collection = WifiJammingTools()
        try:
             main_collection.show_options()
        except KeyboardInterrupt:
             print(f"\n{B}Program sonlandırıldı.{RESET}")
        except Exception:
             print(f"\n{R}Kritik bir hata oluştu!{RESET}")
             print_exc()
    else:
        print(f"{R}Onay verilmedi, programdan çıkılıyor.{RESET}")
        sys.exit(0)
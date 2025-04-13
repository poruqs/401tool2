# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
# Bu betik için json, socket, ipaddress gerekmiyor gibi görünüyor
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
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")

            try:
                # shell=True, 'cd ... && ...' gibi yapıları çalıştırır ama güvenlik riski!
                # Özellikle sudo ile birlikte daha riskli olabilir.
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
        clean_desc = self.DESCRIPTION.replace('\n\b', '\n').replace(' | boxes | lolcat', '') # Styling komutlarını temizle
        print(clean_desc)
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
            print(f"  [{index + 1}] {option[0]}")

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
                selected_function = self.OPTIONS[option_index - 1][1]
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

    def install(self):
        """Varsayılan kurulum metodu. INSTALL_COMMANDS'ı çalıştırır."""
        self.before_install()
        self._execute_commands(self.INSTALL_COMMANDS, target_dir=None) # Komutlar kendi cd'sini içerebilir
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
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")

    def run(self):
        """Varsayılan çalıştırma metodu. RUN_COMMANDS listesini çalıştırır."""
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

# === Sosyal Medya Bulucu Araç Tanımlamaları ===

class FacialFind(HackingTool):
    TITLE = "Sosyal Medya Bulucu (Yüz Tanıma)"
    DESCRIPTION = (
        "Farklı sitelerdeki profilleri yüz tanıma yoluyla ilişkilendiren\n"
        "bir Sosyal Medya Haritalama Aracı (Social Mapper).\n\n"
        f"{R}{BRIGHT}UYARI: Kurulumu karmaşıktır, manuel adımlar ve ek bağımlılıklar gerektirir!{RESET}"
    )
    INSTALLATION_DIR = "social_mapper"
    # Kurulum komutları OS bağımlı (apt) ve karmaşık
    INSTALL_COMMANDS = [
        # Debian/Ubuntu için bağımlılıklar ve PPA ekleme
        "echo '--- Sistem paketleri güncelleniyor ve bağımlılıklar kuruluyor (sudo gerektirir) ---' && sudo apt update && sudo apt install -y software-properties-common build-essential cmake libgtk-3-dev libboost-all-dev",
        # Firefox PPA (Social Mapper'ın belirli bir FF sürümüne ihtiyacı olabilir)
        "echo '--- Firefox PPA ekleniyor (sudo gerektirir) ---' && sudo add-apt-repository -y ppa:mozillateam/firefox-next && sudo apt update",
        # Social Mapper'ı klonla
        f"echo '--- Social Mapper klonlanıyor ---' && sudo git clone https://github.com/Greenwolf/social_mapper.git {INSTALLATION_DIR}",
        # Python bağımlılıklarını kur (dizin içinde)
        f"echo '--- Python bağımlılıkları kuruluyor (sudo ve pip gerektirir) ---' && cd {os.path.join(INSTALLATION_DIR, 'setup')} && sudo {sys.executable} -m pip install --no-cache-dir -r requirements.txt",
        # Manuel Adımlar İçin Uyarı (boxes/lolcat kaldırıldı)
        (
            f"echo '\n{Y}{BRIGHT}--- MANUEL KURULUM GEREKLİ! ---{RESET}\n"
            f"{Y}[!] İşletim sisteminiz için Geckodriver'ı kurmanız gerekiyor.{RESET}\n"
            f"{Y}[!] İndirme Linki: https://github.com/mozilla/geckodriver/releases{RESET}\n"
            f"{Y}[!] Linux'ta indirip /usr/local/bin veya /usr/bin gibi PATH içindeki bir yere taşıyın.{RESET}\n"
            f"{Y}[!] Ardından social_mapper.py içindeki kullanıcı adı/şifre ayarlarını yapın.{RESET}'"
        )
    ]
    PROJECT_URL = "https://github.com/Greenwolf/social_mapper"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        run_dir = os.path.join(self.INSTALLATION_DIR, "setup") # Çalıştırılacak dizin farklı
        script_name = "social_mapper.py"
        script_path = os.path.join(run_dir, script_name)

        if not os.path.exists(run_dir) or not os.path.exists(script_path):
            print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Kurulumu yapın ('Install') ve manuel adımları tamamladığınızdan emin olun.{RESET}")
            return

        # Yardım menüsünü göster ve ek talimatlar ver
        print(f"\n{C}Social Mapper yardım menüsü gösteriliyor...{RESET}")
        command_help = ["sudo", sys.executable, script_path, "-h"]
        try:
             subprocess.run(command_help, check=True) # cwd burada gereksiz
        except Exception as e:
             print(f"{R}Yardım menüsü gösterilirken hata: {e}{RESET}")

        print(f"""\n{Y}{BRIGHT}--- Önemli Ayarlar ---{RESET}
{C}Çalıştırmadan önce '{script_path}' dosyasını açıp{RESET}
{C}kullanmak istediğiniz sosyal medya hesaplarının (gerçek veya sahte){RESET}
{C}kullanıcı adı ve şifrelerini ilgili bölümlere girmeniz GEREKİR!{RESET}
{Y}---------------------{RESET}""")

        print(f"""\n{Y}{BRIGHT}--- Örnek Kullanım ---{RESET}
{G}sudo python3 {script_path} -f <input_folder> -i <image_folder> -m fast -fb -tw{RESET}
{C}(<input_folder>: Kişi isimlerinin olduğu klasör, <image_folder>: Yüz resimlerinin olduğu klasör){RESET}
{Y}-------------------{RESET}""")
        # echo "python social_mapper.py -f [<imageFoldername>] -i [<imgFolderPath>] -m fast [<AcName>] -fb -tw" | boxes | lolcat'


class FindUser(HackingTool):
    TITLE = "Kullanıcı Adı Bulucu (finduser)"
    DESCRIPTION = "+75 sosyal ağda kullanıcı adlarını arar."
    INSTALLATION_DIR = "finduser"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/xHak9x/finduser.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo chmod +x finduser.sh"
    ]
    # run metodu override edilmediği için RUN_COMMANDS kullanılır
    RUN_COMMANDS = ["sudo bash finduser.sh"] # Bu betik interaktif olmalı
    PROJECT_URL = "https://github.com/xHak9x/finduser"


class Sherlock(HackingTool):
    TITLE = "Sherlock (Username Finder)"
    DESCRIPTION = (
        "Sosyal ağlarda kullanıcı adıyla hesap arar.\n"
        f"{Y}Daha fazla kullanım için:{W} python3 sherlock --help{RESET}"
    )
    INSTALLATION_DIR = "sherlock"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/sherlock-project/sherlock.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install -r requirements.txt"
    ]
    PROJECT_URL = "https://github.com/sherlock-project/sherlock"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        run_dir = self.INSTALLATION_DIR
        script_name = "sherlock" # Kurulum sonrası komut adı
        script_path = os.path.join(run_dir, script_name) # Betiğin tam yolu

        if not os.path.exists(run_dir) or not os.path.exists(script_path):
            print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
            print("Kurulumu yapın ('Install').")
            return

        name = input(f" Aranacak Kullanıcı Ad(lar)ı (boşlukla ayırın) [{self.TITLE}] >> ")
        if not name:
            print(f"{R}HATA: Kullanıcı adı boş olamaz.{RESET}")
            return

        # Kullanıcı adlarını ayır
        usernames = name.split()
        # Timeout, output file gibi ek parametreler sorulabilir
        timeout = input(f" Zaman Aşımı (saniye, boş bırakırsanız varsayılan) [{self.TITLE}] >> ").strip()
        output_file = input(f" Çıktı Dosyası (isteğe bağlı) [{self.TITLE}] >> ").strip()

        command = ["sudo", sys.executable, script_path] # sudo gerekebilir mi? Deneyelim.
        command.extend(usernames)
        if timeout and timeout.isdigit(): command.extend(["--timeout", timeout])
        if output_file: command.extend(["--output", output_file])
        # Örnek: command.append("--print-found") # Sadece bulunanları yazdır

        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            # Sherlock kendi dizininden çalışmalı
            subprocess.run(command, cwd=run_dir, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: '{sys.executable}', 'sudo' veya '{script_path}' bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: Sherlock hatası (Kod: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")


class SocialScan(HackingTool):
    TITLE = "SocialScan (Username/Email Check)"
    DESCRIPTION = (
        "Çevrimiçi platformlarda kullanıcı adı ve e-posta adresinin \n"
        "kullanılabilirliğini %100 doğrulukla kontrol eder."
    )
    # Pip ile kurulur, INSTALLATION_DIR gereksiz
    INSTALL_COMMANDS = [f"sudo {sys.executable} -m pip install socialscan"]
    PROJECT_URL = "https://github.com/iojw/socialscan"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        # socialscan komutunun PATH'de olduğunu varsayalım
        if not self._is_tool_installed("socialscan"):
             print(f"{R}HATA: 'socialscan' komutu bulunamadı. Kurulum başarılı oldu mu ('Install')?{RESET}")
             return

        name = input(f" Kullanıcı Adı veya Email (birden fazlaysa boşlukla ayırın) [{self.TITLE}] >> ")
        if not name:
             print(f"{R}HATA: Girdi boş olamaz.{RESET}")
             return

        # Girdiyi boşluklara göre ayır
        targets = name.split()
        command = ["sudo", "socialscan"] # sudo gerekebilir mi? Deneyelim.
        command.extend(targets)

        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: 'socialscan' veya 'sudo' komutu bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: SocialScan hatası (Kod: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")

    # Dirb'den kopyalanan yardımcı fonksiyon
    def _is_tool_installed(self, tool_name):
        """Basitçe komutun PATH içinde olup olmadığını kontrol eder."""
        import shutil
        return shutil.which(tool_name) is not None


class SocialMediaFinderTools(HackingToolsCollection):
    TITLE = "Sosyal Medya Bulucu Araçlar"
    DESCRIPTION = "Kullanıcı adı, e-posta veya yüz tanıma ile sosyal medya profillerini bulma araçları."
    TOOLS = [
        FacialFind(),
        FindUser(),
        Sherlock(),
        SocialScan()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    main_collection = SocialMediaFinderTools()
    try:
         main_collection.show_options()
    except KeyboardInterrupt:
         print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception:
         print(f"\n{R}Kritik bir hata oluştu!{RESET}")
         print_exc()
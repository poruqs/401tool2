# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
# Bu betik için json, socket, ipaddress gerekmiyor gibi görünüyor
# import json
# import socket
# import ipaddress
from platform import system
from traceback import print_exc
from typing import Callable, List, Tuple, Any # Typing eklendi

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
    INSTALLATION_DIR: str = "" # Kurulum dizini (varsa, komutlar burada çalıştırılır)
    UNINSTALL_COMMANDS: List[str] = []
    RUN_COMMANDS: List[str] = [] # run override edilmezse bunlar çalışır
    OPTIONS: List[Tuple[str, Callable]] = []
    PROJECT_URL: str = ""

    def __init__(self, options: list = None, installable: bool = True, runnable: bool = True):
        options = options or []
        self.OPTIONS = []
        # Kurulum komutları varsa ve installable True ise Install ekle
        if installable and self.INSTALL_COMMANDS:
            self.OPTIONS.append(('Install', self.install))
        # Çalıştırılabilirse veya RUN_COMMANDS varsa Run ekle
        if runnable or self.RUN_COMMANDS:
            self.OPTIONS.append(('Run', self.run))
        self.OPTIONS.extend(options)
        if self.UNINSTALL_COMMANDS:
             self.OPTIONS.append(('Uninstall', self.uninstall))

    def _execute_commands(self, command_list: List[str], target_dir: str = None):
        """Verilen komut listesini belirtilen dizinde sırayla çalıştırır."""
        if not isinstance(command_list, (list, tuple)):
            print(f"{R}HATA: Komut listesi geçersiz.{RESET}")
            return False # Başarısızlık belirt

        print(f"{C}--- Komutlar Çalıştırılıyor ---{RESET}")
        success = True
        effective_cwd = target_dir or self.INSTALLATION_DIR or None # Çalışma dizinini belirle

        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")

            try:
                # shell=True, 'cd ... && ...' gibi yapıları çalıştırabilir ama güvenlik riski taşır.
                # Mümkünse ayrı komutlar ve cwd kullanmak daha iyidir.
                # Basitlik adına shell=True kullanalım ama dikkatli olmalı.
                subprocess.run(command, shell=True, check=True, cwd=effective_cwd)
            except FileNotFoundError as e:
                 print(f"{R}HATA: Komut veya program bulunamadı: {e}{RESET}")
                 success = False
                 break # Hata durumunda dur
            except subprocess.CalledProcessError as e:
                print(f"{R}HATA: Komut hata ile sonlandı (Kod: {e.returncode}): {command}{RESET}")
                success = False
                break # Hata durumunda dur
            except Exception as e:
                 print(f"{R}Komut çalıştırılırken beklenmedik hata: {command}\nHata: {e}{RESET}")
                 success = False
                 break # Hata durumunda dur

        status = f"{G}Başarılı{RESET}" if success else f"{R}Başarısız{RESET}"
        print(f"{C}--- Komutlar Tamamlandı (Durum: {status}) ---{RESET}")
        return success

    def show_info(self):
        """Aracın bilgilerini gösterir."""
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        # Açıklamadaki \n\b gibi garip karakterleri temizle
        clean_desc = self.DESCRIPTION.replace('\n\b', '\n')
        print(clean_desc)
        if self.PROJECT_URL:
            print(f"\n{C}Proje Sayfası:{W} {self.PROJECT_URL}{RESET}")
        print("-" * (len(self.TITLE) + 6))

    def show_options(self, parent=None):
        """Aracın seçeneklerini gösterir ve seçimi işler."""
        clear_screen()
        self.show_info()
        print(f"\n{Y}Seçenekler:{RESET}")
        valid_indices = list(range(1, len(self.OPTIONS) + 1)) # Geçerli seçenek numaraları
        for index, option in enumerate(self.OPTIONS):
            print(f"  [{index + 1}] {option[0]}")

        # Ekstra seçenekler (varsa)
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
        # Komutları INSTALLATION_DIR içinde çalıştırmayı dene
        self._execute_commands(self.INSTALL_COMMANDS, target_dir=self.INSTALLATION_DIR)
        self.after_install()

    def after_install(self):
        print(f"\n{G}{self.TITLE} kurulumu tamamlandı (hatalar için yukarıyı kontrol edin).{RESET}")

    def before_uninstall(self) -> bool:
        confirm = input(f"{Y}UYARI: {self.TITLE} kaldırılacak. Emin misiniz? [e/H]: {W}").strip().lower()
        return confirm == 'e'

    def uninstall(self):
        if self.before_uninstall():
            print(f"\n{C}{self.TITLE} kaldırılıyor...{RESET}")
            self._execute_commands(self.UNINSTALL_COMMANDS) # Kaldırma dizini belirsiz, genelde global çalışır
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
             # Çalıştırma komutlarını INSTALLATION_DIR içinde çalıştırmayı dene
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
        super().__init__(installable=False, runnable=False) # Koleksiyonların kendisi kurulmaz/çalışmaz
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
        valid_indices = list(range(len(self.TOOLS))) # Geçerli indeksler (0'dan başlar)
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

# === Web Saldırı Araç Tanımlamaları ===

class Web2Attack(HackingTool):
    TITLE = "Web2Attack"
    DESCRIPTION = "Python ile yazılmış araçlar ve exploitler içeren web saldırı framework'ü."
    INSTALLATION_DIR = "web2attack"
    INSTALL_COMMANDS = [f"sudo git clone https://github.com/santatic/web2attack.git {INSTALLATION_DIR}"]
    # RUN_COMMANDS için cd gerekli, base class'ın run metodu bunu (INSTALLATION_DIR ile) deneyecek
    RUN_COMMANDS = ["sudo python3 w2aconsole"] # python3 sistemde olmalı
    PROJECT_URL = "https://github.com/santatic/web2attack"

class Skipfish(HackingTool):
    TITLE = "Skipfish"
    DESCRIPTION = (
        "Skipfish – Tam otomatik, aktif web uygulaması güvenlik keşif aracı.\n"
        "Kullanım: skipfish -o [KlasörAdı] hedef_ip/site"
    )
    # Kurulum komutu yok, sistemde kurulu olduğu varsayılıyor
    # RUN_COMMANDS yardım gösterir
    RUN_COMMANDS = [
        "sudo skipfish -h",
        # boxes/lolcat kaldırıldı, basit echo kullanalım
        'echo "\nKullanım Örneği: skipfish -o CIKTI_KLASORU http://hedefsite.com"'
    ]

    def __init__(self):
        # Kurulum seçeneği olmasın
        super().__init__(installable=False)

class SubDomainFinder(HackingTool):
    TITLE = "SubDomain Finder (Sublist3r)"
    DESCRIPTION = (
        "Sublist3r, OSINT kullanarak web sitelerinin alt alan adlarını (subdomain) listelemek için tasarlanmış bir Python aracıdır.\n"
        "Kullanım:\n\t"
        "[1] python3 sublist3r.py -d example.com\n\t"
        "[2] python3 sublist3r.py -d example.com -p 80,443"
    )
    INSTALLATION_DIR = "Sublist3r"
    INSTALL_COMMANDS = [
        # Genel bağımlılıklar
        f"sudo {sys.executable} -m pip install requests argparse dnspython",
        # Klonla
        f"sudo git clone https://github.com/aboul3la/Sublist3r.git {INSTALLATION_DIR}",
        # Araca özel bağımlılıklar (dizin içinde)
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install -r requirements.txt"
    ]
    # Run sadece help gösterir, asıl kullanım parametre gerektirir
    RUN_COMMANDS = ["python3 sublist3r.py -h"] # sudo gerekmeyebilir?
    PROJECT_URL = "https://github.com/aboul3la/Sublist3r"

    # run metodunu override edip kullanıcıdan domain almak daha kullanışlı olabilir
    def run(self):
        run_dir = self.INSTALLATION_DIR
        script_path = os.path.join(run_dir, "sublist3r.py")
        if not os.path.exists(run_dir) or not os.path.exists(script_path):
            print(f"{R}HATA: Sublist3r kurulu değil veya bulunamadı.{RESET}")
            return

        domain = input(f" Hedef Domain (örn: example.com) [{self.TITLE}] >> ")
        if not domain:
            print(f"{R}HATA: Domain boş olamaz.{RESET}")
            return
        ports = input(f" Taranacak Portlar (isteğe bağlı, örn: 80,443) [{self.TITLE}] >> ").strip()
        output_file = input(f" Çıktı Dosyası (isteğe bağlı, örn: subdomains.txt) [{self.TITLE}] >> ").strip()

        command = [sys.executable, script_path, "-d", domain]
        if ports: command.extend(["-p", ports])
        if output_file: command.extend(["-o", output_file])

        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            subprocess.run(command, cwd=run_dir, check=True)
        except Exception as e:
            print(f"{R}Sublist3r çalıştırılırken hata: {e}{RESET}")

class CheckURL(HackingTool):
    TITLE = "CheckURL (IDN Homograph)"
    DESCRIPTION = (
        "IDN Homograph Saldırısı kullanan kötü niyetli URL'leri tespit eder.\n\t"
        f"{Y}[Örnek Kullanım]{W} python3 checkURL.py --url google.com{RESET}"
    )
    INSTALLATION_DIR = "checkURL"
    INSTALL_COMMANDS = [f"sudo git clone https://github.com/UndeadSec/checkURL.git {INSTALLATION_DIR}"]
    # RUN_COMMANDS help gösterir, run override edilebilir
    RUN_COMMANDS = ["python3 checkURL.py --help"]
    PROJECT_URL = "https://github.com/UndeadSec/checkURL"

    def run(self):
        run_dir = self.INSTALLATION_DIR
        script_path = os.path.join(run_dir, "checkURL.py")
        if not os.path.exists(run_dir) or not os.path.exists(script_path):
            print(f"{R}HATA: checkURL kurulu değil veya bulunamadı.{RESET}")
            return

        url_to_check = input(f" Kontrol edilecek URL [{self.TITLE}] >> ").strip()
        if not url_to_check:
            print(f"{R}HATA: URL boş olamaz.{RESET}")
            return

        command = [sys.executable, script_path, "--url", url_to_check]
        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            subprocess.run(command, cwd=run_dir, check=True)
        except Exception as e:
            print(f"{R}checkURL çalıştırılırken hata: {e}{RESET}")


class Blazy(HackingTool):
    TITLE = "Blazy (Login Bruteforcer)"
    DESCRIPTION = f"Modern bir giriş sayfası kaba kuvvet saldırı aracı.\n{R}{BRIGHT}UYARI: Python 2.7 gerektirir!{RESET}"
    INSTALLATION_DIR = "Blazy"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/UltimateHackers/Blazy.git {INSTALLATION_DIR}",
        # Python 2.7 pip'ini bulmak zor olabilir, 'pip2' veya 'pip2.7' deneyebiliriz
        f"cd {INSTALLATION_DIR} && sudo pip2 install -r requirements.txt || sudo pip2.7 install -r requirements.txt"
    ]
    # Çalıştırma için python2.7 gerekli
    RUN_COMMANDS = ["python2.7 blazy.py"] # Varsayılan olarak yardım menüsünü gösterir
    PROJECT_URL = "https://github.com/UltimateHackers/Blazy"

    # run override edilebilir ama varsayılanı help gösteriyor, o da yeterli olabilir.
    # Kullanıcıdan input almak istenirse run override edilmeli.


class SubDomainTakeOver(HackingTool):
    TITLE = "Sub-Domain TakeOver Check"
    DESCRIPTION = (
        "Bir alt alan adının (subdomain.example.com) kaldırılmış veya silinmiş \n"
        "bir harici servise (örn: GitHub Pages, S3) işaret etmesi durumunda \n"
        "ortaya çıkan zafiyeti kontrol eder.\n"
        f"{Y}Kullanım:{W} python3 takeover.py -d www.domain.com -v{RESET}"
    )
    INSTALLATION_DIR = "takeover"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/edoardottt/takeover.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} setup.py install"
    ]
    PROJECT_URL = "https://github.com/edoardottt/takeover"

    def __init__(self):
        # Kurulum sonrası manuel çalıştırma gerektirebilir
        super().__init__(runnable = False)


class Dirb(HackingTool):
    TITLE = "Dirb (Web Content Scanner)"
    DESCRIPTION = (
        "DIRB bir Web İçerik Tarayıcısıdır. Mevcut (ve/veya gizli) Web Nesnelerini arar.\n"
        "Bir web sunucusuna karşı sözlük tabanlı bir saldırı başlatarak çalışır."
    )
    INSTALLATION_DIR = "dirb_tool" # dirb sistem komutuyla karışmasın
    # Kurulum derleme gerektirir (build-essential, make, gcc vb. gerekir)
    INSTALL_COMMANDS = [
        "sudo apt-get update && sudo apt-get install -y build-essential", # Örnek bağımlılık Debian/Ubuntu için
        f"sudo git clone https://gitlab.com/kalilinux/packages/dirb.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo bash configure && sudo make && sudo make install" # make install varsa
        # Alternatif: Derlenen dosyayı PATH'e eklemek veya tam yoldan çalıştırmak
    ]
    PROJECT_URL = "https://gitlab.com/kalilinux/packages/dirb"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        # dirb komutunun PATH'de olduğunu varsayalım (make install sonrası)
        if not self._is_tool_installed("dirb"):
             print(f"{R}HATA: 'dirb' komutu bulunamadı. Kurulum başarılı oldu mu veya PATH'de mi?{RESET}")
             return

        target_url = input(f" Hedef URL (örn: http://example.com) [{self.TITLE}] >> ")
        if not target_url:
             print(f"{R}HATA: URL boş olamaz.{RESET}")
             return
        wordlist = input(f" Sözlük Dosyası (Boş bırakırsanız varsayılan kullanılır) [{self.TITLE}] >> ").strip()

        command = ["sudo", "dirb", target_url]
        if wordlist:
            command.append(wordlist) # Varsayılan sözlük yerine belirtileni kullan

        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: 'dirb' veya 'sudo' komutu bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: Dirb çalıştırılırken hata oluştu (Kod: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
             print(f"{R}Beklenmedik bir hata oluştu: {e}{RESET}")

    def _is_tool_installed(self, tool_name):
        """Basitçe komutun PATH içinde olup olmadığını kontrol eder."""
        import shutil
        return shutil.which(tool_name) is not None


class WebAttackTools(HackingToolsCollection):
    TITLE = "Web Saldırı Araçları"
    DESCRIPTION = "Web uygulamaları için çeşitli saldırı, tarama ve bilgi toplama araçları."
    TOOLS = [
        Web2Attack(),
        Skipfish(),
        SubDomainFinder(),
        CheckURL(),
        Blazy(),
        SubDomainTakeOver(),
        Dirb()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    # Ana koleksiyonu oluştur
    main_collection = WebAttackTools()

    # Menüyü başlat
    try:
         main_collection.show_options() # parent=None (varsayılan)
    except KeyboardInterrupt:
         print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception:
         print(f"\n{R}Kritik bir hata oluştu!{RESET}")
         print_exc()
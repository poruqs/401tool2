# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
import contextlib # Faceshell'deki suppress için (gerçi değiştireceğiz)
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
        if runnable or self.RUN_COMMANDS: # Eğer run() override edilirse veya RUN_COMMANDS varsa Run ekle
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
        # Belirtilen dizin yoksa mevcut dizini kullan
        effective_cwd = target_dir if (target_dir and os.path.isdir(target_dir)) else None

        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")

            try:
                # shell=True, 'cd ... && ...' gibi yapıları çalıştırır ama güvenlik riski!
                # Komutları dikkatlice kontrol etmek önemlidir.
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
        # INSTALL_COMMANDS içinde 'cd' varsa _execute_commands shell=True ile dener
        # Kurulum dizini belirtilmişse hedef dizin olarak onu kullanırız
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
             # RUN_COMMANDS içindeki komutları INSTALLATION_DIR içinde çalıştırmayı dene
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

# === Sosyal Medya ve Uygulama Araç Tanımlamaları ===

class InstaBrute(HackingTool):
    TITLE = "Instagram Attack (InstaBrute)"
    DESCRIPTION = f"Instagram'a yönelik kaba kuvvet saldırısı.\n{R}{BRIGHT}UYARI: Python 2.7 gerektirir! İzin almadan kullanmak yasa dışıdır!{RESET}"
    INSTALLATION_DIR = "instaBrute"
    # Kurulum komutları: Önce klonla, sonra pip2 ile kur.
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/chinoogawa/instaBrute.git {INSTALLATION_DIR}",
        # pip2 veya pip2.7'yi dener
        f"cd {INSTALLATION_DIR} && (sudo pip2 install -r requirements.txt || sudo pip2.7 install -r requirements.txt)"
    ]
    PROJECT_URL = "https://github.com/chinoogawa/instaBrute"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        run_dir = self.INSTALLATION_DIR
        # Betik adı 'instaBrute.py' mi yoksa farklı mı? Kontrol etmek lazım.
        script_name = "instaBrute.py"
        script_path = os.path.join(run_dir, script_name)

        if not os.path.exists(run_dir) or not os.path.exists(script_path):
            print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
            print("Lütfen önce aracı kurun ('Install').")
            return

        name = input(f" Hedef Kullanıcı Adı [{self.TITLE}] >> ")
        wordlist = input(f" Wordlist Dosya Yolu [{self.TITLE}] >> ")
        if not name or not wordlist:
            print(f"{R}HATA: Kullanıcı adı ve wordlist boş olamaz.{RESET}")
            return

        # Python 2.7'yi çalıştırmak için 'python' mı 'python2' mi 'python2.7' mi?
        # Sisteme göre değişir, 'python2.7' veya 'python2' denemek daha güvenli.
        python_executable = "python2.7" # veya "python2"
        command = ["sudo", python_executable, script_path, "-u", name, "-d", wordlist]

        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        print(f"{C}InstaBrute çalışıyor... (Durdurmak için Ctrl+C){RESET}")
        try:
            # Çalışma dizini önemli
            subprocess.run(command, cwd=run_dir, check=True)
        except FileNotFoundError:
            print(f"{R}HATA: '{python_executable}', 'sudo' veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Python 2.7 sisteminizde kurulu ve PATH içinde mi?{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{R}HATA: InstaBrute hatası (Kod: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
            print(f"{R}Beklenmedik hata: {e}{RESET}")


class BruteForce(HackingTool):
    TITLE = "All-in-One Social Bruteforce"
    DESCRIPTION = (
        "Gmail, Hotmail, Twitter, Facebook, Netflix için Kaba Kuvvet Saldırı Aracı.\n"
        f"{Y}[Örnek Kullanım]{W} python3 Brute_Force.py -g <Account@gmail.com> -l <File_list>{RESET}\n"
        f"{R}{BRIGHT}UYARI: İzin almadan kullanmak yasa dışıdır!{RESET}"
    )
    INSTALLATION_DIR = "Brute_Force"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/Matrix07ksa/Brute_Force.git {INSTALLATION_DIR}",
        # Bağımlılıklar: pip3 ile
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install proxylist mechanize"
    ]
    # Run sadece help gösterir
    RUN_COMMANDS = ["python3 Brute_Force.py -h"]
    PROJECT_URL = "https://github.com/Matrix07ksa/Brute_Force"

    # İsteğe bağlı olarak run metodu override edilip kullanıcıdan input alınabilir
    # def run(self):
    #     service = input("Servis (g, h, f, t, n): ")
    #     email = input("Email/Username: ")
    #     wordlist = input("Wordlist: ")
    #     # ... komutu oluştur ve çalıştır ...


class Faceshell(HackingTool):
    TITLE = "Facebook Attack (Faceshell)"
    DESCRIPTION = f"Facebook Kaba Kuvvet Saldırısı (Brute_Force aracını kullanır).\n{R}{BRIGHT}UYARI: İzin almadan kullanmak yasa dışıdır!{RESET}"
    # Aynı repoyu ve kurulumu kullanır
    INSTALLATION_DIR = "Brute_Force" # BruteForce ile aynı dizin
    INSTALL_COMMANDS = [
        # Eğer BruteForce zaten kurulduysa tekrar klonlamaya gerek yok.
        # Bu durumu kontrol etmek framework'e eklenebilir veya burada basit bir kontrol yapılabilir.
        f"if [ ! -d '{INSTALLATION_DIR}' ]; then sudo git clone https://github.com/Matrix07ksa/Brute_Force.git {INSTALLATION_DIR}; fi",
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install proxylist mechanize"
    ]
    PROJECT_URL = "https://github.com/Matrix07ksa/Brute_Force"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        run_dir = self.INSTALLATION_DIR
        script_name = "Brute_Force.py"
        script_path = os.path.join(run_dir, script_name)

        if not os.path.exists(run_dir) or not os.path.exists(script_path):
            print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Önce 'All-in-One Social Bruteforce' aracını kurmayı deneyin.{RESET}")
            return

        name = input(f" Facebook Kullanıcı Adı/ID/Email [{self.TITLE}] >> ")
        wordlist = input(f" Wordlist Dosya Yolu [{self.TITLE}] >> ")
        if not name or not wordlist:
            print(f"{R}HATA: Girdiler boş olamaz.{RESET}")
            return

        # -f parametresi Facebook için kullanılır
        command = [sys.executable, script_path, "-f", name, "-l", wordlist]
        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            subprocess.run(command, cwd=run_dir, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: '{command[0]}' veya '{command[1]}' bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: Faceshell (Brute_Force) hatası (Kod: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")


class AppCheck(HackingTool):
    TITLE = "Application Checker (Underhanded)"
    DESCRIPTION = "Bir bağlantı aracılığıyla hedef cihazda bir uygulamanın kurulu olup olmadığını kontrol eder."
    INSTALLATION_DIR = "underhanded"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/jakuta-tech/underhanded.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo chmod +x underhanded.sh"
    ]
    RUN_COMMANDS = ["sudo bash underhanded.sh"] # Çalıştırmak için temel run metodunu kullanır
    PROJECT_URL = "https://github.com/jakuta-tech/underhanded"


class SocialMediaBruteforceTools(HackingToolsCollection):
    TITLE = "Sosyal Medya Kaba Kuvvet Araçları"
    DESCRIPTION = f"Sosyal medya hesaplarına yönelik saldırı ve test araçları.\n{R}{BRIGHT}UYARI: Bu araçların izinsiz kullanımı yasa dışıdır!{RESET}"
    TOOLS = [
        InstaBrute(),
        BruteForce(),
        Faceshell(),
        AppCheck()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    main_collection = SocialMediaBruteforceTools()
    try:
         main_collection.show_options()
    except KeyboardInterrupt:
         print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception:
         print(f"\n{R}Kritik bir hata oluştu!{RESET}")
         print_exc()
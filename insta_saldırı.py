# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
# contextlib kaldırıldı, Faceshell'deki suppress yerine doğrudan hata mesajı gösterilecek
# import contextlib
from platform import system
from traceback import print_exc
from typing import Callable, List, Tuple, Any

# --- UYARI ---
# Bu betik, sosyal medya hesaplarına yönelik kaba kuvvet (bruteforce) ve
# diğer potansiyel olarak zararlı araçları yönetmek için bir arayüzdür.
# Bu araçların İZİNSİZ hesaplara karşı kullanılması YASA DIŞIDIR ve ETİK DEĞİLDİR.
# Sadece izinli testler ve eğitim amaçlı kullanın. Sorumluluk kullanıcıya aittir.
# InstaBrute aracı Python 2.7 gerektirir ve artık DESTEKLENMEMEKTEDİR, çalışmayacaktır.
# Diğer araçların API bağımlılıkları veya GitHub repoları zamanla kullanılamaz hale gelebilir.
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
    os.system("cls" if system() == "Windows" else "clear")

def pause():
    """Devam etmek için Enter beklenir."""
    try:
        input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit()

# --- Yardımcı Fonksiyon: Aracın kurulu olup olmadığını kontrol et ---
# (web_saldırı.py'den kopyalandı)
def is_tool_installed(tool_name):
    """Basitçe komutun sistem PATH'inde olup olmadığını kontrol eder."""
    import shutil
    return shutil.which(tool_name) is not None

# === Temel Sınıflar (Framework Yapısı) ===
# (Bu sınıflar web_saldırı.py'deki ile aynıdır, tekrar eklenmiştir)

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
        # Çalışma dizinini belirle
        effective_cwd = target_dir or self.INSTALLATION_DIR or None
        if effective_cwd and not os.path.isdir(effective_cwd):
             print(f"{Y}Uyarı: Hedef dizin '{effective_cwd}' mevcut değil. Komutlar mevcut dizinde çalıştırılacak.{RESET}")
             effective_cwd = None

        for command in command_list:
            # Güvenlik Notu: sudo içeren komutlara dikkat!
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")

            try:
                # shell=True riskli olsa da 'cd ... && ...' için gerekli olabilir.
                subprocess.run(command, shell=True, check=True, cwd=effective_cwd)
            except FileNotFoundError as e:
                 print(f"{R}HATA: Komut veya program bulunamadı: {e}{RESET}")
                 print(f"{Y}Komut: '{command}'{RESET}")
                 print(f"{Y}Gerekli programın (örn: git, pip, python2.7, bash) kurulu ve PATH'de olduğundan emin olun.{RESET}")
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
        print("-" * (len(strip_colors(self.TITLE)) + 6)) # Başlıktaki renk kodlarını hesaba katma

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
        except KeyboardInterrupt:
             print("\nİşlem iptal edildi.")
             return None # Ana menüye dön
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
        success = self._execute_commands(self.INSTALL_COMMANDS, target_dir=None)
        self.after_install(success)
        return success

    def after_install(self, success):
        if success:
            print(f"\n{G}{self.TITLE} kurulumu başarıyla tamamlandı (veya hatalarla bitti, yukarıyı kontrol edin).{RESET}")
        else:
            print(f"\n{R}{self.TITLE} kurulumu başarısız oldu.{RESET}")

    def before_uninstall(self) -> bool:
        confirm = input(f"{Y}UYARI: {self.TITLE} kaldırılacak. Emin misiniz? [e/H]: {W}").strip().lower()
        return confirm == 'e'

    def uninstall(self):
        if self.before_uninstall():
            print(f"\n{C}{self.TITLE} kaldırılıyor...{RESET}")
            success = self._execute_commands(self.UNINSTALL_COMMANDS, target_dir=None)
            self.after_uninstall(success)
            return success
        else:
             print("Kaldırma işlemi iptal edildi.")
             return False

    def after_uninstall(self, success):
         if success:
             print(f"\n{G}{self.TITLE} kaldırıldı (veya hatalarla bitti).{RESET}")
         else:
             print(f"\n{R}{self.TITLE} kaldırma işlemi başarısız oldu.{RESET}")

    def before_run(self):
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")

    def run(self):
        """Varsayılan çalıştırma metodu. RUN_COMMANDS listesini çalıştırır."""
        self.before_run()
        success = False
        if not self.RUN_COMMANDS:
            print(f"{Y}Bu araç için özel bir 'run' metodu veya RUN_COMMANDS tanımlanmamış.{RESET}")
        else:
             # RUN_COMMANDS içindeki komutları INSTALLATION_DIR içinde çalıştırmayı dene
             success = self._execute_commands(self.RUN_COMMANDS, target_dir=self.INSTALLATION_DIR)
        self.after_run(success)
        return success

    def after_run(self, success):
        pass # Genellikle bir şey yapmaya gerek yok

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
        print("=" * (len(strip_colors(self.TITLE)) + 6))

    def show_options(self, parent = None):
        """Koleksiyon içindeki araçları listeler."""
        clear_screen()
        self.show_info()
        print(f"\n{Y}Araçlar:{RESET}")
        valid_indices = list(range(len(self.TOOLS))) # 0'dan başlayan indeksler
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
        except KeyboardInterrupt:
             print("\nİşlem iptal edildi.")
             return None # Ana menüye dön
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
    TITLE = f"Instagram Bruteforce (InstaBrute) {R}{BRIGHT}(PYTHON 2.7 GEREKLİ - ÇALIŞMAZ!){RESET}"
    DESCRIPTION = (f"Instagram hesabına yönelik kaba kuvvet saldırısı.\n"
                   f"{R}{BRIGHT}!!! UYARI: Bu araç Python 2.7 gerektirir ve Python 2 artık DESTEKLENMEMEKTEDİR!{RESET}\n"
                   f"{R}{BRIGHT}Modern sistemlerde büyük ihtimalle ÇALIŞMAYACAKTIR.{RESET}\n"
                   f"{R}İzin almadan kullanmak yasa dışıdır!{RESET}")
    INSTALLATION_DIR = "instaBrute"
    # Kurulum komutları Python 2 ve pip2 gerektirir, başarısız olması çok muhtemel
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/chinoogawa/instaBrute.git {INSTALLATION_DIR}",
        # pip2 veya pip2.7'yi dener, bulamazsa hata mesajı verir
        f"cd {INSTALLATION_DIR} && (sudo pip2 install -r requirements.txt || sudo pip2.7 install -r requirements.txt || echo '{R}HATA: Python 2 pip (pip2/pip2.7) bulunamadı veya requirements.txt kurulamadı!{RESET}')"
    ]
    PROJECT_URL = "https://github.com/chinoogawa/instaBrute"
    RUN_COMMANDS = [] # run override edildi

    def install(self):
        # Kurulum öncesi Python 2 kontrolü yapalım
        print(f"\n{C}{self.TITLE} kurulumu deneniyor...{RESET}")
        py2_executable = None
        for cmd in ["python2.7", "python2"]:
            if is_tool_installed(cmd):
                py2_executable = cmd
                break
        if not py2_executable:
            print(f"{R}HATA: Python 2.7 veya Python 2 sisteminizde bulunamadı.{RESET}")
            print(f"{Y}InstaBrute aracı çalışmak için Python 2 gerektirir.{RESET}")
            return False # Kurulum başarısız

        pip2_executable = None
        for cmd in ["pip2.7", "pip2"]:
             if is_tool_installed(cmd):
                  pip2_executable = cmd
                  break
        if not pip2_executable:
             print(f"{Y}UYARI: Python 2 pip ('pip2' veya 'pip2.7') bulunamadı. Bağımlılıklar kurulamayacak.{RESET}")
             # Komutları buna göre ayarla
             self.INSTALL_COMMANDS = [
                 f"sudo git clone https://github.com/chinoogawa/instaBrute.git {self.INSTALLATION_DIR}",
                 f"echo '{Y}Python 2 pip bulunamadığı için bağımlılıklar atlandı.'",
             ]
        else:
             # pip2 bulunduysa orijinal komutları kullan
             self.INSTALL_COMMANDS = [
                 f"sudo git clone https://github.com/chinoogawa/instaBrute.git {self.INSTALLATION_DIR}",
                 f"cd {self.INSTALLATION_DIR} && sudo {pip2_executable} install -r requirements.txt"
             ]
        # Komutları çalıştır
        success = self._execute_commands(self.INSTALL_COMMANDS, target_dir=None)
        self.after_install(success)
        return success

    def run(self):
        # Çalıştırmadan önce Python 2'yi tekrar kontrol et
        print(f"\n{C}{self.TITLE} çalıştırılmaya çalışılıyor...{RESET}")
        py2_executable = None
        for cmd in ["python2.7", "python2"]:
            if is_tool_installed(cmd):
                py2_executable = cmd
                break
        if not py2_executable:
             print(f"{R}HATA: Python 2 bulunamadığı için InstaBrute çalıştırılamıyor.{RESET}")
             return False

        # Gerekli bilgileri al
        run_dir = self.INSTALLATION_DIR
        script_name = "instaBrute.py" # Repo'daki betik adı varsayımı
        script_path = os.path.join(run_dir, script_name)

        if not os.path.isdir(run_dir) or not os.path.isfile(script_path):
            print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Lütfen önce aracı kurun ('Install' seçeneği).{RESET}")
            return False

        try:
            name = input(f" Hedef Instagram Kullanıcı Adı [{self.TITLE}] >> ")
            wordlist = input(f" Wordlist Dosya Yolu [{self.TITLE}] >> ")
            if not name or not wordlist:
                print(f"{R}HATA: Kullanıcı adı ve wordlist boş olamaz.{RESET}")
                return False
            if not os.path.isfile(wordlist):
                 print(f"{R}HATA: Belirtilen wordlist dosyası bulunamadı: {wordlist}{RESET}")
                 return False

            # Komutu oluştur (sudo gerekli mi? Deneyelim)
            command = ["sudo", py2_executable, script_path, "-u", name, "-d", wordlist]

            print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
            print(f"{C}InstaBrute çalışıyor... (Durdurmak için Ctrl+C){RESET}")
            # Çalışma dizini önemli
            subprocess.run(command, cwd=run_dir, check=True)
            return True
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
            return False
        except FileNotFoundError:
            # python2, sudo veya script_path bulunamazsa
            print(f"{R}HATA: '{command[0]}', '{command[1]}' veya '{command[2]}' bulunamadı.{RESET}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"{R}HATA: InstaBrute hatası (Kod: {e.returncode}). Instagram API değişmiş veya hesap/IP engellenmiş olabilir.{RESET}")
            return False
        except Exception as e:
            print(f"{R}InstaBrute çalıştırılırken beklenmedik hata: {e}{RESET}")
            return False


class BruteForce(HackingTool):
    TITLE = "All-in-One Social Bruteforce (Matrix07ksa)"
    DESCRIPTION = (
        "Gmail, Hotmail, Twitter, Facebook, Netflix için Kaba Kuvvet Saldırı Aracı.\n"
        f"{Y}[Örnek Kullanım]{W} python3 Brute_Force.py -g <Account@gmail.com> -l <Wordlist.txt>{RESET}\n"
        f"{R}{BRIGHT}UYARI: İzin almadan kullanmak yasa dışıdır! Servislerin API'leri değişmiş olabilir.{RESET}"
    )
    INSTALLATION_DIR = "Brute_Force"
    INSTALL_COMMANDS = [
        # Dizinin var olup olmadığını kontrol et, yoksa klonla
        f"if [ ! -d '{INSTALLATION_DIR}' ]; then sudo git clone https://github.com/Matrix07ksa/Brute_Force.git {INSTALLATION_DIR}; else echo '{Y}Dizin zaten var, klonlama atlandı.{RESET}'; fi",
        # Bağımlılıklar: pip3 ile (sudo gerekebilir)
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install proxylist mechanize requests" # requests'i de ekleyelim
    ]
    # Run sadece help gösterir, kullanıcı manuel çalıştırır
    RUN_COMMANDS = [f"{sys.executable} Brute_Force.py -h"]
    PROJECT_URL = "https://github.com/Matrix07ksa/Brute_Force"

    # İsteğe bağlı: run metodunu override edip kullanıcıdan input aldırılabilir
    # def run(self):
    #     service_map = {'g': 'Gmail', 'h': 'Hotmail', 'f': 'Facebook', 't': 'Twitter', 'n': 'Netflix'}
    #     service = input(f"Servis Seçin ({', '.join(service_map.keys())}): ").lower().strip()
    #     if service not in service_map:
    #         print(f"{R}Geçersiz servis.{RESET}")
    #         return False
    #     # ... email/username ve wordlist iste ...
    #     # ... komutu oluştur ve çalıştır ...


class Faceshell(HackingTool):
    TITLE = "Facebook Bruteforce (Faceshell / Matrix07ksa)"
    DESCRIPTION = (f"Facebook Kaba Kuvvet Saldırısı (Brute_Force aracını kullanır).\n"
                   f"{R}{BRIGHT}UYARI: İzin almadan kullanmak yasa dışıdır! Facebook API'leri değişmiş olabilir.{RESET}")
    # Aynı repoyu ve kurulumu kullanır
    INSTALLATION_DIR = "Brute_Force" # BruteForce ile aynı dizin
    INSTALL_COMMANDS = BruteForce.INSTALL_COMMANDS # Aynı kurulum komutları
    PROJECT_URL = BruteForce.PROJECT_URL # Aynı proje URL'si
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        """Kullanıcıdan girdi alarak Brute_Force.py'yi Facebook modu (-f) ile çalıştırır."""
        run_dir = self.INSTALLATION_DIR
        script_name = "Brute_Force.py"
        script_path = os.path.join(run_dir, script_name)

        if not os.path.isdir(run_dir) or not os.path.isfile(script_path):
            print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Lütfen önce 'All-in-One Social Bruteforce' aracını kurun ('Install' seçeneği).{RESET}")
            return False

        try:
            name = input(f" Facebook Kullanıcı Adı/ID/Email [{self.TITLE}] >> ")
            wordlist = input(f" Wordlist Dosya Yolu [{self.TITLE}] >> ")
            if not name or not wordlist:
                print(f"{R}HATA: Girdiler boş olamaz.{RESET}")
                return False
            if not os.path.isfile(wordlist):
                 print(f"{R}HATA: Belirtilen wordlist dosyası bulunamadı: {wordlist}{RESET}")
                 return False

            # Komutu oluştur: python3 Brute_Force.py -f <name> -l <wordlist>
            command = [sys.executable, script_path, "-f", name, "-l", wordlist]
            print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
            subprocess.run(command, cwd=run_dir, check=True)
            return True
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
            return False
        except FileNotFoundError:
             print(f"{R}HATA: Python yorumlayıcısı veya '{script_path}' bulunamadı.{RESET}")
             return False
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: Faceshell (Brute_Force) hatası (Kod: {e.returncode}). API değişmiş veya hesap/IP engellenmiş olabilir.{RESET}")
             return False
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")
             return False


class AppCheck(HackingTool):
    TITLE = "Application Checker (Underhanded)"
    DESCRIPTION = (f"Bir bağlantı aracılığıyla hedef cihazda bir uygulamanın kurulu olup olmadığını kontrol eder.\n"
                   f"{Y}UYARI: Bu yöntem sosyal mühendislik içerir ve aldatıcı olabilir. Etik kullanın!{RESET}")
    INSTALLATION_DIR = "underhanded"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/jakuta-tech/underhanded.git {INSTALLATION_DIR}",
        # Çalıştırma izni ver
        f"cd {INSTALLATION_DIR} && sudo chmod +x underhanded.sh"
    ]
    # run metodu override edilmediği için RUN_COMMANDS kullanılır
    RUN_COMMANDS = ["sudo bash underhanded.sh"] # Bu betik interaktif olmalı
    PROJECT_URL = "https://github.com/jakuta-tech/underhanded"

    def install(self):
        # Kurulum öncesi bash kontrolü
        if not is_tool_installed("bash"):
            print(f"{R}HATA: 'bash' komutu bulunamadı. Bu araç bir bash betiği gerektirir.{RESET}")
            return False
        # Normal kurulumu yap
        return super().install()

    def run(self):
         # Çalıştırma öncesi bash kontrolü
        if not is_tool_installed("bash"):
             print(f"{R}HATA: 'bash' komutu bulunamadığı için araç çalıştırılamıyor.{RESET}")
             return False
        # Normal çalıştırmayı yap (RUN_COMMANDS kullanılır)
        return super().run()


# === Ana Koleksiyon Tanımı ===

class SocialMediaAttackTools(HackingToolsCollection):
    TITLE = "Sosyal Medya Saldırı Araçları"
    DESCRIPTION = (f"Sosyal medya hesaplarına yönelik kaba kuvvet ve diğer test araçları.\n"
                   f"{R}{BRIGHT}UYARI: Bu araçların izinsiz kullanımı yasa dışıdır ve etik değildir!{RESET}")
    TOOLS = [
        InstaBrute(),
        Faceshell(), # Facebook için özel
        BruteForce(), # Diğer servisler için genel
        AppCheck()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    # Gerekli temel kütüphaneleri kontrol et (webbrowser)
    try:
        import webbrowser
        import shutil # is_tool_installed için
    except ImportError as e:
        missing_module = str(e).split("'")[-2]
        print(f"{R}HATA: Gerekli '{missing_module}' kütüphanesi bulunamadı.{RESET}")
        sys.exit(1)

    # Ana koleksiyonu oluştur
    main_collection = SocialMediaAttackTools()
    try:
         main_collection.show_options()
    except KeyboardInterrupt:
         print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception:
         print(f"\n{R}Kritik bir hata oluştu!{RESET}")
         print_exc()
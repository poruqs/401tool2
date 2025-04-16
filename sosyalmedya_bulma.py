# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
import shutil # is_tool_installed için
from platform import system
from traceback import print_exc
from typing import Callable, List, Tuple, Any

# --- UYARI ---
# Bu betik, OSINT (Açık Kaynak İstihbaratı) araçlarını yönetir.
# Bu araçlarla elde edilen bilgilerin gizliliğe saygılı ve yasalara uygun şekilde kullanılması gerekir.
# Başkalarının kişisel bilgilerini izinsiz toplamak veya kötüye kullanmak YASA DIŞIDIR ve ETİK DEĞİLDİR.
# FacialFind (Social Mapper) aracının kurulumu çok karmaşıktır ve manuel adımlar gerektirir.
# Araçların bulduğu sonuçların doğruluğu garanti edilmez ve API'ler/web siteleri değiştikçe çalışmayabilirler.
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
def is_tool_installed(tool_name):
    """Basitçe komutun sistem PATH'inde olup olmadığını kontrol eder."""
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
        effective_cwd = target_dir or self.INSTALLATION_DIR or None
        if effective_cwd and not os.path.isdir(effective_cwd):
             # Hedef dizin yoksa uyarı ver ama komutları mevcut dizinde çalıştırmayı dene
             print(f"{Y}Uyarı: Hedef dizin '{effective_cwd}' mevcut değil. Komutlar mevcut dizinde çalıştırılacak.{RESET}")
             effective_cwd = None

        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")

            try:
                # shell=True riskli ama 'cd ... && ...' için gerekli olabilir.
                subprocess.run(command, shell=True, check=True, cwd=effective_cwd)
            except FileNotFoundError as e:
                 print(f"{R}HATA: Komut veya program bulunamadı: {e}{RESET}")
                 print(f"{Y}Komut: '{command}'{RESET}")
                 print(f"{Y}Gerekli programın (örn: git, pip, bash, gcc) kurulu ve PATH'de olduğundan emin olun.{RESET}")
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
        # Styling komutlarını ve garip karakterleri temizle
        clean_desc = self.DESCRIPTION.replace('\n\b', '\n').replace(' | boxes | lolcat', '')
        print(clean_desc)
        if self.PROJECT_URL:
            print(f"\n{C}Proje Sayfası:{W} {self.PROJECT_URL}{RESET}")
        print("-" * (len(strip_colors(self.TITLE)) + 6))

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
            success = self._execute_commands(self.UNINSTALL_COMMANDS)
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

# === Sosyal Medya Bulucu Araç Tanımlamaları ===

class FacialFind(HackingTool):
    TITLE = f"Sosyal Medya Bulucu (Yüz Tanıma - Social Mapper) {R}{BRIGHT}(KURULUMU ÇOK ZOR!){RESET}"
    DESCRIPTION = (
        "Farklı sitelerdeki profilleri yüz tanıma yoluyla ilişkilendirmeye çalışan\n"
        "bir Sosyal Medya Haritalama Aracı (Social Mapper).\n\n"
        f"{R}{BRIGHT}UYARI: Kurulumu çok adımlıdır, işletim sistemine özgüdür (Linux/Debian tabanlı), \n"
        f"manuel Geckodriver kurulumu ve betik içinde hesap ayarları gerektirir!{RESET}\n"
        f"{Y}Başarılı kurulum garanti edilmez.{RESET}"
    )
    INSTALLATION_DIR = "social_mapper"
    # Kurulum komutları OS bağımlı (apt) ve karmaşık, sadece bilgilendirme amaçlıdır.
    # Bu komutların doğrudan çalışması pek olası değildir.
    INSTALL_COMMANDS = [
        # Debian/Ubuntu için bağımlılıklar ve PPA ekleme (sudo gerektirir)
        "echo '--- Sistem paketleri güncelleniyor ve bağımlılıklar kuruluyor (sudo apt gerektirir) ---'",
        "echo '--- Örnek Bağımlılıklar (Debian/Ubuntu): sudo apt update && sudo apt install -y software-properties-common build-essential cmake libgtk-3-dev libboost-all-dev firefox ---'",
        # Social Mapper'ı klonla
        f"echo '--- Social Mapper klonlanıyor ({INSTALLATION_DIR}) ---'",
        f"sudo git clone https://github.com/Greenwolf/social_mapper.git {INSTALLATION_DIR}",
        # Python bağımlılıklarını kur (dizin içinde) - setup.py de olabilir, requirements.txt de
        f"echo '--- Python bağımlılıkları kuruluyor (sudo ve pip gerektirir) ---'",
        f"echo '--- Örnek: cd {os.path.join(INSTALLATION_DIR, 'setup')} && sudo {sys.executable} -m pip install --no-cache-dir -r requirements.txt ---'",
        # Manuel Adımlar İçin Uyarı
        (
            f"echo '\n{R}{BRIGHT}--- !!! ÖNEMLİ MANUEL KURULUM ADIMLARI GEREKLİ !!! ---{RESET}\n"
            f"{Y}[1] İşletim sisteminize uygun Firefox ve Geckodriver sürümünü kurun.{RESET}\n"
            f"{Y}    İndirme Linki: https://github.com/mozilla/geckodriver/releases{RESET}\n"
            f"{Y}    Linux'ta indirip /usr/local/bin gibi PATH içindeki bir yere taşıyın ('sudo mv geckodriver /usr/local/bin').{RESET}\n"
            f"{Y}[2] '{os.path.join(INSTALLATION_DIR, 'social_mapper.py')}' dosyasını açıp,\n"
            f"    kullanmak istediğiniz sosyal medya platformları için (örn: Facebook, Instagram)\n"
            f"    geçerli bir kullanıcı adı ve şifre (gerçek veya test hesabı) girmeniz GEREKİR!{RESET}\n"
            f"{Y}[3] Gerekli diğer sistem kütüphanelerini (cmake, boost, gtk) kurduğunuzdan emin olun.{RESET}'"
        )
    ]
    PROJECT_URL = "https://github.com/Greenwolf/social_mapper"
    # Run metodu sadece yardım ve talimatları gösterir
    RUN_COMMANDS = [] # run override edildi

    def install(self):
        # Kurulum komutları sadece bilgilendirme amaçlı, çalıştırmıyoruz.
        self.before_install()
        print(f"{Y}Social Mapper kurulumu oldukça karmaşıktır ve manuel adımlar gerektirir.{RESET}")
        print(f"{Y}Aşağıdaki adımlar genel bir yol haritasıdır (Debian/Ubuntu tabanlı sistemler için):{RESET}")
        # Bilgilendirme amaçlı komutları yazdır
        for cmd in self.INSTALL_COMMANDS:
             # echo komutlarını doğrudan çalıştırabiliriz
             if cmd.startswith("echo "):
                  os.system(cmd)
             else:
                  # Diğer komutları sadece gösterelim
                  print(f"{C}   {cmd}{RESET}")
        print(f"\n{R}Lütfen yukarıdaki MANUEL adımları dikkatlice uygulayın!{RESET}")
        self.after_install(False) # Başarısız gibi işaretleyelim çünkü manuel adım gerekli
        return False

    def run(self):
        """Social Mapper'ın nasıl çalıştırılacağına dair talimatları gösterir."""
        self.before_run()
        run_dir = self.INSTALLATION_DIR
        # Betik adı genellikle 'social_mapper.py' olur
        script_path = os.path.join(run_dir, "social_mapper.py")

        if not os.path.isdir(run_dir) or not os.path.isfile(script_path):
            print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Kurulumu yapın ('Install' seçeneği) ve manuel adımları tamamladığınızdan emin olun.{RESET}")
            return False

        # Yardım menüsünü göstermeyi deneyelim (sudo gerekebilir)
        print(f"\n{C}Social Mapper yardım menüsü gösteriliyor...{RESET}")
        command_help = ["sudo", sys.executable, script_path, "-h"]
        try:
             # cwd burada gerekmeyebilir çünkü script_path tam yol
             subprocess.run(command_help, check=True, timeout=10)
        except FileNotFoundError:
             print(f"{R}HATA: 'sudo', Python yorumlayıcısı veya '{script_path}' bulunamadı.{RESET}")
        except subprocess.TimeoutExpired:
             print(f"{Y}Yardım komutu zaman aşımına uğradı.{RESET}")
        except subprocess.CalledProcessError:
             print(f"{Y}Yardım komutu çalıştırılırken hata oluştu (muhtemelen bağımlılık eksik).{RESET}")
        except Exception as e:
             print(f"{R}Yardım menüsü gösterilirken beklenmedik hata: {e}{RESET}")

        # Ek talimatlar
        print(f"""\n{R}{BRIGHT}--- ÖNEMLİ ÇALIŞTIRMA NOTLARI ---{RESET}
{C}1. Çalıştırmadan önce '{script_path}' dosyasını açıp,
   ilgili sosyal medya platformları için kullanıcı adı ve şifreleri
   (Facebook, Instagram vb.) girmeniz ZORUNLUDUR!{RESET}
{C}2. Geckodriver'ın sistem PATH'inde olduğundan emin olun.{RESET}
{C}3. Gerekli tüm sistem kütüphanelerinin (cmake, boost, gtk) kurulu olduğundan emin olun.{RESET}
{Y}-----------------------------------{RESET}""")

        print(f"""\n{Y}{BRIGHT}--- Örnek Kullanım Komutları ---{RESET}
{G}# Sadece isim listesi ve resim klasörü ile çalıştırma (Facebook ve Twitter'da arama):{RESET}
{W}sudo python3 {script_path} -f names.txt -i image_folder -m fast -fb -tw{RESET}

{G}# Daha fazla detay için:{RESET}
{W}sudo python3 {script_path} --help{RESET}
{Y}-----------------------------{RESET}""")
        self.after_run(True) # Bilgi verdiği için başarılı sayalım
        return True


class FindUser(HackingTool):
    TITLE = "Kullanıcı Adı Bulucu (finduser - xHak9x)"
    DESCRIPTION = f"+75 sosyal ağda kullanıcı adlarını arar.\n{Y}(Bash betiği gerektirir){RESET}"
    INSTALLATION_DIR = "finduser"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/xHak9x/finduser.git {INSTALLATION_DIR}",
        # Çalıştırma izni ver
        f"cd {INSTALLATION_DIR} && sudo chmod +x finduser.sh"
    ]
    # run metodu override edilmediği için RUN_COMMANDS kullanılır
    # Bu betik interaktif olduğu için doğrudan çalıştırmak mantıklı
    RUN_COMMANDS = ["sudo bash finduser.sh"]
    PROJECT_URL = "https://github.com/xHak9x/finduser"

    def install(self):
        # Bash kontrolü
        if not is_tool_installed("bash"):
            print(f"{R}HATA: 'bash' komutu bulunamadı. Bu araç bir bash betiği gerektirir.{RESET}")
            return False
        return super().install()

    def run(self):
        # Bash kontrolü
        if not is_tool_installed("bash"):
             print(f"{R}HATA: 'bash' komutu bulunamadığı için araç çalıştırılamıyor.{RESET}")
             return False
        # Kurulum dizini kontrolü
        if not os.path.isdir(self.INSTALLATION_DIR) or not os.path.isfile(os.path.join(self.INSTALLATION_DIR, "finduser.sh")):
             print(f"{R}HATA: '{self.INSTALLATION_DIR}' veya içindeki 'finduser.sh' bulunamadı.{RESET}")
             print(f"{Y}Lütfen önce aracı kurun ('Install' seçeneği).{RESET}")
             return False
        # Normal çalıştırmayı yap (RUN_COMMANDS kullanılır)
        return super().run()


class Sherlock(HackingTool):
    TITLE = "Sherlock (Username Finder)"
    DESCRIPTION = (
        "Çok sayıda sosyal ağda kullanıcı adıyla hesap arar.\n"
        f"{Y}Daha fazla kullanım için:{W} python3 sherlock --help{RESET}"
    )
    INSTALLATION_DIR = "sherlock"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/sherlock-project/sherlock.git {INSTALLATION_DIR}",
        # Bağımlılıkları kur (sudo gerekebilir/gerekmeyebilir)
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install -r requirements.txt"
    ]
    PROJECT_URL = "https://github.com/sherlock-project/sherlock"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        """Kullanıcıdan kullanıcı adı alarak Sherlock'u çalıştırır."""
        run_dir = self.INSTALLATION_DIR
        # Sherlock kurulum sonrası genellikle doğrudan komut olarak çalışır hale gelir
        # Ama biz betiği doğrudan çalıştıralım (daha güvenilir olabilir)
        script_name = "sherlock.py" # Repo içindeki ana betik adı
        script_path = os.path.join(run_dir, "sherlock", script_name) # İç içe bir 'sherlock' klasörü daha var

        if not os.path.isdir(run_dir) or not os.path.isfile(script_path):
            print(f"{R}HATA: Sherlock kurulu değil veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Lütfen önce aracı kurun ('Install' seçeneği).{RESET}")
            return False

        try:
            names_input = input(f" Aranacak Kullanıcı Ad(lar)ı (boşlukla ayırın) [{self.TITLE}] >> ").strip()
            if not names_input:
                print(f"{R}HATA: Kullanıcı adı boş olamaz.{RESET}")
                return False

            # Kullanıcı adlarını ayır
            usernames = names_input.split()

            # İsteğe bağlı ek parametreler
            timeout_str = input(f" Zaman Aşımı (saniye, boş bırakırsanız varsayılan) [{self.TITLE}] >> ").strip()
            output_file = input(f" Çıktı Dosyası (isteğe bağlı, örn: results.txt) [{self.TITLE}] >> ").strip()
            # Diğer seçenekler: --print-found, --site <site_name>, --proxy <PROXY_URL> vb.

            # Komutu oluştur (sudo genellikle gerekmez)
            command = [sys.executable, script_path]
            command.extend(usernames) # Kullanıcı adlarını ekle
            if timeout_str and timeout_str.isdigit(): command.extend(["--timeout", timeout_str])
            if output_file: command.extend(["--output", output_file])
            # Örnek: command.append("--print-found") # Sadece bulunanları yazdır

            print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
            print(f"{C}Sherlock çalışıyor... (Durdurmak için Ctrl+C){RESET}")
            # Sherlock kendi dizininden çalışmalı
            subprocess.run(command, cwd=run_dir, check=True)
            return True
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
            return False
        except FileNotFoundError:
             print(f"{R}HATA: Python yorumlayıcısı veya '{script_path}' bulunamadı.{RESET}")
             return False
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: Sherlock hatası (Kod: {e.returncode}).{RESET}")
             return False
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")
             return False


class SocialScan(HackingTool):
    TITLE = "SocialScan (Username/Email Availability Check)"
    DESCRIPTION = (
        "Çevrimiçi platformlarda kullanıcı adı ve e-posta adresinin \n"
        "kullanılabilirliğini yüksek doğrulukla kontrol eder."
    )
    # Pip ile kurulur, INSTALLATION_DIR gereksiz
    INSTALLATION_DIR = ""
    INSTALL_COMMANDS = [f"sudo {sys.executable} -m pip install socialscan"]
    PROJECT_URL = "https://github.com/iojw/socialscan"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        """Kullanıcıdan girdi alarak socialscan'ı çalıştırır."""
        tool = "socialscan"
        # Önce aracın kurulu olup olmadığını kontrol et
        if not is_tool_installed(tool):
             print(f"{R}HATA: '{tool}' komutu bulunamadı.{RESET}")
             print(f"{Y}Lütfen önce aracı kurun ('Install' seçeneği).{RESET}")
             return False

        try:
            targets_input = input(f" Kullanıcı Adı veya Email (birden fazlaysa boşlukla ayırın) [{self.TITLE}] >> ").strip()
            if not targets_input:
                 print(f"{R}HATA: Girdi boş olamaz.{RESET}")
                 return False

            # Girdiyi boşluklara göre ayır
            targets = targets_input.split()
            # Komutu oluştur (sudo genellikle gerekmez)
            command = [tool]
            command.extend(targets)
            # Diğer seçenekler: --platforms, --show-available, --fast vb.

            print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
            subprocess.run(command, check=True)
            return True
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
            return False
        except FileNotFoundError:
             # Bu durum is_tool_installed kontrolünden sonra pek olası değil ama...
             print(f"{R}HATA: '{tool}' komutu çalıştırılamadı.{RESET}")
             return False
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: SocialScan hatası (Kod: {e.returncode}).{RESET}")
             return False
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")
             return False


# === Ana Koleksiyon Tanımı ===

class SocialMediaFinderTools(HackingToolsCollection):
    TITLE = "Sosyal Medya Bulucu Araçlar (OSINT)"
    DESCRIPTION = "Kullanıcı adı, e-posta veya yüz tanıma ile sosyal medya profillerini bulma araçları."
    TOOLS = [
        FacialFind(),
        FindUser(),
        Sherlock(),
        SocialScan()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    # Gerekli temel kütüphaneleri kontrol et (webbrowser, shutil)
    try:
        import webbrowser
        import shutil
    except ImportError as e:
        missing_module = str(e).split("'")[-2]
        print(f"{R}HATA: Gerekli '{missing_module}' kütüphanesi bulunamadı.{RESET}")
        sys.exit(1)

    # Ana koleksiyonu oluştur
    main_collection = SocialMediaFinderTools()
    try:
         main_collection.show_options()
    except KeyboardInterrupt:
         print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception:
         print(f"\n{R}Kritik bir hata oluştu!{RESET}")
         print_exc()
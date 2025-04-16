# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
import ipaddress # iptool.py'den kopyalanan _is_tool_installed için
import shutil # _is_tool_installed için
from platform import system
from traceback import print_exc
from typing import Callable, List, Tuple, Any

# --- UYARI ---
# Bu betik, çeşitli web saldırı ve bilgi toplama araçlarını yönetmek için bir arayüzdür.
# Bu araçların birçoğu (örn. bruteforce, tarayıcılar) İZİNSİZ sistemlere karşı kullanıldığında YASA DIŞIDIR.
# Sadece izinli sistemlerde ve eğitim amaçlı kullanın. Sorumluluk kullanıcıya aittir.
# Blazy gibi bazı araçlar eski Python 2.7 gerektirir ve çalışmayabilir.
# Dirb gibi araçlar derleme gerektirir ve sistem bağımlılıkları vardır.
# Araçların GitHub repoları veya bağımlılıkları zamanla kullanılamaz hale gelebilir.
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

class HackingTool(object):
    """Tek bir aracı temsil eden temel sınıf."""
    TITLE: str = "Başlıksız Araç"
    DESCRIPTION: str = "Açıklama Yok"
    INSTALL_COMMANDS: List[str] = []
    INSTALLATION_DIR: str = "" # Kurulum dizini (varsa, bazı komutlar burada çalıştırılır)
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
        # Kullanıcı tanımlı ek seçenekleri ekle
        self.OPTIONS.extend(options)
        # Kaldırma komutları varsa Uninstall ekle
        if self.UNINSTALL_COMMANDS:
             self.OPTIONS.append(('Uninstall', self.uninstall))

    def _execute_commands(self, command_list: List[str], target_dir: str = None):
        """Verilen komut listesini belirtilen dizinde sırayla çalıştırır."""
        if not isinstance(command_list, (list, tuple)):
            print(f"{R}HATA: Komut listesi geçersiz.{RESET}")
            return False # Başarısızlık belirt

        print(f"{C}--- Komutlar Çalıştırılıyor ---{RESET}")
        success = True
        # Çalışma dizinini belirle: Önce target_dir, sonra aracın INSTALLATION_DIR'ı, yoksa None (mevcut dizin)
        effective_cwd = target_dir or self.INSTALLATION_DIR or None
        if effective_cwd and not os.path.isdir(effective_cwd):
             print(f"{Y}Uyarı: Hedef dizin '{effective_cwd}' mevcut değil. Komutlar mevcut dizinde çalıştırılacak.{RESET}")
             effective_cwd = None

        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            if effective_cwd:
                print(f"{C}   (Dizin: {effective_cwd}){RESET}")

            try:
                # shell=True, 'cd ... && ...' gibi yapıları çalıştırabilir ama güvenlik riski taşır.
                # Özellikle sudo ile birlikte dikkatli olunmalı.
                # check=True: Komut hata kodu döndürürse CalledProcessError fırlatır.
                subprocess.run(command, shell=True, check=True, cwd=effective_cwd)
            except FileNotFoundError as e:
                 # Komutun kendisi bulunamazsa (örn. 'git', 'pip', 'python2.7' yoksa)
                 print(f"{R}HATA: Komut veya program bulunamadı: {e}{RESET}")
                 print(f"{Y}Komut: '{command}'{RESET}")
                 print(f"{Y}Gerekli programın sisteminizde kurulu ve PATH içinde olduğundan emin olun.{RESET}")
                 success = False
                 break # Hata durumunda diğer komutlara geçme
            except subprocess.CalledProcessError as e:
                # Komut çalıştı ancak sıfırdan farklı bir çıkış kodu döndürdü (hata)
                print(f"{R}HATA: Komut hata ile sonlandı (Kod: {e.returncode}): {command}{RESET}")
                # Komutun hata çıktısını göstermek faydalı olabilir (eğer yakalanmışsa)
                # if e.stderr: print(f"{R}Hata Çıktısı:\n{e.stderr}{RESET}")
                success = False
                break # Hata durumunda diğer komutlara geçme
            except Exception as e:
                 # Diğer beklenmedik hatalar (örn. izin hataları)
                 print(f"{R}Komut çalıştırılırken beklenmedik hata: {command}\nHata: {e}{RESET}")
                 success = False
                 break # Hata durumunda diğer komutlara geçme

        status = f"{G}Başarılı{RESET}" if success else f"{R}Başarısız{RESET}"
        print(f"{C}--- Komutlar Tamamlandı (Durum: {status}) ---{RESET}")
        return success # Komutların genel başarı durumunu döndür

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
        valid_indices = list(range(1, len(self.OPTIONS) + 1)) # Geçerli seçenek numaraları (1'den başlar)
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
                ret_code = selected_function() # Seçilen fonksiyonu çalıştır (install, run, uninstall...)
                if ret_code != 99: pause() # Eğer fonksiyon 'Geri' sinyali vermediyse bekle
            elif option_index in extra_options:
                if option_index == 98:
                    self.show_project_page()
                    pause()
                elif option_index == 99:
                    # Geri veya Çıkış
                    if parent is None:
                         print(f"{B}Çıkılıyor...{RESET}")
                         sys.exit()
                    return 99 # Bir üst menüye dönmek için 99 döndür
            else:
                print(f"{R}Geçersiz seçenek.{RESET}")
                time.sleep(1)

        except (ValueError, TypeError):
             print(f"{R}Lütfen geçerli bir numara girin.{RESET}")
             time.sleep(1)
        except KeyboardInterrupt:
             print("\nİşlem iptal edildi.")
             # İsteğe bağlı olarak burada da çıkılabilir veya menüye dönülebilir
             # sys.exit()
             return None # Ana menüye dönmek için None döndürebiliriz
        except Exception:
            print(f"{R}Bir hata oluştu!{RESET}")
            print_exc() # Hatanın detayını yazdır
            pause()

        # Eğer 'Geri' seçilmediyse, aynı menüyü tekrar göster
        if ret_code != 99:
            return self.show_options(parent=parent)
        else:
             return 99 # 'Geri' ise, bu değeri yukarı taşı

    def before_install(self):
        """Kurulum öncesi işlemler (alt sınıflar override edebilir)."""
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")

    def install(self):
        """Varsayılan kurulum metodu. INSTALL_COMMANDS'ı çalıştırır."""
        self.before_install()
        # Komutları INSTALLATION_DIR içinde çalıştırmayı dene
        success = self._execute_commands(self.INSTALL_COMMANDS, target_dir=None) # Komutlar kendi cd'sini içerebilir
        self.after_install(success)
        return success # Kurulumun başarı durumunu döndür

    def after_install(self, success):
        """Kurulum sonrası işlemler (alt sınıflar override edebilir)."""
        if success:
            print(f"\n{G}{self.TITLE} kurulumu başarıyla tamamlandı (veya hatalarla bitti, yukarıyı kontrol edin).{RESET}")
        else:
            print(f"\n{R}{self.TITLE} kurulumu başarısız oldu.{RESET}")

    def before_uninstall(self) -> bool:
        """Kaldırma öncesi onay (alt sınıflar override edebilir)."""
        confirm = input(f"{Y}UYARI: {self.TITLE} kaldırılacak. Emin misiniz? [e/H]: {W}").strip().lower()
        return confirm == 'e'

    def uninstall(self):
        """Varsayılan kaldırma metodu."""
        if self.before_uninstall():
            print(f"\n{C}{self.TITLE} kaldırılıyor...{RESET}")
            # Kaldırma komutları genellikle global çalışır veya kendi dizinlerini belirtir
            success = self._execute_commands(self.UNINSTALL_COMMANDS, target_dir=None)
            self.after_uninstall(success)
            return success
        else:
             print("Kaldırma işlemi iptal edildi.")
             return False

    def after_uninstall(self, success):
        """Kaldırma sonrası işlemler (alt sınıflar override edebilir)."""
        if success:
             print(f"\n{G}{self.TITLE} kaldırıldı (veya hatalarla bitti).{RESET}")
        else:
             print(f"\n{R}{self.TITLE} kaldırma işlemi başarısız oldu.{RESET}")

    def before_run(self):
        """Çalıştırma öncesi işlemler (alt sınıflar override edebilir)."""
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")

    def run(self):
        """Varsayılan çalıştırma metodu. RUN_COMMANDS listesini çalıştırır."""
        self.before_run()
        success = False
        if not self.RUN_COMMANDS:
            print(f"{Y}Bu araç için özel bir 'run' metodu veya RUN_COMMANDS tanımlanmamış.{RESET}")
        else:
             # Çalıştırma komutlarını INSTALLATION_DIR içinde çalıştırmayı dene
             success = self._execute_commands(self.RUN_COMMANDS, target_dir=self.INSTALLATION_DIR)
        self.after_run(success)
        return success

    def after_run(self, success):
        """Çalıştırma sonrası işlemler (alt sınıflar override edebilir)."""
        # Genellikle bir şey yapmaya gerek yok, ama alt sınıflar kullanabilir
        pass

    def show_project_page(self):
        """Proje sayfasını varsayılan tarayıcıda açar."""
        if self.PROJECT_URL:
            try:
                print(f"{C}Proje sayfası açılıyor: {self.PROJECT_URL}{RESET}")
                webbrowser.open_new_tab(self.PROJECT_URL)
            except Exception as e:
                print(f"{R}Tarayıcı açılırken hata: {e}{RESET}")
        else:
            print(f"{Y}Bu araç için proje URL'si belirtilmemiş.{RESET}")

# === Koleksiyon Sınıfı (Framework Yapısı) ===

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
            # Araçların başlığını al (TITLE özelliği olmalı)
            tool_title = getattr(tool, 'TITLE', f'İsimsiz Araç {index}')
            # İsteğe bağlı: Aracın kurulu olup olmadığını veya özel durumunu göster
            # status = f" ({tool.is_installed()})" if hasattr(tool, 'is_installed') else ""
            # print(f"  [{index}] {tool_title}{status}")
            print(f"  [{index}] {tool_title}")

        parent_title = getattr(parent, 'TITLE', 'Ana Menü') if parent is not None else 'Çıkış'
        print(f"\n  [{99}] Geri ({parent_title})")

        tool_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None

        try:
            tool_index = int(tool_index_str)
            if tool_index in valid_indices:
                selected_tool = self.TOOLS[tool_index]
                # Seçilen aracın menüsünü göster, parent olarak kendini (koleksiyonu) ver
                ret_code = selected_tool.show_options(parent=self)
            elif tool_index == 99:
                # Geri veya Çıkış
                if parent is None:
                     print(f"{B}Çıkılıyor...{RESET}")
                     sys.exit()
                return 99 # Bir üst menüye dönmek için 99 döndür
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

        # Eğer alt menüden 'Geri' (99) gelinmediyse, bu menüyü tekrar göster
        if ret_code != 99:
            return self.show_options(parent=parent)
        else:
             return 99 # 'Geri' ise, bu değeri yukarı taşı

# === Web Saldırı Araç Tanımlamaları ===

class Web2Attack(HackingTool):
    TITLE = "Web2Attack Framework"
    DESCRIPTION = "Python ile yazılmış araçlar ve exploitler içeren web saldırı framework'ü."
    INSTALLATION_DIR = "web2attack"
    INSTALL_COMMANDS = [f"sudo git clone https://github.com/santatic/web2attack.git {INSTALLATION_DIR}"]
    # RUN_COMMANDS INSTALLATION_DIR içinde çalıştırılır
    RUN_COMMANDS = ["sudo python3 w2aconsole"] # Python 3 gerektirir
    PROJECT_URL = "https://github.com/santatic/web2attack"

class Skipfish(HackingTool):
    TITLE = "Skipfish Web Scanner"
    DESCRIPTION = (
        "Skipfish – Tam otomatik, aktif web uygulaması güvenlik keşif aracı.\n"
        f"{Y}Kullanım:{W} skipfish -o [KlasörAdı] hedef_ip/site"
    )
    # Kurulum komutu yok, sistemde kurulu olduğu varsayılıyor
    INSTALL_COMMANDS = []
    # Run sadece yardım gösterir
    RUN_COMMANDS = [
        "skipfish -h", # sudo gerekmeyebilir
        'echo "\nKullanım Örneği: skipfish -o CIKTI_KLASORU http://hedefsite.com"'
    ]

    def __init__(self):
        # Kurulum seçeneği olmasın, sistemde kurulu varsayılıyor
        super().__init__(installable=False)

    def run(self):
        # Varsayılan run yerine, kurulu olup olmadığını kontrol edip yardım gösterelim
        tool = "skipfish"
        print(f"\n{C}'{tool}' aracının sistemde kurulu olduğu varsayılıyor.{RESET}")
        if not is_tool_installed(tool):
            print(f"{R}HATA: '{tool}' komutu sistem PATH'inde bulunamadı.{RESET}")
            print(f"{Y}Lütfen '{tool}' aracını sisteminize kurun (örn: sudo apt install skipfish).{RESET}")
            return False # Başarısız
        # Komut bulunduysa, varsayılan RUN_COMMANDS'ı çalıştır (yardım gösterir)
        return super().run()


class SubDomainFinder(HackingTool):
    TITLE = "SubDomain Finder (Sublist3r)"
    DESCRIPTION = (
        "Sublist3r, OSINT kullanarak web sitelerinin alt alan adlarını (subdomain) listelemek için tasarlanmış bir Python aracıdır.\n"
        f"{Y}Kullanım Örnekleri:\n\t"
        f"{W}[1] python3 sublist3r.py -d example.com\n\t"
        f"{W}[2] python3 sublist3r.py -d example.com -p 80,443 -o subdomains.txt{RESET}"
    )
    INSTALLATION_DIR = "Sublist3r"
    INSTALL_COMMANDS = [
        # Genel bağımlılıklar (sistem geneli veya --user ile)
        # sudo kullanmak yerine --user ile denemek daha iyi olabilir, ama sudo ile bırakalım şimdilik
        f"sudo {sys.executable} -m pip install requests argparse dnspython",
        # Klonla
        f"sudo git clone https://github.com/aboul3la/Sublist3r.git {INSTALLATION_DIR}",
        # Araca özel bağımlılıklar (kurulum dizini içinde)
        # Önce dizine gir, sonra pip install yap
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} -m pip install -r requirements.txt"
    ]
    RUN_COMMANDS = [] # run metodu override edildi
    PROJECT_URL = "https://github.com/aboul3la/Sublist3r"

    def run(self):
        """Kullanıcıdan domain ve isteğe bağlı parametreler alarak Sublist3r'ı çalıştırır."""
        run_dir = self.INSTALLATION_DIR
        # Betik adı repo içinde genellikle 'sublist3r.py' olur
        script_path = os.path.join(run_dir, "sublist3r.py")

        # Betik veya dizin yoksa hata ver
        if not os.path.isdir(run_dir) or not os.path.isfile(script_path):
            print(f"{R}HATA: Sublist3r kurulu değil veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Lütfen önce aracı kurun ('Install' seçeneği).{RESET}")
            return False # Başarısız

        try:
            domain = input(f" Hedef Domain (örn: example.com) [{self.TITLE}] >> ").strip()
            if not domain:
                print(f"{R}HATA: Domain boş olamaz.{RESET}")
                return False
            ports = input(f" Taranacak Portlar (isteğe bağlı, virgülle ayır, örn: 80,443) [{self.TITLE}] >> ").strip()
            output_file = input(f" Çıktı Dosyası (isteğe bağlı, örn: subdomains.txt) [{self.TITLE}] >> ").strip()
            threads = input(f" Thread Sayısı (isteğe bağlı, örn: 10) [{self.TITLE}] >> ").strip()
            # Diğer Sublist3r argümanları da eklenebilir (-v verbose, -e search_engines vb.)

            # Komutu oluştur
            command = [sys.executable, script_path, "-d", domain]
            if ports: command.extend(["-p", ports])
            if output_file: command.extend(["-o", output_file])
            if threads and threads.isdigit(): command.extend(["-t", threads])

            print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
            # Komutu Sublist3r'ın dizininde çalıştır
            subprocess.run(command, cwd=run_dir, check=True)
            return True # Başarılı
        except KeyboardInterrupt:
             print("\nİşlem kullanıcı tarafından iptal edildi.")
             return False
        except FileNotFoundError:
             # python3 veya script_path bulunamazsa (kurulum hatası olabilir)
             print(f"{R}HATA: Python yorumlayıcısı veya '{script_path}' bulunamadı.{RESET}")
             return False
        except subprocess.CalledProcessError as e:
             print(f"{R}Sublist3r çalıştırılırken hata oluştu (Kod: {e.returncode}).{RESET}")
             return False
        except Exception as e:
            print(f"{R}Sublist3r çalıştırılırken beklenmedik bir hata oluştu: {e}{RESET}")
            return False

class CheckURL(HackingTool):
    TITLE = "CheckURL (IDN Homograph Attack Detector)"
    DESCRIPTION = (
        "Uluslararası Alan Adı (IDN) Homograph Saldırısı kullanan kötü niyetli URL'leri tespit eder.\n\t"
        f"{Y}[Örnek Kullanım]{W} python3 checkURL.py --url google.com{RESET}"
    )
    INSTALLATION_DIR = "checkURL"
    INSTALL_COMMANDS = [f"sudo git clone https://github.com/UndeadSec/checkURL.git {INSTALLATION_DIR}"]
    RUN_COMMANDS = [] # run metodu override edildi
    PROJECT_URL = "https://github.com/UndeadSec/checkURL"

    def run(self):
        """Kullanıcıdan URL alarak checkURL aracını çalıştırır."""
        run_dir = self.INSTALLATION_DIR
        script_path = os.path.join(run_dir, "checkURL.py")

        if not os.path.isdir(run_dir) or not os.path.isfile(script_path):
            print(f"{R}HATA: checkURL kurulu değil veya '{script_path}' bulunamadı.{RESET}")
            print(f"{Y}Lütfen önce aracı kurun ('Install' seçeneği).{RESET}")
            return False

        try:
            url_to_check = input(f" Kontrol edilecek URL [{self.TITLE}] >> ").strip()
            if not url_to_check:
                print(f"{R}HATA: URL boş olamaz.{RESET}")
                return False

            # Komutu oluştur (checkURL.py --url <URL>)
            command = [sys.executable, script_path, "--url", url_to_check]
            print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
            # Komutu checkURL dizininde çalıştır
            subprocess.run(command, cwd=run_dir, check=True)
            return True
        except KeyboardInterrupt:
             print("\nİşlem kullanıcı tarafından iptal edildi.")
             return False
        except FileNotFoundError:
             print(f"{R}HATA: Python yorumlayıcısı veya '{script_path}' bulunamadı.{RESET}")
             return False
        except subprocess.CalledProcessError as e:
            print(f"{R}checkURL çalıştırılırken hata oluştu (Kod: {e.returncode}).{RESET}")
            return False
        except Exception as e:
            print(f"{R}checkURL çalıştırılırken beklenmedik bir hata oluştu: {e}{RESET}")
            return False

class Blazy(HackingTool):
    TITLE = "Blazy (Login Bruteforcer)"
    DESCRIPTION = (f"Modern bir giriş sayfası kaba kuvvet saldırı aracı.\n"
                   f"{R}{BRIGHT}UYARI: Python 2.7 gerektirir! Modern sistemlerde çalışmayabilir!{RESET}\n"
                   f"{Y}Kullanım:{W} python2.7 blazy.py -h (yardım için)")
    INSTALLATION_DIR = "Blazy"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/UltimateHackers/Blazy.git {INSTALLATION_DIR}",
        # Python 2.7 pip'ini bulmak zor olabilir, 'pip2' veya 'pip2.7' deneyebiliriz
        # Bu komut büyük ihtimalle başarısız olacaktır.
        f"cd {INSTALLATION_DIR} && (sudo pip2 install -r requirements.txt || sudo pip2.7 install -r requirements.txt || echo '{R}Python 2 pip bulunamadı/kurulum başarısız!{RESET}')"
    ]
    # Çalıştırma için python2.7 gerekli, sadece yardım gösterelim
    RUN_COMMANDS = ["python2.7 blazy.py -h"]
    PROJECT_URL = "https://github.com/UltimateHackers/Blazy"

    def install(self):
        # Kurulum öncesi Python 2 kontrolü yapalım
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")
        py2_executable = None
        for cmd in ["python2.7", "python2"]:
            if is_tool_installed(cmd):
                py2_executable = cmd
                break
        if not py2_executable:
            print(f"{R}HATA: Python 2.7 veya Python 2 sisteminizde bulunamadı.{RESET}")
            print(f"{Y}Blazy aracı Python 2 gerektirir ve bu sürüm artık desteklenmemektedir.{RESET}")
            return False # Kurulum başarısız

        # pip2 kontrolü
        pip2_executable = None
        for cmd in ["pip2.7", "pip2"]:
             if is_tool_installed(cmd):
                  pip2_executable = cmd
                  break
        if not pip2_executable:
             print(f"{Y}UYARI: Python 2 pip ('pip2' veya 'pip2.7') bulunamadı.{RESET}")
             print(f"{Y}Bağımlılıklar kurulamayabilir.{RESET}")
             # Yine de klonlamaya devam et, ama INSTALL_COMMANDS'ı buna göre ayarla
             self.INSTALL_COMMANDS = [
                 f"sudo git clone https://github.com/UltimateHackers/Blazy.git {self.INSTALLATION_DIR}",
                 f"echo '{Y}Python 2 pip bulunamadığı için bağımlılıklar atlandı.'",
             ]
        else:
            # pip2 bulunduysa orijinal komutları kullan
            self.INSTALL_COMMANDS = [
                f"sudo git clone https://github.com/UltimateHackers/Blazy.git {self.INSTALLATION_DIR}",
                f"cd {self.INSTALLATION_DIR} && sudo {pip2_executable} install -r requirements.txt"
            ]

        # Komutları şimdi çalıştır
        success = self._execute_commands(self.INSTALL_COMMANDS, target_dir=None)
        self.after_install(success)

        if success:
             print(f"\n{G}Blazy klonlandı. Çalıştırmak için '{py2_executable} {os.path.join(self.INSTALLATION_DIR, 'blazy.py')}' kullanın.{RESET}")
             if not pip2_executable: print(f"{Y}Ancak bağımlılıklar kurulamamış olabilir.{RESET}")
        return success

    def run(self):
        # Yardım komutunu çalıştır, ama önce python2'nin varlığını tekrar kontrol et
        py2_executable = None
        for cmd in ["python2.7", "python2"]:
            if is_tool_installed(cmd):
                py2_executable = cmd
                break
        if not py2_executable:
             print(f"{R}HATA: Python 2 bulunamadığı için Blazy çalıştırılamıyor.{RESET}")
             return False
        # RUN_COMMANDS'ı dinamik olarak ayarla
        self.RUN_COMMANDS = [f"{py2_executable} blazy.py -h"]
        return super().run()


class SubDomainTakeOver(HackingTool):
    TITLE = "Sub-Domain TakeOver Check (takeover.py)"
    DESCRIPTION = (
        "Bir alt alan adının (subdomain.example.com) kaldırılmış veya silinmiş \n"
        "bir harici servise (örn: GitHub Pages, S3) işaret etmesi durumunda \n"
        "ortaya çıkan zafiyeti kontrol eder.\n"
        f"{Y}Kullanım:{W} python3 takeover.py -d www.domain.com -v{RESET}"
    )
    INSTALLATION_DIR = "takeover"
    INSTALL_COMMANDS = [
        # sudo gerekebilir mi? Genellikle setup.py için gerekir.
        f"git clone https://github.com/m4ll0k/takeover.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} setup.py install"
    ]
    PROJECT_URL = "https://github.com/m4ll0k/takeover"
    RUN_COMMANDS = [] # run metodu override edildi

    def __init__(self):
        # Kurulum sonrası manuel çalıştırma gerektirdiği için Run seçeneği olmasın?
        # Ya da run metodu ile kullanımını gösterelim.
        super().__init__(runnable=True) # run metodu var

    def run(self):
        # takeover.py komutunun PATH'de olduğunu varsayalım (setup.py install sonrası)
        tool = "takeover.py"
        print(f"\n{C}'{tool}' aracının kurulum sonrası PATH'e eklendiği varsayılıyor.{RESET}")
        # if not is_tool_installed(tool): # setup.py install her zaman PATH'e eklemeyebilir
        #     print(f"{R}HATA: '{tool}' komutu sistem PATH'inde bulunamadı.{RESET}")
        #     print(f"{Y}Kurulum başarılı olduysa, aracı tam yoluyla çalıştırmanız gerekebilir.{RESET}")
        #     return False

        # Doğrudan script'i bulup çalıştırmayı deneyelim
        # setup.py nereye kurar? site-packages? /usr/local/bin? Belirsiz.
        # En iyisi kullanıcıya nasıl çalıştırılacağını göstermek.
        print(f"\n{Y}Kullanım Örnekleri:{RESET}")
        print(f" {W}python3 {tool} -d subdomain.example.com{RESET}")
        print(f" {W}python3 {tool} -l list_of_subdomains.txt -o result.json{RESET}")
        print(f" {W}python3 {tool} --help (Tüm seçenekler için){RESET}")
        print(f"\n{Y}Lütfen aracı manuel olarak terminalden çalıştırın.{RESET}")
        return True # Sadece bilgi verdiği için başarılı sayalım


class Dirb(HackingTool):
    TITLE = "Dirb (Web Content Scanner)"
    DESCRIPTION = (
        "DIRB bir Web İçerik Tarayıcısıdır. Mevcut (ve/veya gizli) Web Nesnelerini arar.\n"
        "Bir web sunucusuna karşı sözlük tabanlı bir saldırı başlatarak çalışır.\n"
        f"{R}{BRIGHT}UYARI: Kurulumu kaynak koddan derleme gerektirir! 'build-essential' gibi paketler gerekir.{RESET}"
    )
    INSTALLATION_DIR = "dirb_tool" # dirb sistem komutuyla karışmasın diye farklı isim
    INSTALL_COMMANDS = [
        # Gerekli paketleri kurma komutu (Debian/Ubuntu örneği)
        "echo '--- Gerekli derleme araçları kuruluyor (sudo apt gerektirir) ---' && sudo apt-get update && sudo apt-get install -y build-essential",
        # Klonla
        f"sudo git clone https://gitlab.com/kalilinux/packages/dirb.git {INSTALLATION_DIR}",
        # Derle ve kur (configure betiği olmayabilir, doğrudan make deneriz)
        # Hata almamak için || true ekleyelim
        f"cd {INSTALLATION_DIR} && (sudo make || echo '{Y}make başarısız oldu{RESET}') && (sudo make install || echo '{Y}make install başarısız/gerekli değil{RESET}')"
        # Alternatif: Derlenen dosyayı PATH'e eklemek veya tam yoldan çalıştırmak
    ]
    PROJECT_URL = "https://gitlab.com/kalilinux/packages/dirb"
    RUN_COMMANDS = [] # run metodu override edildi

    def install(self):
        # Kurulum öncesi build-essential kontrolü (yaklaşık)
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor (derleme gerektirir)...{RESET}")
        if not is_tool_installed("gcc") or not is_tool_installed("make"):
             print(f"{Y}UYARI: 'gcc' veya 'make' komutları bulunamadı.{RESET}")
             print(f"{Y}Kurulumun ilk adımı bunları kurmayı deneyecek (Debian/Ubuntu için 'build-essential').{RESET}")
             print(f"{Y}Farklı bir sistem kullanıyorsanız, derleme araçlarını manuel olarak kurmanız gerekebilir.{RESET}")
        # Komutları çalıştır
        success = self._execute_commands(self.INSTALL_COMMANDS, target_dir=None)
        self.after_install(success)

        if success:
             print(f"\n{G}Dirb derlendi/kuruldu (veya hatalarla bitti).{RESET}")
             print(f"{Y}'dirb' komutunun çalışıp çalışmadığını kontrol edin.{RESET}")
        return success

    def run(self):
        """Kullanıcıdan URL ve isteğe bağlı sözlük alarak dirb'ü çalıştırır."""
        # dirb komutunun PATH'de olduğunu varsayalım (make install sonrası)
        tool = "dirb"
        if not is_tool_installed(tool):
             # Eğer derleme sonrası /usr/local/bin gibi bir yere kurulmadıysa,
             # INSTALLATION_DIR içindeki derlenmiş dosyayı arayabiliriz.
             compiled_path = os.path.join(self.INSTALLATION_DIR, tool)
             if os.path.isfile(compiled_path) and os.access(compiled_path, os.X_OK):
                  print(f"{Y}Uyarı: '{tool}' komutu PATH'de bulunamadı, ancak '{compiled_path}' kullanılıyor.{RESET}")
                  tool = compiled_path # Tam yolu kullan
             else:
                  print(f"{R}HATA: '{tool}' komutu bulunamadı veya çalıştırılabilir değil.{RESET}")
                  print(f"{Y}Kurulum/derleme başarılı oldu mu ve araç PATH'de mi?{RESET}")
                  return False

        try:
            target_url = input(f" Hedef URL (örn: http://example.com) [{self.TITLE}] >> ").strip()
            if not target_url:
                 print(f"{R}HATA: URL boş olamaz.{RESET}")
                 return False
            wordlist = input(f" Sözlük Dosyası (Boş bırakırsanız varsayılan kullanılır) [{self.TITLE}] >> ").strip()

            # Komutu oluştur (sudo genellikle gerekmez)
            command = [tool, target_url]
            if wordlist:
                # Sözlük dosyasının varlığını kontrol etmek iyi olurdu
                if os.path.isfile(wordlist):
                     command.append(wordlist) # Varsayılan sözlük yerine belirtileni kullan
                else:
                     print(f"{Y}Uyarı: Belirtilen sözlük dosyası '{wordlist}' bulunamadı. Varsayılan kullanılacak.{RESET}")
            # Diğer dirb seçenekleri de eklenebilir (-X .php,.html vb.)

            print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
            subprocess.run(command, check=True)
            return True
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
            return False
        except FileNotFoundError:
             # Bu durum 'tool' yolu hatalıysa oluşur, yukarıda kontrol edilmiş olmalı
             print(f"{R}HATA: '{tool}' komutu çalıştırılamadı.{RESET}")
             return False
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: Dirb çalıştırılırken hata oluştu (Kod: {e.returncode}).{RESET}")
             return False
        except Exception as e:
             print(f"{R}Beklenmedik bir hata oluştu: {e}{RESET}")
             return False


# === Ana Koleksiyon Tanımı ===

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
    # Gerekli temel kütüphaneleri kontrol et (webbrowser, ipaddress, shutil)
    try:
        import webbrowser
        import ipaddress
        import shutil
    except ImportError as e:
        missing_module = str(e).split("'")[-2]
        print(f"{R}HATA: Gerekli '{missing_module}' kütüphanesi bulunamadı.{RESET}")
        print(f"{Y}Python kurulumunuzu kontrol edin veya 'pip install {missing_module}' deneyin (bazıları standart kütüphanedir).{RESET}")
        sys.exit(1)

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
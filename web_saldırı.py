# -*- coding: utf-8 -*-
# web_saldırı.py (Framework - Geliştirilmiş Uyarılar ve Talimatlar)

import os
import sys
import webbrowser
import subprocess
import time
import shutil # shutil.which için eklendi
from platform import system
from traceback import print_exc
from typing import List, Tuple, Callable, Any # Typing eklendi

# Renk tanımları
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    BRIGHT = Style.BRIGHT; DIM = Style.DIM; R = Fore.RED; G = Fore.GREEN
    Y = Fore.YELLOW; B = Fore.BLUE; M = Fore.MAGENTA; C = Fore.CYAN
    W = Fore.WHITE; RESET = Style.RESET_ALL
except ImportError:
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli ('pip install colorama'). Renksiz devam ediliyor.")
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""
    class Style: BRIGHT = ""; DIM = ""; RESET_ALL = ""
    class Fore: RED = ""; GREEN = ""; YELLOW = ""; BLUE = ""; MAGENTA = ""; CYAN = ""; WHITE = ""

# --- Gerekli Temel Araçları Kontrol Et ---
def check_prerequisites():
    """Temel bağımlılıkları (git, python3, pip) kontrol eder."""
    print(f"{C}Temel gereksinimler kontrol ediliyor...{RESET}")
    missing = []
    if not shutil.which("git"):
        missing.append("git")
    if not shutil.which("python3"): # veya sys.executable kontrolü
        missing.append("python3")
    # pip kontrolü biraz daha karmaşık olabilir (pip, pip3)
    if not shutil.which("pip3") and not shutil.which("pip"):
         missing.append("pip/pip3")

    if missing:
        print(f"{R}Hata: Temel araçlar eksik! Bu framework'ün çalışması için şunlar gereklidir:{RESET}")
        for tool in missing:
            print(f"{R} - {tool}{RESET}")
        print(f"{Y}Lütfen sisteminize uygun paket yöneticisi ile (örn: apt, yum, brew) eksik araçları kurun.{RESET}")
        return False
    print(f"{G}Temel gereksinimler (git, python3, pip) mevcut görünüyor.{RESET}")
    return True

# --- Yardımcı Fonksiyonlar ---
def clear_screen(): os.system("cls" if system() == "Windows" else "clear")
def pause():
    try: input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt: print("\nÇıkılıyor..."); sys.exit()

# --- Ana Framework Sınıfları (HackingTool, HackingToolsCollection) ---
# Bu sınıflar önceki cevaplardaki gibi kalabilir.
# _execute_commands fonksiyonunu biraz daha sağlamlaştıralım.

class HackingTool:
    TITLE = "Başlıksız Araç"; DESCRIPTION = "Açıklama Yok"
    INSTALL_COMMANDS = []; INSTALLATION_DIR = ""; UNINSTALL_COMMANDS = []
    RUN_COMMANDS = []; OPTIONS = []; PROJECT_URL = ""

    def __init__(self, options=None, installable=True, runnable=True):
        self.OPTIONS = []
        if installable and self.INSTALL_COMMANDS: self.OPTIONS.append(('Install', self.install))
        if runnable: self.OPTIONS.append(('Run', self.run))
        if options: self.OPTIONS.extend(options)
        if self.UNINSTALL_COMMANDS: self.OPTIONS.append(('Uninstall', self.uninstall))

    def _execute_commands(self, command_list: List[str], target_dir: str = None, shell_mode=True):
        """Verilen komut listesini çalıştırır (subprocess ile)."""
        if not isinstance(command_list, (list, tuple)):
            print(f"{R}HATA: Komut listesi geçersiz.{RESET}")
            return False

        print(f"{C}--- Komutlar Çalıştırılıyor ---{RESET}")
        success = True
        # Çalışma dizinini belirle (varsa kurulum dizini, yoksa mevcut dizin)
        effective_cwd = target_dir or self.INSTALLATION_DIR or None

        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            # Eğer effective_cwd varsa ve dizin değilse uyar
            if effective_cwd and not os.path.isdir(effective_cwd):
                 print(f"{Y}Uyarı: Hedef dizin '{effective_cwd}' bulunamadı veya geçerli değil. Komut mevcut dizinde çalıştırılacak.{RESET}")
                 run_cwd = None
            else:
                 run_cwd = effective_cwd

            if run_cwd: print(f"{C}   (Dizin: {run_cwd}){RESET}")

            try:
                # shell=True daha kolay ama güvenlik riski taşır.
                # shell=False daha güvenli ama komutları listeye bölmek gerekir.
                # Framework yapısı shell=True'ye daha uygun görünüyor.
                process = subprocess.run(command, shell=shell_mode, cwd=run_cwd,
                                         check=False, text=True, encoding='utf-8',
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE) # check=False

                # Çıktıları yazdır
                if process.stdout: print(f"{G}Stdout:{RESET}\n{process.stdout.strip()}")
                if process.stderr: print(f"{R}Stderr:{RESET}\n{process.stderr.strip()}")

                # Dönüş kodunu kontrol et
                if process.returncode != 0:
                    print(f"{R}HATA: Komut {process.returncode} kodu ile başarısız oldu!{RESET}")
                    success = False
                    # Opsiyonel: Hata durumunda dur
                    # break

            except FileNotFoundError as e:
                 print(f"{R}HATA: Komut veya program bulunamadı! '{command.split()[0]}' sisteminizde kurulu mu?{RESET}")
                 print(f"{R}Detay: {e}{RESET}")
                 success = False; break
            except Exception as e:
                print(f"{R}Komut çalıştırılırken beklenmedik hata: {e}{RESET}")
                traceback.print_exc()
                success = False; break

        status = f"{G}Başarılı{RESET}" if success else f"{R}Başarısız (veya Hatalı){RESET}"
        print(f"{C}--- Komut Çalıştırma Tamamlandı ({status}) ---{RESET}")
        return success

    # show_info, show_options, install, run, uninstall, vs. önceki cevaplardaki gibi kalabilir.
    # run metodu genellikle override edilir.
    def show_info(self):
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        print(self.DESCRIPTION)
        if self.PROJECT_URL: print(f"\n{C}Proje Sayfası:{W} {self.PROJECT_URL}{RESET}")
        print("-" * (len(self.TITLE) + 6))

    def show_options(self, parent=None):
        clear_screen(); self.show_info()
        print(f"\n{Y}Seçenekler:{RESET}")
        for index, option in enumerate(self.OPTIONS): print(f"  [{index + 1}] {option[0]}")
        if self.PROJECT_URL: print(f"  [{98}] Proje Sayfasını Aç")
        parent_title = parent.TITLE if hasattr(parent, 'TITLE') else 'Ana Menü'
        print(f"  [{99}] Geri ({parent_title if parent is not None else 'Çıkış'})")

        option_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None
        try:
            option_index = int(option_index_str)
            if 1 <= option_index <= len(self.OPTIONS):
                selected_function = self.OPTIONS[option_index - 1][1]
                ret_code = selected_function() # Fonksiyonu çağır
                if ret_code != 99: pause() # Geri dönülmediyse bekle
            elif option_index == 98 and self.PROJECT_URL:
                webbrowser.open_new_tab(self.PROJECT_URL); pause()
            elif option_index == 99:
                return 99 # Üst menüye sinyal
            else: print(f"{R}Geçersiz seçenek.{RESET}"); time.sleep(1)
        except (ValueError, TypeError): print(f"{R}Lütfen geçerli bir numara girin.{RESET}"); time.sleep(1)
        except Exception: print(f"{R}Bir hata oluştu!{RESET}"); traceback.print_exc(); pause()

        if ret_code != 99: return self.show_options(parent=parent)
        else: return 99

    def install(self):
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")
        success = self._execute_commands(self.INSTALL_COMMANDS) # Kurulum dizini otomatik kullanılır (varsa)
        print(f"\n{G if success else R}{self.TITLE} kurulumu {'tamamlandı!' if success else 'başarısız!'}{RESET}")
        return success

    def run(self): # Genellikle alt sınıflarda override edilir
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")
        if not self.RUN_COMMANDS:
            print(f"{Y}Bu araç için özel 'run' metodu veya RUN_COMMANDS tanımlanmamış.{RESET}")
            return False
        # Kurulum dizininde çalıştırmayı dene
        success = self._execute_commands(self.RUN_COMMANDS, target_dir=self.INSTALLATION_DIR)
        return success

    def uninstall(self):
        confirm = input(f"{Y}UYARI: {self.TITLE} kaldırılacak. Emin misiniz? [e/H]: {W}").strip().lower()
        if confirm == 'e':
            print(f"\n{C}{self.TITLE} kaldırılıyor...{RESET}")
            success = self._execute_commands(self.UNINSTALL_COMMANDS)
            print(f"\n{G if success else R}{self.TITLE} kaldırma işlemi {'tamamlandı.' if success else 'başarısız.'}{RESET}")
            return success
        return False

class HackingToolsCollection(HackingTool):
    TITLE = "Başlıksız Koleksiyon"; DESCRIPTION = "Açıklama Yok"; TOOLS = []
    def __init__(self, title: str = "", description: str = "", tools: list = None):
        super().__init__(installable=False, runnable=False) # Koleksiyonun kendisi kurulmaz/çalıştırılmaz
        self.TITLE = title or self.TITLE
        self.DESCRIPTION = description or self.DESCRIPTION
        self.TOOLS = tools or []

    def show_info(self):
        print(f"\n{M}{BRIGHT}=== {self.TITLE} ==={RESET}")
        if self.DESCRIPTION: print(self.DESCRIPTION)
        print("=" * (len(self.TITLE) + 6))

    def show_options(self, parent = None):
        clear_screen(); self.show_info()
        print(f"\n{Y}Araçlar:{RESET}")
        for index, tool in enumerate(self.TOOLS):
            tool_title = getattr(tool, 'TITLE', f'İsimsiz Araç {index+1}')
            print(f"  [{index + 1}] {tool_title}") # 1'den başlatalım

        parent_title = parent.TITLE if hasattr(parent, 'TITLE') else 'Ana Menü'
        print(f"\n  [{99}] Geri ({parent_title if parent is not None else 'Çıkış'})")

        tool_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None
        try:
            tool_index = int(tool_index_str)
            if 1 <= tool_index <= len(self.TOOLS):
                selected_tool = self.TOOLS[tool_index - 1]
                ret_code = selected_tool.show_options(parent=self) # Alt menüyü göster
            elif tool_index == 99:
                return 99 # Üst menüye sinyal
            else: print(f"{R}Geçersiz seçenek.{RESET}"); time.sleep(1)
        except (ValueError, TypeError): print(f"{R}Lütfen geçerli bir numara girin.{RESET}"); time.sleep(1)
        except Exception: print(f"{R}Bir hata oluştu!{RESET}"); traceback.print_exc(); pause()

        if ret_code != 99: return self.show_options(parent=parent)
        else: return 99

# --- Web Saldırı Araç Tanımları ---

class Web2Attack(HackingTool):
    TITLE = "Web2Attack Framework"
    DESCRIPTION = "Python ile yazılmış web saldırı framework'ü.\nKurulum ve kullanım için kendi içinde talimatları olabilir."
    INSTALLATION_DIR = "web2attack"
    INSTALL_COMMANDS = [
        # Önce silmeyi deneyebiliriz (tekrar kurulum için)
        f"rm -rf {INSTALLATION_DIR}",
        # Klonla
        f"git clone https://github.com/santatic/web2attack.git {INSTALLATION_DIR}"
        # Bağımlılık kurulumu repo içinde belirtilmişse eklenmeli
        # f"cd {INSTALLATION_DIR} && pip install -r requirements.txt" # Örnek
    ]
    # Çalıştırma komutu repo yapısına göre değişebilir
    RUN_COMMANDS = [f"python3 {os.path.join(INSTALLATION_DIR, 'w2aconsole')}"] # Tam yolu belirtmek daha iyi
    PROJECT_URL = "https://github.com/santatic/web2attack"

    # Çalıştırma için override edelim, cd yapmaya gerek kalmasın
    def run(self):
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")
        script_path = os.path.join(self.INSTALLATION_DIR, 'w2aconsole')
        if not os.path.exists(script_path):
             print(f"{R}Hata: '{script_path}' bulunamadı. Lütfen önce kurun.{RESET}")
             return False
        command = ["python3", script_path]
        print(f"{Y}>> Çalıştırılıyor: {' '.join(command)}{RESET}")
        try:
            # subprocess.run ile çalıştıralım ki etkileşimli olabilsin
            subprocess.run(command, check=False) # check=False
        except Exception as e:
            print(f"{R}Çalıştırma sırasında hata: {e}{RESET}")
            return False
        return True

class Skipfish(HackingTool):
    TITLE = "Skipfish Web Scanner"
    DESCRIPTION = ("Otomatik web uygulaması güvenlik keşif aracı.\n"
                  f"{Y}UYARI: Bu araç genellikle sistem geneline kurulmalıdır (örn: apt install skipfish).{RESET}\n"
                   "Buradaki 'Run' seçeneği sadece yardım menüsünü gösterir.")
    INSTALLABLE = False # Buradan kurulamaz
    RUN_COMMANDS = ["skipfish -h"] # Sadece yardım gösterir

    def __init__(self):
         # Kurulum seçeneği olmasın
        super().__init__(installable=False, runnable=True)

    def run(self):
        # skipfish'in kurulu olup olmadığını kontrol et
        if not shutil.which("skipfish"):
             print(f"{R}Hata: 'skipfish' komutu sisteminizde bulunamadı.{RESET}")
             print(f"{Y}Lütfen sisteminize uygun şekilde kurun (örn: sudo apt install skipfish).{RESET}")
             return False
        # Kuruluysa yardım menüsünü göster
        print(f"{C}Skipfish yardım menüsü gösteriliyor...{RESET}")
        return self._execute_commands(self.RUN_COMMANDS)


class SubDomainFinder(HackingTool):
    TITLE = "SubDomain Finder (Sublist3r)"
    DESCRIPTION = "Alt alan adlarını çeşitli kaynaklardan bulan OSINT aracı."
    INSTALLATION_DIR = "Sublist3r"
    INSTALL_COMMANDS = [
        f"rm -rf {INSTALLATION_DIR}", # Önce eskiyi sil
        f"git clone https://github.com/aboul3la/Sublist3r.git {INSTALLATION_DIR}",
        # Bağımlılıkları kütüphane olarak kuralım (requirements.txt bazen sorun çıkarır)
        f"pip3 install requests dnspython argparse" # Gerekli ana kütüphaneler
        # Veya requirements.txt kullan:
        # f"cd {INSTALLATION_DIR} && pip3 install -r requirements.txt"
    ]
    PROJECT_URL = "https://github.com/aboul3la/Sublist3r"
    RUN_COMMANDS = [] # run override edildi

    def install(self): # requirements.txt için install override edelim
         print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")
         # Önce git clone
         success_clone = self._execute_commands([self.INSTALL_COMMANDS[0], self.INSTALL_COMMANDS[1]])
         if not success_clone: return False
         # Sonra pip install (doğru dizinde)
         req_command = f"pip3 install -r requirements.txt"
         print(f"{Y}>> Çalıştırılıyor: {req_command} (Dizin: {self.INSTALLATION_DIR}){RESET}")
         success_pip = self._execute_commands([req_command], target_dir=self.INSTALLATION_DIR)
         print(f"\n{G if success_pip else R}{self.TITLE} kurulumu {'tamamlandı!' if success_pip else 'başarısız (pip)!'}{RESET}")
         return success_pip


    def run(self):
        script_path = os.path.join(self.INSTALLATION_DIR, "sublist3r.py")
        if not os.path.exists(script_path):
             print(f"{R}Hata: '{script_path}' bulunamadı. Lütfen önce kurun ('Install').{RESET}")
             return False

        domain = input(f"{Y}Hedef Domain (örn: example.com): {RESET}").strip()
        if not domain:
            print(f"{R}Domain boş olamaz!{RESET}")
            return False

        # Çalıştırma komutu
        command = f"python3 {script_path} -d {domain}"
        print(f"\n{C}Sublist3r çalıştırılıyor...{RESET}")
        # Run direkt çalıştırır, execute_commands'a gerek yok
        try:
             # Canlı çıktı için Popen daha iyi olabilir ama run basit
             subprocess.run(command, shell=True, check=False)
        except Exception as e:
             print(f"{R}Sublist3r çalıştırılırken hata: {e}{RESET}")
             return False
        return True

# --- Ana Koleksiyon ---
class WebAttackTools(HackingToolsCollection):
    TITLE = "Web Saldırı Araçları"
    DESCRIPTION = "Web uygulamaları için saldırı ve tarama araçları."
    TOOLS = [
        # Eklenecek veya çıkarılacak araçları buraya tanımla
        Web2Attack(),
        Skipfish(),
        SubDomainFinder()
        # Dirb, Blazy gibi diğer araçlar da buraya eklenebilir (kurulum/çalıştırma komutları ile)
        # Örnek:
        # Dirb(HackingTool): TITLE="Dirb", ... INSTALL_COMMANDS=["sudo apt install dirb"], RUN_COMMANDS=["dirb"]...
    ]

# --- Ana Çalıştırma Bloğu ---
if __name__ == '__main__':
    if not check_prerequisites(): # Temel araçlar var mı?
         sys.exit(1)
    try:
        WebAttackTools().show_options() # Ana koleksiyon menüsünü göster
    except KeyboardInterrupt:
        print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception as e:
        print(f"\n{R}Kritik hata: {e}{RESET}")
        traceback.print_exc() # Hata detayını göster
# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import shutil
from platform import system
from traceback import print_exc
from typing import List, Tuple, Callable, Any

# Renk tanımları
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
    BRIGHT = DIM = R = G = Y = B = M = C = W = RESET = ""
    class Style: BRIGHT = DIM = RESET_ALL = ""
    class Fore: RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""

def clear_screen():
    os.system("cls" if system() == "Windows" else "clear")

def pause():
    try:
        input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit()

def is_tool_installed(tool_name):
    return shutil.which(tool_name) is not None

class HackingTool:
    TITLE = "Başlıksız Araç"
    DESCRIPTION = "Açıklama Yok"
    INSTALL_COMMANDS = []
    INSTALLATION_DIR = ""
    UNINSTALL_COMMANDS = []
    RUN_COMMANDS = []
    OPTIONS = []
    PROJECT_URL = ""

    def __init__(self, options=None, installable=True, runnable=True):
        options = options or []
        self.OPTIONS = []
        if installable and self.INSTALL_COMMANDS:
            self.OPTIONS.append(('Install', self.install))
        if runnable or self.RUN_COMMANDS:
            self.OPTIONS.append(('Run', self.run))
        self.OPTIONS.extend(options)
        if self.UNINSTALL_COMMANDS:
            self.OPTIONS.append(('Uninstall', self.uninstall))

    def _execute_commands(self, command_list, target_dir=None):
        if not isinstance(command_list, (list, tuple)):
            print(f"{R}HATA: Komut listesi geçersiz.{RESET}")
            return False

        print(f"{C}--- Komutlar Çalıştırılıyor ---{RESET}")
        success = True
        effective_cwd = target_dir or self.INSTALLATION_DIR or None
        
        if effective_cwd and not os.path.isdir(effective_cwd):
            print(f"{Y}Uyarı: Hedef dizin '{effective_cwd}' mevcut değil.{RESET}")
            effective_cwd = None

        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            try:
                subprocess.run(command, shell=True, check=True, cwd=effective_cwd)
            except subprocess.CalledProcessError as e:
                print(f"{R}HATA: Komut hata ile sonlandı (Kod: {e.returncode}){RESET}")
                success = False
                break
            except Exception as e:
                print(f"{R}Beklenmedik hata: {e}{RESET}")
                success = False
                break

        status = f"{G}Başarılı{RESET}" if success else f"{R}Başarısız{RESET}"
        print(f"{C}--- Komutlar Tamamlandı ({status}) ---{RESET}")
        return success

    def show_info(self):
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        print(self.DESCRIPTION)
        if self.PROJECT_URL:
            print(f"\n{C}Proje Sayfası:{W} {self.PROJECT_URL}{RESET}")

    def show_options(self, parent=None):
        clear_screen()
        self.show_info()
        print(f"\n{Y}Seçenekler:{RESET}")
        
        for i, (name, _) in enumerate(self.OPTIONS, 1):
            print(f"  [{i}] {name}")

        print(f"  [98] Proje Sayfasını Aç" if self.PROJECT_URL else "", end="")
        parent_title = getattr(parent, 'TITLE', 'Ana Menü') if parent else 'Çıkış'
        print(f"  [99] Geri ({parent_title})")

        try:
            choice = int(input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip())
            if 1 <= choice <= len(self.OPTIONS):
                return self.OPTIONS[choice-1][1]()
            elif choice == 98 and self.PROJECT_URL:
                webbrowser.open(self.PROJECT_URL)
            elif choice == 99:
                return 99
            else:
                print(f"{R}Geçersiz seçenek!{RESET}")
        except (ValueError, KeyboardInterrupt):
            print(f"{R}Geçersiz giriş!{RESET}")
        
        pause()
        return self.show_options(parent)

    def install(self):
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")
        success = self._execute_commands(self.INSTALL_COMMANDS)
        print(f"\n{G}Kurulum tamamlandı!{RESET}" if success else f"\n{R}Kurulum başarısız!{RESET}")
        return success

    def run(self):
        if not self.RUN_COMMANDS:
            print(f"{Y}Bu araç için çalıştırma komutu tanımlanmamış.{RESET}")
            return False
            
        print(f"\n{C}{self.TITLE} çalıştırılıyor...{RESET}")
        success = self._execute_commands(self.RUN_COMMANDS)
        return success

    def uninstall(self):
        confirm = input(f"{Y}Emin misiniz? (e/H): {W}").lower()
        if confirm != 'e':
            return False
            
        print(f"\n{C}{self.TITLE} kaldırılıyor...{RESET}")
        success = self._execute_commands(self.UNINSTALL_COMMANDS)
        print(f"\n{G}Kaldırma tamamlandı!{RESET}" if success else f"\n{R}Kaldırma başarısız!{RESET}")
        return success

class HackingToolsCollection(HackingTool):
    TITLE = "Başlıksız Koleksiyon"
    DESCRIPTION = "Açıklama Yok"
    TOOLS = []

    def show_options(self, parent=None):
        clear_screen()
        print(f"\n{M}{BRIGHT}=== {self.TITLE} ==={RESET}")
        print(self.DESCRIPTION)
        print(f"\n{Y}Araçlar:{RESET}")
        
        for i, tool in enumerate(self.TOOLS, 1):
            print(f"  [{i}] {tool.TITLE}")

        parent_title = getattr(parent, 'TITLE', 'Ana Menü') if parent else 'Çıkış'
        print(f"  [99] Geri ({parent_title})")

        try:
            choice = int(input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip())
            if 1 <= choice <= len(self.TOOLS):
                tool = self.TOOLS[choice-1]
                while tool.show_options(parent=self) != 99:
                    pass
            elif choice == 99:
                return 99
            else:
                print(f"{R}Geçersiz seçenek!{RESET}")
        except (ValueError, KeyboardInterrupt):
            print(f"{R}Geçersiz giriş!{RESET}")
        
        return self.show_options(parent)

# Araç tanımları
class Web2Attack(HackingTool):
    TITLE = "Web2Attack Framework"
    DESCRIPTION = "Python ile yazılmış web saldırı framework'ü."
    INSTALLATION_DIR = "web2attack"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/santatic/web2attack.git {INSTALLATION_DIR}"
    ]
    RUN_COMMANDS = [f"cd {INSTALLATION_DIR} && python3 w2aconsole"]
    PROJECT_URL = "https://github.com/santatic/web2attack"

class Skipfish(HackingTool):
    TITLE = "Skipfish Web Scanner"
    DESCRIPTION = "Otomatik web uygulaması güvenlik keşif aracı."
    RUN_COMMANDS = ["skipfish -h"]

class SubDomainFinder(HackingTool):
    TITLE = "SubDomain Finder (Sublist3r)"
    DESCRIPTION = "Alt alan adlarını listelemek için OSINT aracı."
    INSTALLATION_DIR = "Sublist3r"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/aboul3la/Sublist3r.git {INSTALLATION_DIR}",
        f"pip install -r {INSTALLATION_DIR}/requirements.txt"
    ]
    PROJECT_URL = "https://github.com/aboul3la/Sublist3r"

    def run(self):
        domain = input(f"Hedef Domain: ").strip()
        if not domain:
            print(f"{R}Domain gerekli!{RESET}")
            return False
            
        cmd = f"python3 {self.INSTALLATION_DIR}/sublist3r.py -d {domain}"
        print(f"{Y}Çalıştırılıyor: {cmd}{RESET}")
        return self._execute_commands([cmd])

class WebAttackTools(HackingToolsCollection):
    TITLE = "Web Saldırı Araçları"
    DESCRIPTION = "Web uygulamaları için saldırı ve tarama araçları."
    TOOLS = [
        Web2Attack(),
        Skipfish(),
        SubDomainFinder()
    ]

if __name__ == '__main__':
    try:
        WebAttackTools().show_options()
    except KeyboardInterrupt:
        print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception as e:
        print(f"\n{R}Kritik hata: {e}{RESET}")
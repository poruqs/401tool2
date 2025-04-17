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

# --- UYARI ---
# Bu araçlar sadece etik hackleme ve güvenlik araştırmaları için kullanılmalıdır.
# Yasal olmayan şekillerde kullanımı kesinlikle yasaktır.
# --- UYARI SONU ---

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
        self.OPTIONS = []
        if installable and self.INSTALL_COMMANDS:
            self.OPTIONS.append(('Install', self.install))
        if runnable or self.RUN_COMMANDS:
            self.OPTIONS.append(('Run', self.run))
        if options:
            self.OPTIONS.extend(options)
        if self.UNINSTALL_COMMANDS:
            self.OPTIONS.append(('Uninstall', self.uninstall))

    def _execute_commands(self, command_list, target_dir=None):
        if not command_list:
            return False

        success = True
        for cmd in command_list:
            print(f"{Y}>> {cmd}{RESET}")
            try:
                subprocess.run(cmd, shell=True, check=True, cwd=target_dir)
            except Exception as e:
                print(f"{R}Hata: {e}{RESET}")
                success = False
                break
        return success

    def show_info(self):
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        print(self.DESCRIPTION)
        if self.PROJECT_URL:
            print(f"\n{C}Proje Sayfası: {self.PROJECT_URL}{RESET}")

    def show_options(self, parent=None):
        clear_screen()
        self.show_info()
        
        print(f"\n{Y}Seçenekler:{RESET}")
        for i, (name, _) in enumerate(self.OPTIONS, 1):
            print(f"  [{i}] {name}")

        if self.PROJECT_URL:
            print(f"  [98] Proje Sayfasını Aç")
        print(f"  [99] Geri")

        try:
            choice = input(f"\n{G}>> Seçiminiz: {W}").strip()
            if choice == "98" and self.PROJECT_URL:
                webbrowser.open(self.PROJECT_URL)
            elif choice == "99":
                return 99
            elif choice.isdigit() and 0 < int(choice) <= len(self.OPTIONS):
                func = self.OPTIONS[int(choice)-1][1]
                if func() != 99:
                    pause()
            else:
                print(f"{R}Geçersiz seçim!{RESET}")
                time.sleep(1)
        except Exception as e:
            print(f"{R}Hata: {e}{RESET}")
        
        return self.show_options(parent)

    def install(self):
        print(f"\n{C}Kurulum başlatılıyor...{RESET}")
        success = self._execute_commands(self.INSTALL_COMMANDS)
        print(f"\n{G}Kurulum tamamlandı!{RESET}" if success else f"\n{R}Kurulum başarısız!{RESET}")
        return success

    def run(self):
        if not self.RUN_COMMANDS:
            print(f"{Y}Çalıştırma komutu tanımlanmamış{RESET}")
            return False
            
        print(f"\n{C}Çalıştırılıyor...{RESET}")
        success = self._execute_commands(self.RUN_COMMANDS, self.INSTALLATION_DIR)
        return success

    def uninstall(self):
        if input(f"{Y}Emin misiniz? (e/H): {W}").lower() != 'e':
            return False
            
        print(f"\n{C}Kaldırılıyor...{RESET}")
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

        print(f"  [99] Geri")

        try:
            choice = input(f"\n{G}>> Seçiminiz: {W}").strip()
            if choice == "99":
                return 99
            elif choice.isdigit() and 0 < int(choice) <= len(self.TOOLS):
                tool = self.TOOLS[int(choice)-1]
                while tool.show_options(parent=self) != 99:
                    pass
            else:
                print(f"{R}Geçersiz seçim!{RESET}")
                time.sleep(1)
        except Exception as e:
            print(f"{R}Hata: {e}{RESET}")
        
        return self.show_options(parent)

# Araç Tanımları
class FacialFind(HackingTool):
    TITLE = "Sosyal Medya Bulucu (Yüz Tanıma)"
    DESCRIPTION = "Farklı platformlardaki profilleri yüz tanıma ile eşleştirir."
    INSTALLATION_DIR = "social_mapper"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/Greenwolf/social_mapper.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && pip install -r requirements.txt"
    ]
    PROJECT_URL = "https://github.com/Greenwolf/social_mapper"

    def run(self):
        print(f"{Y}Bu araç manuel kurulum gerektirir.{RESET}")
        print(f"{C}Detaylar için proje sayfasını ziyaret edin: {self.PROJECT_URL}{RESET}")
        return True

class FindUser(HackingTool):
    TITLE = "Kullanıcı Adı Bulucu"
    DESCRIPTION = "75+ platformda kullanıcı adı arar."
    INSTALLATION_DIR = "finduser"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/xHak9x/finduser.git {INSTALLATION_DIR}",
        f"chmod +x {INSTALLATION_DIR}/finduser.sh"
    ]
    RUN_COMMANDS = [f"./{INSTALLATION_DIR}/finduser.sh"]
    PROJECT_URL = "https://github.com/xHak9x/finduser"

class Sherlock(HackingTool):
    TITLE = "Sherlock"
    DESCRIPTION = "Çok sayıda sosyal ağda kullanıcı adı arar."
    INSTALLATION_DIR = "sherlock"
    INSTALL_COMMANDS = [
        f"git clone https://github.com/sherlock-project/sherlock.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && pip install -r requirements.txt"
    ]
    PROJECT_URL = "https://github.com/sherlock-project/sherlock"

    def run(self):
        username = input(f"{G}Aranacak kullanıcı adı: {W}").strip()
        if not username:
            print(f"{R}Kullanıcı adı gerekli!{RESET}")
            return False
            
        cmd = f"cd {self.INSTALLATION_DIR} && python3 sherlock {username}"
        return self._execute_commands([cmd])

class SocialScan(HackingTool):
    TITLE = "SocialScan"
    DESCRIPTION = "Kullanıcı adı/e-posta kullanılabilirliğini kontrol eder."
    INSTALL_COMMANDS = ["pip install socialscan"]
    RUN_COMMANDS = ["socialscan --help"]
    PROJECT_URL = "https://github.com/iojw/socialscan"

# Ana Koleksiyon
class SocialMediaFinderTools(HackingToolsCollection):
    TITLE = "Sosyal Medya Bulucu Araçlar"
    DESCRIPTION = "OSINT araçları ile sosyal medya profillerini bulma"
    TOOLS = [
        FacialFind(),
        FindUser(),
        Sherlock(),
        SocialScan()
    ]

if __name__ == '__main__':
    try:
        SocialMediaFinderTools().show_options()
    except KeyboardInterrupt:
        print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception as e:
        print(f"\n{R}Hata: {e}{RESET}")
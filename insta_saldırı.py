# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
from platform import system
from traceback import print_exc
from typing import List, Tuple, Callable, Any

# --- GÜVENLİK UYARISI ---
print("""\033[1;31m
=============================================
YASA DIŞI KULLANIMINDAN SORUMLUSU KULLANICIDIR!
İZİNSİZ KULLANIM YASA DIŞIDIR!
SADECE KENDİ HESAPLARINIZDA TEST YAPIN
=============================================\033[0m
""")
time.sleep(2)

# Renk tanımları
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    BRIGHT = Style.BRIGHT
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    C = Fore.CYAN
    W = Fore.WHITE
    RESET = Style.RESET_ALL
except ImportError:
    BRIGHT = R = G = Y = C = W = RESET = ""

def clear_screen():
    os.system("cls" if system() == "Windows" else "clear")

def is_tool_installed(tool):
    return subprocess.run(f"command -v {tool}", shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE).returncode == 0

class SecurityTool:
    TITLE = "Güvenlik Aracı"
    DESCRIPTION = "Temel açıklama"
    
    def __init__(self):
        self.options = [
            ('Bilgi Göster', self.show_info),
            ('Çıkış', sys.exit)
        ]
    
    def show_info(self):
        clear_screen()
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        print(self.DESCRIPTION)
        return True
    
    def run_tool(self):
        while True:
            clear_screen()
            print(f"\n{Y}{self.TITLE} - Seçenekler:{RESET}")
            for i, (name, _) in enumerate(self.options, 1):
                print(f"  [{i}] {name}")
            
            try:
                choice = input(f"\n{G}>> Seçiminiz: {W}").strip()
                if choice.isdigit() and 0 < int(choice) <= len(self.options):
                    self.options[int(choice)-1][1]()
                else:
                    print(f"{R}Geçersiz seçim!{RESET}")
                    time.sleep(1)
            except (KeyboardInterrupt, EOFError):
                print("\nÇıkılıyor...")
                sys.exit(0)
            except Exception as e:
                print(f"{R}Hata: {e}{RESET}")
                time.sleep(1)

class PasswordStrengthTester(SecurityTool):
    TITLE = "Şifre Güvenlik Test Aracı"
    DESCRIPTION = ("Kendi şifrelerinizin güvenliğini test edin\n"
                  f"{Y}Uyarı: Başkalarının şifrelerini test etmeyin!{RESET}")
    
    def __init__(self):
        super().__init__()
        self.options = [
            ('Şifre Test Et', self.test_password),
            ('Geri', lambda: False)
        ]
    
    def test_password(self):
        print(f"\n{C}Şifre güvenlik testi (kendi şifreleriniz için){RESET}")
        password = input("Test etmek istediğiniz şifre: ")
        
        # Basit güvenlik kontrolü
        strength = 0
        if len(password) >= 8: strength += 1
        if any(c.isupper() for c in password): strength += 1
        if any(c.islower() for c in password): strength += 1
        if any(c.isdigit() for c in password): strength += 1
        if any(c in '!@#$%^&*()' for c in password): strength += 1
        
        ratings = {
            0: f"{R}Çok Zayıf", 
            1: f"{R}Zayıf",
            2: f"{Y}Orta",
            3: f"{G}Güçlü",
            4: f"{G}Çok Güçlü",
            5: f"{G}Mükemmel"
        }
        
        print(f"\nŞifre gücü: {ratings.get(strength, 'Bilinmiyor')}{RESET}")
        pause()
        return True

class EthicalToolsCollection:
    def __init__(self):
        self.tools = [
            PasswordStrengthTester()
        ]
    
    def show_menu(self):
        while True:
            clear_screen()
            print(f"\n{Y}{BRIGHT}ETİK GÜVENLİK ARAÇLARI{RESET}")
            print(f"{C}Sadece yasal ve etik sınırlar içinde kullanın{RESET}")
            
            for i, tool in enumerate(self.tools, 1):
                print(f"  [{i}] {tool.TITLE}")
            print("  [99] Çıkış")
            
            try:
                choice = input(f"\n{G}>> Seçiminiz: {W}").strip()
                if choice == "99":
                    print("\nÇıkılıyor...")
                    sys.exit(0)
                elif choice.isdigit() and 0 < int(choice) <= len(self.tools):
                    self.tools[int(choice)-1].run_tool()
                else:
                    print(f"{R}Geçersiz seçim!{RESET}")
                    time.sleep(1)
            except (KeyboardInterrupt, EOFError):
                print("\nÇıkılıyor...")
                sys.exit(0)
            except Exception as e:
                print(f"{R}Hata: {e}{RESET}")
                time.sleep(2)

if __name__ == '__main__':
    try:
        EthicalToolsCollection().show_menu()
    except KeyboardInterrupt:
        print("\nProgram sonlandırıldı")
        sys.exit(0)
    except Exception as e:
        print(f"\n{R}Kritik hata: {e}{RESET}")
        sys.exit(1)
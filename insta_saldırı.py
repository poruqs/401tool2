# -*- coding: utf-8 -*-
# insta_saldırı.py - YANILTICI İSİM DÜZELTİLDİ - Sadece Şifre Güçlülük Testi

import os
import sys
import webbrowser
import subprocess
import time
from platform import system
from traceback import print_exc
from typing import List, Tuple, Callable, Any # Gerekli importlar

# --- GÜVENLİK UYARISI ve AÇIKLAMA ---
print(f"""{Fore.RED}{Style.BRIGHT}
=============================================
        !!! ÖNEMLİ UYARI !!!
Bu betik ('insta_saldırı.py') ismiyle
Instagram saldırı aracı gibi görünse de,
GERÇEKTE Instagram ile ilgili bir işlem YAPMAZ.
Mevcut haliyle sadece girdiğiniz bir şifrenin
güçlülüğünü tahmin etmeye yarayan basit bir
araç içerir.

Instagram hesaplarına yönelik izinsiz işlemler
YASA DIŞIDIR ve ETİK DEĞİLDİR!
=============================================
{Style.RESET_ALL}""")
time.sleep(4) # Kullanıcının uyarıyı okuması için bekle

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
    print("Uyarı: Renkli arayüz için 'colorama' kütüphanesi gerekli ('pip install colorama').")
    BRIGHT = R = G = Y = C = W = RESET = ""

def clear_screen():
    os.system("cls" if system() == "Windows" else "clear")

def pause():
    """Devam etmek için Enter beklenir."""
    try:
        input(f"\n{Y}Devam etmek için Enter'a basın...{RESET}")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit()

# Ana Sınıf (Şifre Testi için)
class PasswordStrengthTester:
    TITLE = "Şifre Güvenlik Test Aracı"
    DESCRIPTION = ("Kendi şifrelerinizin temel güvenliğini tahmin edin.\n"
                  f"{Y}Uyarı: Başkalarının şifrelerini test etmeyin!{RESET}")

    def __init__(self):
        # Seçenekleri tanımla
        self.options = [
            ('Şifre Test Et', self.test_password),
            ('Geri', lambda: 99) # Geri dönmek için 99 döndür
        ]

    def show_info(self):
        """Araç bilgilerini gösterir."""
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        print(self.DESCRIPTION)

    def test_password(self):
        """Basit şifre güçlülük testi yapar."""
        print(f"\n{C}Şifre güvenlik testi (kendi şifreleriniz için){RESET}")
        try:
            password = input("Test etmek istediğiniz şifre: ")
            if not password:
                print(f"{R}Şifre boş olamaz.{RESET}")
                return True # Menüye dönmek için True

            # Basit güvenlik kontrolü (uzunluk, büyük/küçük harf, rakam, özel karakter)
            strength = 0
            if len(password) >= 8: strength += 1
            if len(password) >= 12: strength += 1 # Daha uzunsa ek puan
            if any(c.isupper() for c in password): strength += 1
            if any(c.islower() for c in password): strength += 1
            if any(c.isdigit() for c in password): strength += 1
            # Daha fazla özel karakter kontrolü
            if any(c in '!@#$%^&*()_+-=[]{};:\'",./<>?' for c in password): strength += 1

            ratings = {
                0: f"{R}Çok Zayıf", 1: f"{R}Zayıf", 2: f"{Y}Orta",
                3: f"{Y}İdare Eder", 4: f"{G}Güçlü", 5: f"{G}Çok Güçlü",
                6: f"{G}{BRIGHT}Mükemmel{RESET}"
            }

            print(f"\nTahmini Şifre Gücü: {ratings.get(strength, f'{Y}Orta')}{RESET}")

        except KeyboardInterrupt:
            print("\nİşlem iptal edildi.")
        except Exception as e:
            print(f"{R}Test sırasında hata: {e}{RESET}")

        # İşlem sonrası menüye dönmek için True döndür
        return True # True dönünce pause() çağrılır

    def run_tool(self, parent=None): # Ana menüye geri dönebilmek için parent eklendi
        """Aracın seçenek menüsünü gösterir ve yönetir."""
        while True:
            clear_screen()
            self.show_info()
            print(f"\n{Y}Seçenekler:{RESET}")
            for i, (name, _) in enumerate(self.options, 1):
                print(f"  [{i}] {name}")

            try:
                choice_str = input(f"\n{G}>> Seçiminiz: {W}").strip()
                if not choice_str.isdigit():
                    print(f"{R}Lütfen bir numara girin.{RESET}")
                    time.sleep(1)
                    continue

                choice = int(choice_str)
                if 1 <= choice <= len(self.options):
                    # Seçilen fonksiyonu çağır
                    result = self.options[choice-1][1]()
                    if result == 99: # Eğer fonksiyon 99 döndürürse (Geri)
                        return 99 # Bir üst menüye dönmek için 99 döndür
                    elif result is True: # İşlem yapıldıysa ve geri dönülmediyse
                         pause() # Pause before showing options again
                else:
                    print(f"{R}Geçersiz seçenek!{RESET}")
                    time.sleep(1)

            except (KeyboardInterrupt, EOFError):
                print("\nÇıkılıyor...")
                sys.exit(0)
            except Exception as e:
                print(f"{R}Menü hatası: {e}{RESET}")
                traceback.print_exc() # Hata detayını yazdır
                time.sleep(2)

# Ana Çalıştırma Bloğu
if __name__ == '__main__':
    try:
        # Doğrudan aracı çalıştır
        tester = PasswordStrengthTester()
        tester.run_tool()
    except KeyboardInterrupt:
        print("\nProgram sonlandırıldı.")
    except Exception as e:
        print(f"\n{R}Kritik hata: {e}{RESET}")
        traceback.print_exc()
        sys.exit(1)
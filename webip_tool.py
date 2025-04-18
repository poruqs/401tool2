#!/usr/bin/env python3
import socket
import sys
import ipaddress # IP format kontrolü için

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
    BLUE = Fore.BLUE # Menü için
    HEADER = Fore.MAGENTA # Başlık için
except ImportError:
    R = Y = G = C = RESET = ""
    BLUE = HEADER = ""


def ip_to_site():
    while True:
        ip_input = input(f"\n{Y}IP adresi girin (örn: 8.8.8.8): {RESET}").strip()
        if not ip_input: continue # Boş girişi atla
        try:
            # Girilenin geçerli bir IP adresi olup olmadığını kontrol et
            ipaddress.ip_address(ip_input)
            break # Geçerliyse döngüden çık
        except ValueError:
            print(f"{R}Hata: Geçersiz IP adresi formatı! Tekrar deneyin.{RESET}")

    print(f"{C}Ana makine adı (hostname) aranıyor...{RESET}")
    try:
        # gethostbyaddr IP'ye karşılık gelen ana makine adını bulur
        # Dönen tuple'ın ilk elemanı genellikle hostname'dir.
        hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip_input)
        print(f"\n{G}✅ Ana Makine Adı (Hostname): {hostname}{RESET}")
        # Genellikle ana hostname web sitesi adıdır ama garanti değildir.
        # Kullanıcıya farklı olasılıkları sunabiliriz:
        print(f"   🔗 Olası Web Adresi: http://{hostname}")
        if aliaslist:
            print(f"   ℹ️ Diğer İsimler (Alias): {', '.join(aliaslist)}")
    except socket.herror as e:
        # Hostname bulunamadığında (DNS'te PTR kaydı yoksa vb.)
        print(f"\n{R}❌ Ana makine adı bulunamadı!{RESET}")
        print(f"{R}   Detay: {e}{RESET}")
    except socket.gaierror as e:
        # Genel adres/isim çözümleme hatası
         print(f"\n{R}❌ Adres çözümleme hatası!{RESET}")
         print(f"{R}   Detay: {e}{RESET}")
    except Exception as e:
        print(f"\n{R}❌ Beklenmedik bir hata oluştu: {e}{RESET}")


def site_to_ip():
    while True:
        site_input = input(f"\n{Y}Site adresi girin (örn: google.com): {RESET}").strip()
        if not site_input: continue
        # Kullanıcı http/https eklemişse veya www varsa kaldıralım (gethostbyname için gereksiz)
        site = site_input.replace("https://", "").replace("http://", "").split('/')[0] # Sadece domain kısmı
        if not site:
             print(f"{R}Hata: Geçerli bir site adı girin.{RESET}")
             continue
        break

    print(f"{C}IP adresi aranıyor...{RESET}")
    try:
        # gethostbyname domain adına karşılık gelen IP adresini bulur
        ip_address = socket.gethostbyname(site)
        print(f"\n{G}✅ IP Adresi: {ip_address}{RESET}")

        # Ek olarak tüm IP adreslerini bulmayı deneyebiliriz (IPv4/IPv6)
        try:
            print(f"{C}Tüm adres bilgileri alınıyor (getaddrinfo)...{RESET}")
            # AF_UNSPEC hem IPv4 hem IPv6 için sonuçları getirir
            results = socket.getaddrinfo(site, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            unique_ips = set()
            for res in results:
                # family, type, proto, canonname, sockaddr
                # sockaddr bir tuple'dır, ilk elemanı IP adresidir
                ip = res[4][0]
                unique_ips.add(ip)
            if unique_ips:
                 print(f"   ℹ️ Bulunan Tüm IP Adresleri: {', '.join(unique_ips)}")
        except socket.gaierror:
            print(f"{Y}   Uyarı: Tüm adres bilgileri (getaddrinfo) alınamadı.{RESET}")
        except Exception as e_extra:
             print(f"{Y}   Uyarı: Ek adres bilgisi alınırken hata: {e_extra}{RESET}")

    except socket.gaierror as e:
        # Domain adı çözümlenemezse
        print(f"\n{R}❌ IP adresi bulunamadı veya site adı geçersiz!{RESET}")
        print(f"{R}   Detay: {e}{RESET}")
    except Exception as e:
         print(f"\n{R}❌ Beklenmedik bir hata oluştu: {e}{RESET}")


# Ana Menü ve Döngü
def main():
    while True:
        print(f"""{HEADER}
        ╔══════════════════════════╗
        ║    IP <-> SITE DÖNÜŞTÜRÜCÜ   ║
        ╠══════════════════════════╣{BLUE}
        ║ 1. IP'den Site Bul       ║
        ║ 2. Siteden IP Bul        ║{HEADER}
        ║                          ║
        ║ 0. Çıkış                 ║
        ╚══════════════════════════╝
        {RESET}""")

        secim = input(f"{Y}Seçim (1/2/0): {RESET}").strip()

        try:
            if secim == "1":
                ip_to_site()
            elif secim == "2":
                site_to_ip()
            elif secim == "0":
                print(f"\n{G}Çıkış yapılıyor...{RESET}")
                break
            else:
                print(f"\n{R}Geçersiz seçim! Lütfen 0, 1 veya 2 girin.{RESET}")
        except KeyboardInterrupt:
             print(f"\n{G}Çıkış yapılıyor...{RESET}")
             break
        except Exception as e:
             print(f"\n{R}Ana döngüde hata: {e}{RESET}")

        # Her işlemden sonra bekleyelim
        try:
            input(f"\n{C}Devam etmek için Enter'a basın...{RESET}")
        except KeyboardInterrupt:
             print(f"\n{G}Çıkış yapılıyor...{RESET}")
             break

if __name__ == "__main__":
    main()
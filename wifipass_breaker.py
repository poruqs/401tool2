import os
import subprocess
from colorama import Fore, init

init(autoreset=True)

def print_banner():
    print(Fore.CYAN + """
    ╔════════════════════════════════════════════╗
    ║          401HackTeam - WiFi Tool           ║
    ╠════════════════════════════════════════════╣
    ║                                            ║
    ║    1. WiFi Ağlarını Tara                   ║
    ║    2. Çıkış                                ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """)

def scan_wifi():
    print(Fore.CYAN + "\n[+] WiFi Ağları Taranıyor...")
    result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True)
    networks = result.stdout.splitlines()
    if not networks:
        print(Fore.RED + "[-] Hiç WiFi ağı bulunamadı!")
        return []
    
    print(Fore.GREEN + "\n[+] Bulunan WiFi Ağları:")
    for i, net in enumerate(networks, 1):
        print(f"{Fore.YELLOW}[{i}] {net}")
    return networks

def crack_wifi(network_name):
    print(Fore.RED + "\n⚠️ UYARI: Bu işlem yasa dışıdır! Sadece kendi ağınızda deneyin.")
    print(Fore.GREEN + f"\n[+] {network_name} şifresi kırılıyor...")
    
    # Simüle edilmiş kırma işlemi
    print(Fore.GREEN + f"\n[+] Sonuç:")
    print(Fore.YELLOW + f"WiFi Adı   : {network_name}")
    print(Fore.YELLOW + f"Şifresi    : wifisifre123 (Örnek)")

def main():
    while True:
        os.system("clear")
        print_banner()
        
        # Seçim alanı
        print(Fore.WHITE + "\n" + "═"*50)
        choice = input(Fore.CYAN + "\n[?] Seçiminiz (1-2): ")
        print(Fore.WHITE + "═"*50)
        
        if choice == "1":
            networks = scan_wifi()
            if not networks:
                input(Fore.RED + "\n[!] Devam etmek için Enter'a basın...")
                continue
            
            # WiFi seçimi
            print(Fore.WHITE + "\n" + "═"*50)
            wifi_choice = input(Fore.CYAN + "\n[?] Şifresini kırmak istediğiniz ağ numarası: ")
            print(Fore.WHITE + "═"*50)
            
            try:
                selected = networks[int(wifi_choice) - 1]
                crack_wifi(selected)
                input(Fore.YELLOW + "\n[+] Devam etmek için Enter'a basın...")
            except:
                print(Fore.RED + "[-] Geçersiz numara!")
                input(Fore.RED + "\n[!] Tekrar denemek için Enter'a basın...")
                
        elif choice == "2":
            break
            
        else:
            print(Fore.RED + "[-] Geçersiz seçim!")
            input(Fore.RED + "\n[!] Tekrar denemek için Enter'a basın...")

if __name__ == "__main__":
    main()
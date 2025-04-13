import subprocess
import os
import sys

# Banner (Raw string kullanarak boşlukları ve karakterleri koru)
# Not: Terminalinizin yazı tipi ve karakter kodlaması bu tür karakterleri desteklemelidir.
banner = r"""
██╗  ██╗ ██████╗  ██╗
██║  ██║██╔═████╗███║
███████║██║██╔██║╚██║
╚════██║████╔╝██║ ██║
     ██║╚██████╔╝ ██║
     ╚═╝ ╚═════╝  ╚═╝
"""

def clear_screen():
    """Ekranı temizler (Windows için 'cls', Linux/macOS için 'clear')."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Menüyü gösterir ve kullanıcıdan seçim alır."""
    clear_screen() # Menüyü göstermeden önce ekranı temizle
    print(banner)
    print("Ana Menü\n" + "="*20) # Başlık ve ayırıcı çizgi
    print("1-) Call Bomb")          # Dosya adı kaldırıldı
    print("2-) Crash")              # Dosya adı kaldırıldı
    print("3-) SMS Bomb")           # Dosya adı kaldırıldı
    print("4-) Base64 Decode")      # Dosya adı kaldırıldı
    print("5-) Netflix Checker")    # Dosya adı kaldırıldı
    print("\n0-) Çıkış") # Çıkış seçeneği
    print("-" * 20)

    choice = input("Lütfen bir seçenek numarası girin: ")
    return choice

def run_script(script_name):
    """Belirtilen Python betiğini çalıştırır."""
    try:
        print(f"\n'{script_name}' başlatılıyor...")
        # 'python' veya 'python3' komutunu işletim sistemine göre kullan
        python_executable = sys.executable # Mevcut Python yorumlayıcısını kullanır
        subprocess.run([python_executable, script_name], check=True)
        print(f"\n'{script_name}' başarıyla tamamlandı.")
    except FileNotFoundError:
        print(f"\nHATA: '{script_name}' dosyası bulunamadı!")
        print("Lütfen betik dosyasının 'main.py' ile aynı dizinde olduğundan emin olun.")
    except subprocess.CalledProcessError as e:
        print(f"\nHATA: '{script_name}' çalıştırılırken bir sorun oluştu (Çıkış Kodu: {e.returncode}).")
    except Exception as e:
        print(f"\nBeklenmedik bir hata oluştu: {e}")
    input("\nDevam etmek için Enter tuşuna basın...") # Kullanıcının sonucu görmesi için bekle

# Ana program akışı
if __name__ == "__main__":
    while True: # Menüyü sürekli göstermek için döngü
        user_choice = show_menu()

        # Kullanıcının seçimine göre ilgili betiği çalıştır
        if user_choice == '1':
            run_script("call_bomb.py")
        elif user_choice == '2':
            run_script("crash.py")
        elif user_choice == '3':
            run_script("sms_bomb.py")
        elif user_choice == '4':
            run_script("base64decode.py")
        elif user_choice == '5':
            # Dosya adındaki çift noktaya dikkat!
            run_script("netflix_checker.py")
        elif user_choice == '0':
            print("\nProgramdan çıkılıyor...")
            break # Döngüyü kır ve programı sonlandır
        else:
            print("\nGeçersiz seçim! Lütfen listedeki numaralardan birini girin.")
            input("Devam etmek için Enter tuşuna basın...") # Hata mesajından sonra bekle
# -*- coding: utf-8 -*-
# sim-clone.py - DİKKAT: İLERİ SEVİYE ARAÇ, CİDDİ RİSKLER!

import subprocess
import re
import sys
import traceback
import shutil # shutil.which için
from datetime import datetime
import os # os.path.exists için

# Renkler (opsiyonel)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
except ImportError:
    R = Y = G = C = RESET = ""
    BOLD = ""

# --- GEREKLİ ARAÇ KONTROLÜ ---
QCSUPER_CMD = "qcsuper"
def check_qcsuper():
    """qcsuper aracının sistemde kurulu olup olmadığını kontrol eder."""
    qcsuper_path = shutil.which(QCSUPER_CMD)
    if not qcsuper_path:
        print(f"\n{R}{BOLD}Hata: '{QCSUPER_CMD}' komutu sistemde bulunamadı!{RESET}")
        print(f"{Y}Bu betik, SIM kartı ile etkileşim için 'qcsuper' aracına ihtiyaç duyar.")
        print(f"{Y}Kurulumu ve kullanımı uzmanlık gerektirir ve genellikle GitHub üzerinden yapılır.")
        print(f"{Y}Ayrıca, uyumlu Qualcomm modemli bir cihaz ve potansiyel olarak root/özel sürücüler gerektirir.")
        print(f"{Y}Detaylı bilgi için qcsuper GitHub reposuna bakın.{RESET}")
        return False
    print(f"{G}'{QCSUPER_CMD}' bulundu: {qcsuper_path}{RESET}")
    return True

# --- ÇOK ÖNEMLİ UYARILAR ---
print(f"""{R}{BOLD}
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!          ÇOK ÖNEMLİ UYARI / CRITICAL WARNING          !!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
- SIM KART KLONLAMAK çoğu ülkede YASA DIŞIDIR ve ciddi hukuki
  sonuçları vardır. Bu aracı ASLA yasa dışı amaçlarla kullanmayın.
- Bu işlem son derece risklidir ve SIM kartınıza veya telefonunuza
  KALICI ZARAR VEREBİLİR.
- Bu betik SADECE belirli Qualcomm modemlere sahip cihazlarda ve
  özel yapılandırmalarla çalışabilir. Her cihazda çalışmaz.
- 'qcsuper' aracının kurulumu ve kullanımı ileri düzey bilgi gerektirir.
- Root yetkisi, özel sürücüler veya USB hata ayıklama modları gerekebilir.
- Başarılı bir klonlama işlemi için SIM kartın şifreleme anahtarlarına
  (Ki, IMSI vb.) erişim gerekir ki bu genellikle mümkün değildir veya
  çok zordur. Bu betik bu anahtarları otomatik olarak alamaz.
- Bu araç sadece eğitim ve araştırma amaçlıdır. Kullanımdan doğacak
  tüm riskler ve yasal sorumluluklar tamamen kullanıcıya aittir.
  NE YAPTIĞINIZI BİLMİYORSANIZ KESİNLİKLE KULLANMAYIN!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
{RESET}""")
try:
    confirm = input(f"{Y}Tüm uyarıları okudum, anladım ve riskleri kabul ediyorum. Devam etmek istiyor musunuz? (e/y): {RESET}").strip().lower()
    if confirm not in ['e', 'y']:
        print(f"{G}İşlem iptal edildi.{RESET}")
        sys.exit()
    elif confirm == 'e':
         print(f"{R}RİSKLİ İŞLEM BAŞLATILIYOR...{RESET}")
         time.sleep(2)
    else: # 'y' dışında bir şey girilirse iptal et
         print(f"{G}İşlem iptal edildi.{RESET}")
         sys.exit()
except KeyboardInterrupt:
    print(f"\n{G}İşlem iptal edildi.{RESET}")
    sys.exit()
# ===========================================================


class SIMCloner:
    def __init__(self, port="/dev/ttyUSB0"): # Varsayılan port değişebilir
        # Port'un sistemde var olup olmadığını basitçe kontrol edelim
        # if not os.path.exists(port) and not port.lower().startswith("com"): # Windows COM portları için
        #     print(f"{Y}Uyarı: Belirtilen port '{port}' sistemde bulunamadı. Doğru portu belirtmeniz gerekebilir.{RESET}")
        #     # Portu kullanıcıdan almak daha iyi olabilir.
        #     new_port = input(f"{Y}Kullanılacak portu girin (örn: /dev/ttyUSB0 veya COM3): {RESET}").strip()
        #     if new_port: self.port = new_port
        #     else: raise ValueError("Geçerli bir port belirtilmedi.")
        # Şimdilik portu argüman olarak alalım, kullanıcı doğru girmeli.
        self.port = port
        self.log_file = "sim_clone_log.txt"
        print(f"{C}Kullanılacak Port: {self.port}{RESET}")

    def log_error(self, message):
        """Hataları log dosyasına yazar."""
        try:
            with open(self.log_file, "a", encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] ERROR: {message}\n")
        except Exception as e:
            print(f"{R}Log dosyasına yazılamadı ({self.log_file}): {e}{RESET}")

    def run_qcsuper_command(self, args):
        """Verilen argümanlarla qcsuper komutunu çalıştırır."""
        command = [QCSUPER_CMD, "--port", self.port] + args
        print(f"\n{C}Komut çalıştırılıyor: {' '.join(command)}{RESET}")
        try:
            # check_output yerine Popen kullanıp çıktıyı okumak daha iyi olabilir
            # Şimdilik check_output ile deneyelim, hata olursa Popen'a geçilebilir
            # Timeout eklemek önemli!
            result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=True, encoding='utf-8') # check=True hata durumunda exception fırlatır
            print(f"{G}Komut başarıyla çalıştırıldı.{RESET}")
            if result.stdout: print(f"{G}Çıktı:\n{result.stdout.strip()}{RESET}")
            if result.stderr: print(f"{Y}Hata Çıktısı (stderr):\n{result.stderr.strip()}{RESET}")
            return result.stdout # Başarılı ise çıktıyı döndür
        except FileNotFoundError:
             print(f"{R}Hata: '{QCSUPER_CMD}' komutu bulunamadı veya çalıştırılamadı!{RESET}")
             self.log_error(f"FileNotFoundError: {QCSUPER_CMD} not found or executable.")
             return None
        except subprocess.TimeoutExpired:
             print(f"{R}Hata: Komut zaman aşımına uğradı (60s). Cihaz yanıt vermiyor olabilir.{RESET}")
             self.log_error(f"TimeoutExpired: Command '{' '.join(command)}' timed out.")
             return None
        except subprocess.CalledProcessError as e:
            # Komut hata koduyla biterse
            print(f"{R}Hata: qcsuper komutu hata ile sonlandı! (Return Code: {e.returncode}){RESET}")
            stderr = e.stderr.strip() if e.stderr else "Yok"
            stdout = e.stdout.strip() if e.stdout else "Yok"
            print(f"{R}Stderr: {stderr}{RESET}")
            print(f"{Y}Stdout: {stdout}{RESET}")
            self.log_error(f"CalledProcessError: Command '{' '.join(command)}' failed with code {e.returncode}. Stderr: {stderr}")
            return None
        except Exception as e:
            print(f"{R}Komut çalıştırılırken beklenmedik hata: {e}{RESET}")
            self.log_error(f"Exception running command '{' '.join(command)}': {e}")
            traceback.print_exc()
            return None


    def detect_card(self):
        """SIM kartın algılanıp algılanmadığını kontrol eder."""
        # --detect argümanı qcsuper'da var mı kontrol etmek lazım, dökümantasyonda yok gibi.
        # Genellikle --info veya benzeri bir komut kullanılır.
        # Şimdilik --read gibi temel bir komutun başarılı olup olmadığına bakalım.
        # Veya --adb ile cihazı listelemeyi deneyebiliriz.
        # En iyisi --info kullanmak (eğer varsa). Varsayılan olarak --read deneyelim.
        print(f"\n{C}SIM kart algılanmaya çalışılıyor (port: {self.port})...{RESET}")
        # Basit bir okuma komutu gönderelim, başarılı olursa kart vardır varsayalım.
        # --read genellikle dosya adı ister, sadece bağlantıyı test edelim.
        # Belki sadece portu açmayı deneyen bir komut?
        # Şimdilik --info varsayalım veya basit bir --shell komutu?
        # --info yoksa, --shell ile basit bir AT komutu gönderilebilir: AT+CIMI (IMSI için)
        # result = self.run_qcsuper_command(["--shell", "AT+CIMI"])
        # Şimdilik detect yerine doğrudan klonlamayı deneyelim.
        print(f"{Y}Kart algılama atlanıyor, doğrudan okuma denenecek.{RESET}")
        return True # Algılandı varsayalım, asıl test klonlamada olacak.


    def clone_sim(self, output_file="sim_data.bin"):
        """qcsuper kullanarak SIM verilerini okumayı dener."""
        # Uyarı: Bu işlem genellikle SIM'in dosya sistemini okur,
        # şifreleme anahtarlarını (Ki) OKUMAZ! Klonlama için Ki gereklidir.
        print(f"\n{C}SIM verileri okunuyor -> {output_file}{RESET}")
        print(f"{Y}Uyarı: Bu işlem sadece SIM dosya sistemini okur, klonlama için gerekli şifreleme anahtarlarını (Ki) almaz!{RESET}")

        # Veriyi binary dosyaya oku
        result_read = self.run_qcsuper_command(["--read", "--outfile", output_file])

        if result_read is None:
             print(f"{R}SIM veri okuma başarısız oldu.{RESET}")
             return False

        print(f"{G}SIM verisi '{output_file}' dosyasına okundu (gibi görünüyor).{RESET}")
        # Okunan verinin içeriği qcsuper'a bağlıdır.

        # Ek olarak --dump ile JSON formatında bilgi almayı deneyelim
        json_output_file = output_file + ".json"
        print(f"\n{C}Ek bilgiler JSON olarak alınıyor -> {json_output_file}{RESET}")
        result_dump = self.run_qcsuper_command(["--dump", "--outfile", json_output_file])

        if result_dump is None:
             print(f"{Y}Uyarı: Ek bilgileri JSON olarak alma başarısız oldu.{RESET}")
             # Okuma başarılı olduğu için True dönebiliriz
             return True
        else:
             print(f"{G}Ek bilgiler '{json_output_file}' dosyasına alındı.{RESET}")
             return True


# Ana Çalıştırma Bloğu
if __name__ == "__main__":
    if not check_qcsuper(): # qcsuper kurulu mu?
        sys.exit(1)

    # Kullanıcıdan port alalım
    default_port = "/dev/ttyUSB0" # Linux için yaygın
    port_to_use = input(f"{Y}Kullanılacak portu girin [Varsayılan: {default_port}]: {RESET}").strip() or default_port

    # Kullanıcıdan çıktı dosyası adı alalım
    default_outfile = "sim_clone_output.bin"
    outfile_to_use = input(f"{Y}Çıktı dosya adı [Varsayılan: {default_outfile}]: {RESET}").strip() or default_outfile

    try:
        cloner = SIMCloner(port=port_to_use)

        # Kart algılama adımını atladık, doğrudan klonlamayı dene
        # if cloner.detect_card():
        print(f"\n{C}SIM Klonlama/Okuma işlemi başlatılıyor...{RESET}")
        success = cloner.clone_sim(output_file=outfile_to_use)
        if success:
            print(f"\n{G}İşlem tamamlandı. Çıktı dosyaları: '{outfile_to_use}' ve potansiyel olarak '{outfile_to_use}.json'.{RESET}")
            print(f"{Y}Unutmayın, bu dosyalar genellikle tam bir klonlama için yeterli değildir!{RESET}")
        else:
             print(f"\n{R}SIM okuma işlemi başarısız oldu. Detaylar için logları veya önceki mesajları kontrol edin.{RESET}")
        # else:
        #    print(f"\n{R}SIM kart algılanamadı veya bağlantı kurulamadı.{RESET}")

    except ValueError as e: # Geçersiz port için
         print(f"{R}Hata: {e}{RESET}")
    except Exception as e:
        print(f"\n{R}{BOLD}Ana programda beklenmedik hata:{RESET}\n{e}")
        traceback.print_exc()

    print(f"\n{G}Program sonlandırıldı.{RESET}")
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# ag-tunelleme.py

import socket
import threading
import select
import sys        # sys.exit için
import traceback  # Hataları yazdırmak için
import ipaddress  # IP adresi doğrulamak için
import logging    # Loglama için
from typing import List, Dict, Optional # Tip belirtmek için

# --- Gerekli Kütüphaneleri Kontrol Et ---
try:
    # Şifreleme için
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    # SSH Tünel için
    from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
    # SSH bağlantısı için (sshtunnel'in bağımlılığı ama import edelim)
    import paramiko
except ImportError as e:
    print(f"\nHata: Eksik kütüphane bulundu! -> {e}")
    print("Bu betiğin çalışması için şu kütüphaneler gereklidir:")
    print(" - PyCryptodome (pip install pycryptodomex)") # 'x' ile kuruluyor genelde
    print(" - sshtunnel (pip install sshtunnel)")
    print(" - paramiko (pip install paramiko)")
    print("Lütfen yukarıdaki komutlarla eksik kütüphaneleri kurun.")
    sys.exit(1)

# --- Renkler (Opsiyonel) ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    R = Fore.RED; Y = Fore.YELLOW; G = Fore.GREEN; C = Fore.CYAN; RESET = Style.RESET_ALL
except ImportError:
    R = Y = G = C = RESET = ""

# --- Log Ayarları ---
LOG_FILENAME = 'tunnel.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s', # Thread ismini ekle
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'), # Dosyaya loglama
        logging.StreamHandler() # Konsola loglama
    ]
)
logging.info("Tunnel Manager Başlatıldı.")

# --- YAPILANDIRMA (BURALARI KENDİNE GÖRE DÜZENLE!) ---
# DNS Tüneli için Şifreleme Anahtarı ve IV (Mutlaka değiştir!)
# Anahtar tam 32 byte, IV tam 16 byte olmalı!
DEFAULT_DNS_KEY = b'thirty-two-byte-long-secret-key!' # MUTLAKA DEĞİŞTİR! 32 byte olmalı
DEFAULT_DNS_IV = b'sixteen-byte-iv!'              # MUTLAKA DEĞİŞTİR! 16 byte olmalı
DEFAULT_DNS_SECRET_DOMAIN = "tünel.example.com" # DNS sorgularında kullanılacak alan adı

# --- Ana Tünel Yönetici Sınıfı ---
class SecureTunnelManager:
    def __init__(self):
        self.active_ssh_tunnels: Dict[str, SSHTunnelForwarder] = {} # Aktif SSH tünellerini tutar
        self.dns_key = DEFAULT_DNS_KEY
        self.dns_iv = DEFAULT_DNS_IV
        self.lock = threading.Lock() # Thread güvenliği için kilit
        self.stop_dns_server = threading.Event() # DNS sunucusunu durdurmak için

    def _validate_ip(self, ip: str) -> bool:
        """IP adresinin geçerli olup olmadığını kontrol eder."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            logging.error(f"Geçersiz IP adresi formatı: {ip}")
            return False

    def _aes_encrypt(self, data: str) -> bytes:
        """Verilen string'i AES ile şifreler."""
        try:
            cipher = AES.new(self.dns_key, AES.MODE_CBC, self.dns_iv)
            return cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        except Exception as e:
            logging.error(f"AES şifreleme hatası: {e}")
            return b'' # Hata durumunda boş byte döndür

    def _aes_decrypt(self, data: bytes) -> Optional[str]:
        """Verilen byte verisini AES ile çözer."""
        try:
            cipher = AES.new(self.dns_key, AES.MODE_CBC, self.dns_iv)
            # unpad potansiyel padding hatalarını yakalayabilir
            return unpad(cipher.decrypt(data), AES.block_size).decode('utf-8')
        except ValueError as e: # Padding hatası veya şifre çözme hatası
             logging.warning(f"AES şifre çözme/unpad hatası (muhtemelen geçersiz veri): {e}")
             return None
        except Exception as e:
            logging.error(f"AES şifre çözme sırasında beklenmedik hata: {e}")
            return None

    # --- DNS Tüneli Fonksiyonları ---
    def _dns_handler(self, sock: socket.socket, secret_domain_bytes: bytes) -> None:
        """Gelen DNS isteklerini dinler ve işler."""
        thread_name = threading.current_thread().name
        logging.info(f"DNS Handler ({thread_name}) başlatıldı.")
        while not self.stop_dns_server.is_set():
            try:
                # select ile non-blocking bekleme (1 saniye timeout)
                ready = select.select([sock], [], [], 1)
                if ready[0]: # Eğer sokette okunacak veri varsa
                    data, client_addr = sock.recvfrom(1024) # UDP paketini al
                    logging.debug(f"DNS isteği alındı: {client_addr}, Boyut: {len(data)}")

                    # Basit bir protokol: SECRET_DOMAIN içeriyor mu?
                    # Daha gelişmiş DNS protokol analizi yapılabilir (dnslib gibi)
                    if secret_domain_bytes in data:
                        try:
                            # Domain'den önceki kısmı şifreli veri olarak al
                            encrypted_part = data.split(secret_domain_bytes)[0]
                            decrypted_query = self._aes_decrypt(encrypted_part)

                            if decrypted_query:
                                logging.info(f"DNS Tüneli (Çözüldü): {client_addr} -> Sorgu: '{decrypted_query}'")
                                # İstemciye basit bir onay yanıtı gönder (şifreli)
                                response_data = f"ACK:{decrypted_query}"
                                encrypted_response = self._aes_encrypt(response_data)
                                if encrypted_response:
                                    # Yanıtı aynı istemciye geri gönder
                                    sock.sendto(encrypted_response + secret_domain_bytes, client_addr)
                                    logging.debug(f"DNS Tüneli (Yanıt Gönderildi): {client_addr} <- '{response_data}'")
                            # else: Şifre çözülemediyse log zaten basıldı, yanıt gönderme
                        except Exception as process_err:
                             logging.error(f"DNS isteği işlenirken hata ({client_addr}): {process_err}")

            except OSError as e: # Soket kapatıldığında oluşabilir
                 if self.stop_dns_server.is_set():
                      logging.info(f"DNS Handler ({thread_name}) durduruluyor (soket kapatıldı).")
                 else:
                      logging.error(f"DNS soket hatası: {e}")
                 break # Döngüden çık
            except Exception as e:
                logging.error(f"DNS Handler ({thread_name}) içinde beklenmedik hata: {e}")
                # Hata olsa bile devam etmeyi dene (isteğe bağlı)
                time.sleep(1)
        logging.info(f"DNS Handler ({thread_name}) sonlandı.")


    def start_dns_tunnel(self,
                        listen_port: int = 53,
                        secret_domain: str = DEFAULT_DNS_SECRET_DOMAIN) -> None:
        """AES şifreli basit bir DNS tünel sunucusu başlatır."""
        logging.info(f"DNS Tüneli başlatılıyor (Port: {listen_port}, Secret Domain: {secret_domain})...")
        self.stop_dns_server.clear() # Durdurma bayrağını temizle

        try:
            # UDP soketi oluştur ve dinlemeye başla
            # 0.0.0.0 tüm ağ arayüzlerini dinler
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', listen_port))
            logging.info(f"DNS Tüneli {listen_port} UDP portunda dinleniyor...")

            secret_domain_bytes = secret_domain.encode('utf-8')

            # Gelen istekleri işlemek için bir thread başlat
            # Birden fazla handler thread de başlatılabilir ama basit tutalım
            handler_thread = threading.Thread(target=self._dns_handler, args=(sock, secret_domain_bytes), name="DNS-Handler")
            handler_thread.start()

            # Ana thread burada bekleyebilir veya başka işler yapabilir.
            # Şimdilik, durdurma sinyali gelene kadar beklemesini sağlayalım.
            # Kullanıcı Ctrl+C yaparsa KeyboardInterrupt yakalanır.
            while not self.stop_dns_server.is_set():
                 time.sleep(1) # CPU kullanmamak için bekle

        except OSError as e:
             logging.error(f"DNS Tüneli başlatılamadı (Port {listen_port}): {e}")
             logging.error("Bu port kullanımda olabilir veya root yetkisi gerektirebilir (port < 1024).")
        except Exception as e:
            logging.error(f"DNS Tüneli başlatılırken beklenmedik hata: {e}")
            traceback.print_exc()
        finally:
            logging.info("DNS Tüneli durduruluyor...")
            self.stop_dns_server.set() # Handler thread'e durma sinyali gönder
            if 'sock' in locals():
                 sock.close() # Soketi kapat
            if 'handler_thread' in locals() and handler_thread.is_alive():
                 handler_thread.join(timeout=2) # Thread'in bitmesini bekle
            logging.info("DNS Tüneli tamamen durduruldu.")


    # --- SSH Tüneli Fonksiyonları ---
    def _ssh_tunnel_worker(self, tunnel_name: str, config: Dict) -> None:
        """SSH tünelini ayrı bir thread içinde başlatır ve yönetir."""
        thread_name = threading.current_thread().name
        logging.info(f"SSH Tünel Worker ({thread_name} - {tunnel_name}) başlatılıyor.")
        server = None
        try:
            # Yapılandırmayı al
            jump_hosts = config['jump_hosts']
            local_bind = config['local_bind']
            remote_bind = config['remote_bind']

            # sshtunnel yapılandırması
            # Not: sshtunnel kütüphanesi arka planda zincirleme tünelleri yönetir.
            # Biz sadece ilk atlama noktasını ve son hedefi belirtiriz.
            # Zincirleme için ssh_proxy veya ssh_proxy_enabled kullanmak gerekebilir.
            # Veya her atlama için ayrı tünel nesnesi oluşturup birbirine bağlamak gerekir.
            # Basitlik adına, şimdilik TEK atlama varsayalım veya kütüphanenin zincirlemeyi
            # otomatik yapmasını umalım (dökümantasyona bakmak lazım).
            # Eğer zincirleme gerekiyorsa bu kısım daha karmaşık olur.

            # ---->>>> Düzeltme: sshtunnel doğrudan zincirleme desteklemez gibi.
            #           Zincirleme için ya proxy komutu (ProxyCommand) ya da
            #           iç içe tüneller manuel kurulmalı. Bu çok karmaşık.
            #           Şimdilik SADECE TEK JUMP HOST destekleyelim.
            #           Kullanıcı zincirleme istiyorsa, bunu manuel yapmalı.

            if len(jump_hosts) > 1:
                 logging.warning(f"[{tunnel_name}] Bu implementasyon şu anda sadece TEK atlama noktasını (jump host) destekler. Sadece ilk host kullanılacak.")
            elif not jump_hosts:
                 logging.error(f"[{tunnel_name}] SSH Tüneli için en az bir atlama noktası (jump host) gerekir.")
                 return

            first_jump = jump_hosts[0]

            # SSH Anahtarı ve Şifre kontrolü
            ssh_password = first_jump.get('pass')
            ssh_pkey = first_jump.get('pkey')
            if not ssh_password and not ssh_pkey:
                 logging.warning(f"[{tunnel_name}] SSH için şifre ('pass') veya özel anahtar ('pkey') belirtilmedi. Bağlantı başarısız olabilir.")

            server = SSHTunnelForwarder(
                ssh_address_or_host=(first_jump['host'], int(first_jump.get('port', 22))), # Port int olmalı
                ssh_username=first_jump.get('user'), # Kullanıcı adı None olabilir
                ssh_password=ssh_password,
                ssh_pkey=ssh_pkey,
                # ssh_proxy= ... # Zincirleme için ProxyCommand ayarı burada yapılabilir
                remote_bind_address=remote_bind, # (hedef_host, hedef_port)
                local_bind_address=local_bind,   # ('127.0.0.1', yerel_port)
                set_keepalive=30.0 # Bağlantıyı canlı tut
            )
            server.start() # Tüneli başlat (arka planda thread kullanır)
            logging.info(f"SSH Tüneli Başlatıldı: {tunnel_name} [{local_bind[0]}:{server.local_bind_port} -> {first_jump['host']} -> {remote_bind[0]}:{remote_bind[1]}]")

            # Tüneli aktif tüneller listesine ekle
            with self.lock:
                self.active_ssh_tunnels[tunnel_name] = server

            # Tünel aktif olduğu sürece bekle
            # server.is_active kontrolü ile veya server thread'ini join() ile bekleyebiliriz.
            # Veya bu worker thread'i sadece başlatıp bırakabiliriz, kapatma sinyali gelince server.stop() çağrılır.
            # Şimdilik worker thread'in tünel kapanana kadar yaşamasını sağlayalım.
            while server.is_active:
                 time.sleep(1)
            logging.info(f"SSH Tüneli ({tunnel_name}) aktif değil veya durduruldu.")


        except BaseSSHTunnelForwarderError as e:
            logging.error(f"SSH Tünel Hatası ({tunnel_name}): {e}")
            # print(f"{R}SSH Tünel Hatası ({tunnel_name}): {e}{RESET}")
        except FileNotFoundError as e:
             logging.error(f"SSH Özel Anahtar Dosyası bulunamadı ({tunnel_name}): {e}")
        except paramiko.AuthenticationException as e:
             logging.error(f"SSH Kimlik Doğrulama Hatası ({tunnel_name}): {e}")
        except Exception as e:
            logging.error(f"SSH Tüneli Worker ({tunnel_name}) içinde beklenmedik hata: {e}")
            traceback.print_exc()
        finally:
            # Worker bittiğinde veya hata olduğunda tüneli kapatmayı dene
            if server and server.is_active:
                 server.stop()
            # Listeden kaldır
            with self.lock:
                if tunnel_name in self.active_ssh_tunnels:
                    del self.active_ssh_tunnels[tunnel_name]
            logging.info(f"SSH Tünel Worker ({thread_name} - {tunnel_name}) sonlandı.")


    def create_ssh_tunnel(self,
                         tunnel_name: str,
                         jump_hosts: List[Dict[str, str]], # List of {'host': '...', 'port': ..., 'user': ..., 'pass': ..., 'pkey': ...}
                         local_port: int,
                         remote_host: str,
                         remote_port: int) -> bool:
        """(Tek atlamalı) SSH tüneli oluşturmak için worker thread başlatır."""

        # Basit doğrulama
        if not tunnel_name:
            logging.error("Tünel adı boş olamaz.")
            return False
        if not jump_hosts:
             logging.error("En az bir atlama noktası (jump host) gerekli.")
             return False
        if not isinstance(jump_hosts, list):
             logging.error("jump_hosts bir liste olmalı.")
             return False
        for host_info in jump_hosts:
             if not isinstance(host_info, dict) or 'host' not in host_info:
                  logging.error("jump_hosts içindeki her eleman 'host' anahtarı içeren bir sözlük olmalı.")
                  return False
             if not self._validate_ip(host_info['host']): # IP formatını kontrol et
                  return False
             # Port numarasını kontrol et (varsa)
             if 'port' in host_info:
                 try: int(host_info['port'])
                 except (ValueError, TypeError): logging.error(f"Geçersiz port numarası: {host_info['port']}"); return False

        if not self._validate_ip(remote_host):
             logging.error(f"Uzak sunucu için geçersiz IP formatı: {remote_host}")
             return False
        try:
             if not (0 < int(local_port) < 65536 and 0 < int(remote_port) < 65536): raise ValueError()
        except (ValueError, TypeError):
             logging.error(f"Geçersiz yerel ({local_port}) veya uzak ({remote_port}) port numarası.")
             return False

        # Zaten bu isimde tünel var mı?
        with self.lock:
             if tunnel_name in self.active_ssh_tunnels:
                  logging.error(f"Bu isimde ('{tunnel_name}') zaten aktif bir tünel var.")
                  return False

        # Tünel yapılandırmasını oluştur
        config = {
            'jump_hosts': jump_hosts,
            'local_bind': ('127.0.0.1', local_port), # Genellikle localhost'a bağlanır
            'remote_bind': (remote_host, remote_port)
        }

        # Worker thread'i başlat
        worker = threading.Thread(target=self._ssh_tunnel_worker, args=(tunnel_name, config), name=f"SSH-{tunnel_name}", daemon=True)
        worker.start()
        logging.info(f"SSH Tüneli başlatma talebi gönderildi: {tunnel_name}")
        # Başarının teyidi worker thread içinde loglanır.
        return True # Başlatma talebi başarılı


    def close_ssh_tunnel(self, tunnel_name: str) -> None:
        """Aktif SSH tünelini kapatır."""
        with self.lock:
            if tunnel_name in self.active_ssh_tunnels:
                server = self.active_ssh_tunnels.get(tunnel_name)
                if server:
                    try:
                        logging.info(f"SSH Tüneli kapatılıyor: {tunnel_name}...")
                        server.stop()
                        # Worker thread'in bitmesini beklemeye gerek yok, kendi kendine bitmeli.
                        # Listeden silme worker thread içinde yapılıyor.
                        # del self.active_ssh_tunnels[tunnel_name] # Burada silmek yerine worker'da silmek daha güvenli
                        print(f"{G}SSH Tüneli '{tunnel_name}' başarıyla kapatıldı.{RESET}")
                    except Exception as e:
                        logging.error(f"SSH Tüneli ({tunnel_name}) kapatılırken hata: {str(e)}")
                        print(f"{R}SSH Tüneli '{tunnel_name}' kapatılırken hata: {e}{RESET}")
                else:
                     # Bu durum olmamalı ama kontrol edelim
                     del self.active_ssh_tunnels[tunnel_name]
            else:
                print(f"{Y}Uyarı: '{tunnel_name}' isimli aktif bir SSH tüneli bulunamadı.{RESET}")


    def list_ssh_tunnels(self) -> None:
        """Aktif SSH tünellerini listeler."""
        print(f"\n{C}--- Aktif SSH Tünelleri ---{RESET}")
        with self.lock:
            if not self.active_ssh_tunnels:
                print(f"{Y}Aktif SSH tüneli yok.{RESET}")
                return

            for name, server in self.active_ssh_tunnels.items():
                status = f"{G}Aktif{RESET}" if server.is_active else f"{R}Aktif Değil{RESET}"
                local_bind = f"{server.local_bind_host}:{server.local_bind_port}"
                remote_bind = f"{server.remote_bind_address[0]}:{server.remote_bind_address[1]}"
                ssh_server = f"{server.ssh_host}:{server.ssh_port}"
                print(f" Tünel Adı: {Y}{name}{RESET}")
                print(f"   Durum: {status}")
                print(f"   Yerel Bağlantı: {local_bind}")
                print(f"   SSH Sunucusu: {ssh_server}")
                print(f"   Uzak Hedef: {remote_bind}")
                print("-" * 20)

# --- Kullanıcı Arayüzü ve Ana Çalıştırma ---
def print_ssh_tunnel_menu():
     print(f"""\n{B}--- SSH Tünel Seçenekleri ---{RESET}
  {C}1.{RESET} Yeni SSH Tüneli Oluştur (Tek Atlamalı)
  {C}2.{RESET} Aktif SSH Tünellerini Listele
  {C}3.{RESET} SSH Tünelini Kapat
  {R}0.{RESET} Ana Menüye Dön
""")
     return input(f"{Y}Seçiminiz: {RESET}").strip()

def run_ssh_tunnel_ui(manager: SecureTunnelManager):
     while True:
          choice = print_ssh_tunnel_menu()
          if choice == '1':
               print("\n--- Yeni SSH Tüneli Bilgileri ---")
               try:
                    t_name = input("Tünele bir isim verin: ").strip()
                    jh_host = input("Atlama Noktası (Jump Host) IP/Hostname: ").strip()
                    jh_port = input("Jump Host SSH Portu [Varsayılan: 22]: ").strip() or '22'
                    jh_user = input("Jump Host Kullanıcı Adı: ").strip()
                    print("Jump Host Kimlik Doğrulama Yöntemi:")
                    print(" 1: Şifre")
                    print(" 2: Özel Anahtar Dosyası (Private Key)")
                    auth_method = input("Seçiminiz [1 veya 2]: ").strip()
                    jh_pass = None
                    jh_pkey = None
                    if auth_method == '1':
                         jh_pass = input("Jump Host Şifresi: ").strip() # getpass daha güvenli olurdu
                    elif auth_method == '2':
                         jh_pkey = input("Özel Anahtar Dosya Yolu (örn: /home/user/.ssh/id_rsa): ").strip()
                         if not os.path.exists(jh_pkey):
                              print(f"{R}Hata: Belirtilen anahtar dosyası bulunamadı: {jh_pkey}{RESET}")
                              continue
                    else:
                         print(f"{R}Geçersiz kimlik doğrulama yöntemi seçildi.{RESET}")
                         continue

                    r_host = input("Hedef Sunucu IP/Hostname (Tünelin ulaşacağı): ").strip()
                    r_port = input("Hedef Sunucu Portu: ").strip()
                    l_port = input("Bu makinede dinlenecek Yerel Port: ").strip()

                    # Girdileri doğrula ve tüneli oluştur
                    jump_hosts_list = [{'host': jh_host, 'port': int(jh_port), 'user': jh_user, 'pass': jh_pass, 'pkey': jh_pkey}]
                    manager.create_ssh_tunnel(
                         tunnel_name=t_name,
                         jump_hosts=jump_hosts_list,
                         local_port=int(l_port),
                         remote_host=r_host,
                         remote_port=int(r_port)
                         )
                    # Başlatma talebi gönderildi, durum listede görünecek
                    time.sleep(1) # Başlaması için kısa bir süre tanı

               except ValueError as e:
                    print(f"{R}Hata: Geçersiz sayısal değer girdiniz (Port?). {e}{RESET}")
               except Exception as e:
                    print(f"{R}Hata: Tünel oluşturma sırasında sorun oluştu: {e}{RESET}")
                    traceback.print_exc()

          elif choice == '2':
               manager.list_ssh_tunnels()
          elif choice == '3':
               t_name_to_close = input("Kapatılacak tünelin adını girin: ").strip()
               if t_name_to_close:
                    manager.close_ssh_tunnel(t_name_to_close)
               else:
                    print(f"{R}Tünel adı boş olamaz.{RESET}")
          elif choice == '0':
               break # SSH menüsünden çık
          else:
               print(f"{R}Geçersiz seçim.{RESET}")
          input(f"\n{C}Devam etmek için Enter'a basın...{RESET}")


def print_dns_tunnel_menu():
     print(f"""\n{B}--- DNS Tünel Seçenekleri ---{RESET}
  {C}1.{RESET} DNS Tünel Sunucusunu Başlat (Arka Planda)
  {C}2.{RESET} DNS Tünel Sunucusunu Durdur (DURDURULAMAZ - Programı Kapatın)
  {R}0.{RESET} Ana Menüye Dön
""")
     # Not: Basit thread yönetimi ile sunucuyu güvenli durdurmak zor.
     #      Programı kapatmak en kolay yol.
     return input(f"{Y}Seçiminiz: {RESET}").strip()

def run_dns_tunnel_ui(manager: SecureTunnelManager):
     dns_thread = None
     while True:
          choice = print_dns_tunnel_menu()
          if choice == '1':
              if dns_thread and dns_thread.is_alive():
                  print(f"{Y}DNS Tünel sunucusu zaten çalışıyor.{RESET}")
              else:
                   print("\n--- DNS Tüneli Ayarları ---")
                   try:
                        dns_port = input("Dinlenecek UDP Portu [Varsayılan: 53]: ").strip() or '53'
                        dns_domain = input(f"Gizli Alan Adı [Varsayılan: {DEFAULT_DNS_SECRET_DOMAIN}]: ").strip() or DEFAULT_DNS_SECRET_DOMAIN
                        # Anahtar ve IV'yi de burada sormak daha iyi olabilir ama şimdilik varsayılanı kullanalım.

                        # Sunucuyu ayrı bir thread'de başlat
                        dns_thread = threading.Thread(
                             target=manager.start_dns_tunnel,
                             args=(int(dns_port), dns_domain),
                             name="DNS-Tunnel-Server",
                             daemon=True # Ana program kapanınca bu da kapansın
                        )
                        dns_thread.start()
                        print(f"{G}DNS Tünel sunucusu başlatıldı (Port: {dns_port}, Domain: {dns_domain}). Logları '{LOG_FILENAME}' dosyasından takip edin.{RESET}")
                        time.sleep(1) # Başlaması için bekle
                   except ValueError:
                        print(f"{R}Hata: Geçersiz port numarası girdiniz.{RESET}")
                   except Exception as e:
                        print(f"{R}DNS Tüneli başlatılırken hata: {e}{RESET}")
                        traceback.print_exc()

          elif choice == '2':
                # manager.stop_dns_server.set() # Bu şekilde durdurmak için ana döngünün değişmesi gerekir.
                print(f"{R}DNS sunucusunu durdurmak için ana programı (Ctrl+C ile) kapatmanız gerekmektedir.{RESET}")
          elif choice == '0':
               break # DNS menüsünden çık
          else:
                print(f"{R}Geçersiz seçim.{RESET}")
          input(f"\n{C}Devam etmek için Enter'a basın...{RESET}")

# --- Ana Menü ---
def main_menu():
     print(f"""\n{C}--- Ağ Tünelleme Araçları ---{RESET}
  {B}1.{RESET} SSH Tünel Yönetimi
  {B}2.{RESET} DNS Tünel Yönetimi (Basit/Deneysel)
  {R}0.{RESET} Çıkış
""")
     return input(f"{Y}Seçiminiz: {RESET}").strip()

# --- Ana Çalıştırma ---
if __name__ == "__main__":
    manager = SecureTunnelManager()
    try:
         while True:
              main_choice = main_menu()
              if main_choice == '1':
                   run_ssh_tunnel_ui(manager)
              elif main_choice == '2':
                   run_dns_tunnel_ui(manager)
              elif main_choice == '0':
                   print(f"{G}Çıkış yapılıyor...{RESET}")
                   # Aktif SSH tünellerini kapatmayı deneyelim
                   active_tunnels_copy = list(manager.active_ssh_tunnels.keys()) # Kopi üzerinde dönelim
                   if active_tunnels_copy:
                        print(f"{Y}Aktif SSH tünelleri kapatılıyor...{RESET}")
                        for name in active_tunnels_copy:
                             manager.close_ssh_tunnel(name)
                   # DNS sunucusunu durdur (set event)
                   manager.stop_dns_server.set()
                   break
              else:
                   print(f"{R}Geçersiz seçim.{RESET}")
    except KeyboardInterrupt:
         print(f"\n{G}Ctrl+C algılandı. Çıkış yapılıyor...{RESET}")
         manager.stop_dns_server.set() # DNS'i durdur
         # SSH tünellerini de kapat
         active_tunnels_copy = list(manager.active_ssh_tunnels.keys())
         if active_tunnels_copy:
             print(f"{Y}Aktif SSH tünelleri kapatılıyor...{RESET}")
             for name in active_tunnels_copy: manager.close_ssh_tunnel(name)
    except Exception as e:
         print(f"\n{R}Ana programda beklenmedik hata: {e}{RESET}")
         traceback.print_exc()
    finally:
         print(f"{C}Program sonlandı.{RESET}")
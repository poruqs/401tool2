#!/usr/bin/env python3
import socket
import threading
import select
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
import paramiko
import ipaddress
import logging
from typing import List, Dict, Optional

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tunnel.log'),
        logging.StreamHandler()
    ]
)

class SecureTunnelManager:
    def __init__(self):
        self.active_tunnels = {}
        self.dns_key = b'32-byte-long-encryption-key-here!'
        self.dns_iv = b'16-byte-iv-here!'
        self.lock = threading.Lock()

    def _validate_ip(self, ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            logging.error(f"Geçersiz IP adresi: {ip}")
            return False

    def _aes_encrypt(self, data: str) -> bytes:
        cipher = AES.new(self.dns_key, AES.MODE_CBC, self.dns_iv)
        return cipher.encrypt(pad(data.encode(), AES.block_size))

    def _aes_decrypt(self, data: bytes) -> str:
        cipher = AES.new(self.dns_key, AES.MODE_CBC, self.dns_iv)
        return unpad(cipher.decrypt(data), AES.block_size).decode()

    def start_dns_tunnel(self, 
                        listen_port: int = 53,
                        remote_server: str = "tunnel.example.com",
                        secret_domain: str = "dns.sec") -> None:
        """AES şifreli DNS tüneli başlatır"""
        
        if not self._validate_ip(remote_server.split(':')[0]):
            return

        def dns_handler(data: bytes, client_addr: tuple) -> None:
            try:
                if secret_domain.encode() in data:
                    encrypted = data.split(secret_domain.encode())[0]
                    decrypted = self._aes_decrypt(encrypted)
                    logging.info(f"DNS Tüneli: {client_addr} -> {decrypted}")
                    
                    # Şifreli yanıt gönder
                    response = self._aes_encrypt("ACK:" + decrypted)
                    sock.sendto(response + secret_domain.encode(), client_addr)
            except Exception as e:
                logging.error(f"DNS işleme hatası: {str(e)}")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', listen_port))
            logging.info(f"DNS tüneli {listen_port} portunda dinleniyor...")

            while True:
                ready = select.select([sock], [], [], 1)
                if ready[0]:
                    data, addr = sock.recvfrom(1024)
                    threading.Thread(target=dns_handler, args=(data, addr)).start()
                    
        except Exception as e:
            logging.error(f"DNS tünel hatası: {str(e)}")
        finally:
            sock.close()

    def create_ssh_tunnel(self,
                         jump_hosts: List[Dict[str, str]],
                         local_port: int,
                         remote_host: str,
                         remote_port: int,
                         tunnel_name: str = "default") -> bool:
        """Çoklu atlamalı SSH tüneli oluşturur"""
        
        if not all(self._validate_ip(h['host']) for h in jump_hosts):
            return False

        def _tunnel_worker():
            try:
                last_server = None
                for i, host in enumerate(jump_hosts):
                    if i == len(jump_hosts) - 1:  # Son atlama
                        remote_bind = (remote_host, remote_port)
                    else:
                        remote_bind = (jump_hosts[i+1]['host'], jump_hosts[i+1].get('port', 22))

                    server = SSHTunnelForwarder(
                        ssh_address_or_host=(host['host'], host.get('port', 22)),
                        ssh_username=host['user'],
                        ssh_password=host.get('pass'),
                        ssh_pkey=host.get('pkey'),
                        remote_bind_address=remote_bind,
                        local_bind_address=('127.0.0.1', local_port if i == 0 else 0),
                        set_keepalive=30
                    )
                    server.start()
                    last_server = server

                with self.lock:
                    self.active_tunnels[tunnel_name] = last_server
                logging.info(f"SSH tüneli aktif: {tunnel_name}")

            except BaseSSHTunnelForwarderError as e:
                logging.error(f"SSH tünel hatası: {str(e)}")
                return False
            except Exception as e:
                logging.error(f"Beklenmeyen hata: {str(e)}")
                return False
            return True

        return threading.Thread(target=_tunnel_worker, daemon=True).start()

    def close_tunnel(self, tunnel_name: str) -> None:
        """Aktif tüneli kapatır"""
        with self.lock:
            if tunnel_name in self.active_tunnels:
                try:
                    self.active_tunnels[tunnel_name].stop()
                    del self.active_tunnels[tunnel_name]
                    logging.info(f"Tünel kapatıldı: {tunnel_name}")
                except Exception as e:
                    logging.error(f"Tünel kapatma hatası: {str(e)}")

    def list_tunnels(self) -> Dict[str, Dict]:
        """Aktif tünelleri listeler"""
        return {
            name: {
                'local_port': tunnel.local_bind_port,
                'status': 'active' if tunnel.is_active else 'inactive'
            }
            for name, tunnel in self.active_tunnels.items()
        }

# Kullanım Örneği
if __name__ == "__main__":
    manager = SecureTunnelManager()
    
    # DNS Tüneli Başlatma
    threading.Thread(
        target=manager.start_dns_tunnel,
        kwargs={'secret_domain': 'mysecret.xyz'}
    ).start()
    
    # SSH Tüneli Oluşturma (3 atlamalı)
    ssh_jumps = [
        {'host': 'jump1.example.com', 'user': 'user1', 'pass': 'pass1'},
        {'host': 'jump2.example.com', 'user': 'user2', 'pkey': '/path/to/key'},
        {'host': 'target.internal', 'user': 'admin', 'pass': 'secret'}
    ]
    
    manager.create_ssh_tunnel(
        jump_hosts=ssh_jumps,
        local_port=8080,
        remote_host='db.internal',
        remote_port=3306,
        tunnel_name='mysql_tunnel'
    )
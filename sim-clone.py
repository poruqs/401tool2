import subprocess
import re
from datetime import datetime

class SIMCloner:
    def __init__(self, port="/dev/ttyACM0"):
        self.port = port
        self.log_file = "sim_clone_log.txt"

    def detect_card(self):
        try:
            output = subprocess.check_output(["qcsuper", "--port", self.port, "--detect"])
            return "SIM detected" in output.decode()
        except Exception as e:
            self.log_error(f"Detection error: {str(e)}")
            return False

    def clone_sim(self, output_file="sim_data.bin"):
        commands = [
            f"qcsuper --port {self.port} --read --file {output_file}",
            f"qcsuper --port {self.port} --dump --file {output_file}.json"
        ]
        for cmd in commands:
            try:
                subprocess.run(cmd.split(), check=True)
            except subprocess.CalledProcessError as e:
                self.log_error(f"Clone failed: {str(e)}")
                return False
        return True

    def log_error(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"[{datetime.now()}] ERROR: {message}\n")

# Kullanım:
# cloner = SIMCloner("/dev/ttyUSB0")
# if cloner.detect_card():
#     cloner.clone_sim()
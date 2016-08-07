import os
from subprocess import run
from subprocess import PIPE

class OffSite():
    def __init__():
        self.addr = "fisk@192.168.2.99"
        self.port = "22"
        self.workpoint = "/home/fisk/.config/LuksLocker/working"
        self.safepoint = "/run/media/fisk/Safe"
        os.makedirs(self.workpoint, exist_ok=True)
        os.makedirs(self.safepoint, exist_ok=True)



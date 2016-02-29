#! /usr/bin/python3

import subprocess, os
os.chdir("/home/fisk/Projects/python/Safe")
subprocess.call("gksudo --preserve-env \"./safe.pyw -u $USER\"", shell=True)

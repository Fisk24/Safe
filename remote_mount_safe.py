#! /usr/bin/python3

import getpass, re, time
from paramiko import SSHClient
from paramiko import AutoAddPolicy

class Main():
    def __init__(self):
        self.server = "192.168.1.250"
        self.user   = "fisk"
        self.pw     = getpass.getpass("Password for \"fisk\" on the remote host:")
        self.initSSH("ask")
        self.execRemoteMount()
        input("Check volume mount then press enter")
        self.execRemoteClose()
        self.ssh.close()

    def sendData(self, data):
        while not self.channel.send_ready(): time.sleep(1)
        self.channel.send(str(data))

    def recvData(self, size):
        while not self.channel.recv_ready(): time.sleep(1)
        data = self.channel.recv(size)
        return data

    def execRemoteClose(self):
        stdin, stdout, stderr = self.ssh.exec_command("sudo /home/fisk/Projects/sshs/sshs close")

    def execRemoteMount(self):
        stdin, stdout, stderr = self.ssh.exec_command("sudo /home/fisk/Projects/sshs/sshs open /media/fisk/ARCHIVE1/Safe/onOLEcNsojuin.bin --key /media/fisk/ARCHIVE1/safe.keyfile")
        output = stdout.readlines()
        print(output)
        
    def initSSH(self, auto_add="no"):
        self.ssh = SSHClient() 
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(self.server, username=self.user, password=self.pw)
        self.channel = self.ssh.invoke_shell()

if __name__ == "__main__":
    Main()

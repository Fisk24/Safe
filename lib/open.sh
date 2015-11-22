#! /bin/bash
sudo cryptsetup luksOpen encrypted.img myEncryptedVolume --key-file mykey.keyfile
sudo mount /dev/mapper/myEncryptedVolume ~/Private
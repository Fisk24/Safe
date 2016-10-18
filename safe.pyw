#! /usr/bin/python3

# VERSION: a0.1

'''
	luksHeaderBackup <device> --header-backup-file <file>
	luksHeaderRestore <device> --header-backup-file <file>

	X - open LUKS volume with a key
	create LUKS volumes of any size
	generate passphrase/keyfile and use them to unlock LUKS volume

	### FOR GENERAL ###

	mount point
	minimize to system tray
	default volume deception
	luks header backup

	### FOR LUKS VOLUMES ###
		X - pick location for luks volume file
		X - pick size in terms of units "GiB, MiB, KiB"
		X - dropdown combobox for unit size "GiB, MiB, KiB"
		X - pick filesystem format
		-checkbox for "open when completed?"
		mount and set ownership then if the user did not want the device opened, unmount and lock
		0 - generate md5 checksum for LUKS volume
		X - alert the user that the process is completed

	### FOR PASSPHRASES ###
		ask for passphrase in two seprate entries "password, retype password"
		generate a keyfile on the fly that containes the password then delete the temp key file

	### FOR KEYFILES ###
		checkbox for "make keyfile read-only?"
		generate md5 checksum for keyfile

		keyfile and the md5 checksum will be automatically placed in same directory as the LUKS volume
			the user will be advised to seperate these files from the volume (perhaps place them on a 
			thumb drive and put the thumb drive in a safe)
'''

import sys
import os
import getpass
import subprocess
import argparse
from PyQt4        import uic
from PyQt4.QtGui  import *
from PyQt4.QtCore import *
from lib          import logger
from lib.config   import Config
from lib.qtUI.nlv import NewLuksUI
from lib.oslib    import OffSite

class Main(QMainWindow):
	def __init__(self):
		super(Main, self).__init__()

		#sys.excepthook = self.exceptHook

		logger.tear()

		#### PARSE ARGS ####
		self.parser = argparse.ArgumentParser(description="Manage encrypted file containers...")
		self.parser.add_argument("-u", dest="username", default=getpass.getuser(), help="Pass the potential owner of any volumes created. (Default: you)")
		self.args = self.parser.parse_args()

		print(self.args.username)

		#### Detect Platform/User ####
		if not os.getuid() == 0:
			QMessageBox.critical(self, "User Error", "This program must be run as root to opperate properly.")
			sys.exit(1)

		if sys.platform == "linux":
			cfile = "settings.json"
			cloc  = "."

		#### LOAD CONFIGURATION ####
		self.conf = Config(cfile=cfile, cloc=cloc)
		logger.out(self.conf, self.conf.data[0]["debug"], doTime=False)

		#### LOAD UI FILES ####
		self.ui = uic.loadUi("lib/qtUI/mainwindow.ui", self)

		#### VARIABLES ####
		self.volume  = ""
		self.keyfile = ""
		self.mode    = "LUKS"
		self.opened  = False
                
                #### Connect Buttons ####
		self.ui.openButton.clicked.connect(self.verifyFiles)
		self.ui.closeButton.clicked.connect(self.closeMode)
		self.ui.volumeToolButton.clicked.connect(self.browseVolume)
		self.ui.keyToolButton.clicked.connect(self.browseKey)
		self.ui.newVolToolButton.clicked.connect(self.chooseNewVol)
		#self.ui.openButton.setEnabled(False)

		#### Default UI Mode ####
		if self.conf.data[0]["state"]:
			QMessageBox.critical(self, "User Error", "LUKS Locker was not closed properly last time. For the safety of your encrypted files, please remember to close your locker or use the close button to make LUKS Locker do it for you.")
			self.setCloseUI()
		else:
			self.setOpenUI()
		
		self.ui.passwordLineEdit.hide()

		#### Actions ####
		self.ui.securityComboBox.currentIndexChanged[str].connect(self.switchSecurity)
		#self.ui.volumeTypeComboBox.currentIndexChanged[str].connect(self.switchMode)

		#### Window Stays On Top ####
		self.setWindowFlags(Qt.WindowStaysOnTopHint)

	def exceptHook(self, exctype, excvalue, tracebackobj):
		logger.report()
		QMessageBox.critical(self, str(exctype), str(excvalue))

	def setState(self, state):
		self.conf.data[0]["status"] = state
		self.conf.save()

	def closeEvent(self, event):
		if self.opened:
			reply = QMessageBox.question(self, "Are you sure?", "Closing this window will close and lock you volume!\n\tAre you sure you want to continue?", QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.Yes:
				self.closeLuks()
				event.accept()
			else:
				event.ignore()
		else:
			event.accept()

	def switchSecurity(self, string):
		print("Changed UI")
		if string == "Key File":
			print(string)
			self.ui.keyLineEdit.show()
			self.ui.keyToolButton.show()
			self.ui.passwordLineEdit.hide()

		elif string == "Password":
			print(string)
			self.ui.keyLineEdit.hide()
			self.ui.keyToolButton.hide()
			self.ui.passwordLineEdit.show()

	def switchMode(self, string):
		print("Changed MODE: ",string)
		self.mode = string

	def chooseNewVol(self):
		self.showNewLuksUI()

	def showNewLuksUI(self):
		x = NewLuksUI.getNewLuksUI(self)

	def showNewDMCryptUI(self):
		pass

	def browseVolume(self):
		x = QFileDialog.getOpenFileName()
		if x != "":
			self.ui.volumeLineEdit.setText(x)
		#print(self.ui.volumeLineEdit.text())
		'''
		if self.ui.volumeLineEdit.text() != "":
			self.ui.openButton.setEnabled(True)
			'''

	def browseKey(self):
		x = QFileDialog.getOpenFileName()
		if x != "":
			self.ui.keyLineEdit.setText(x)
		#print(self.ui.volumeLineEdit.text())
		'''
		if self.ui.volumeLineEdit.text() != "":
			self.ui.openButton.setEnabled(True)
			'''

	def verifyFiles(self):
		if os.path.isfile(self.ui.volumeLineEdit.text()) and os.path.isfile(self.ui.keyLineEdit.text()):
			self.openMode()
		else:
			QMessageBox.critical(self, "One or more files not found!", "One or more of the specified files does not exist!")

	def setOpenUI(self):
		self.ui.closeButton.hide()

	def setCloseUI(self):
		self.ui.openButton.hide()

	def createMountPoint(self):
		x = self.conf.data[0]["mpoint"].split("/")
		print(x)
		y = ""
		for i in x:
			y += i+"/"
			print(y)
			try:
				os.mkdir(y)
			except Exception as e:
				logger.out("WARN: "+str(e))


	def openMode(self):
		if self.mode == "LUKS":
			self.openLuks()
		elif self.mode == "DM-C":
			self.openDmc()

	def closeMode(self):
		if self.mode == "LUKS":
			self.closeLuks()
		elif self.mode == "DM-C":
			self.closeDmc()

	def openDmc(self):
		pass

	def closeDmc(self):
		pass

	def openLuks(self):
		self.setState(True)
		self.createMountPoint()

		try:
			out1 = subprocess.check_output("cryptsetup luksOpen \""+self.ui.volumeLineEdit.text()+"\" luksLocker1 --key-file \""+self.ui.keyLineEdit.text()+"\"", stderr=subprocess.STDOUT, shell=True)
			out2 = subprocess.check_output("mount /dev/mapper/luksLocker1 \""+self.conf.data[0]["mpoint"]+"\"", stderr=subprocess.STDOUT, shell=True)
			logger.out("Decrypted and mounted volume...")
			#print(out1, out2)
			self.opened = True
			self.ui.volumeToolButton.setEnabled(False)
			self.ui.keyToolButton.setEnabled(False)
			self.ui.volumeLineEdit.setReadOnly(True)
			self.ui.keyLineEdit.setReadOnly(True)
			self.ui.passwordLineEdit.setReadOnly(True)
			self.ui.securityComboBox.setEnabled(False)
			self.ui.closeButton.show()
			self.ui.openButton.hide()
		except subprocess.CalledProcessError as e:
			logger.out("ERROR: "+str(e))
			logger.out(e.output.decode("utf-8"))
			logger.report()
			#print("THIS: ", e.output)
			QMessageBox.warning(self, "Oops!", e.output.decode("utf-8"))
			if self.conf.data[0]['debug']:
				QMessageBox.critical(self, "Warning", str(e))

	def closeLuks(self):
		try:
			com = subprocess.check_output("umount \""+self.conf.data[0]["mpoint"]+"\"", stderr=subprocess.STDOUT, shell=True)
			com = subprocess.check_output("cryptsetup luksClose luksLocker1", stderr=subprocess.STDOUT, shell=True)
			logger.out("Unmounted and Encrypted...")
			self.opened = False
			self.ui.volumeToolButton.setEnabled(True)
			self.ui.keyToolButton.setEnabled(True)
			self.ui.volumeLineEdit.setReadOnly(False)
			self.ui.keyLineEdit.setReadOnly(False)
			self.ui.passwordLineEdit.setReadOnly(False)
			self.ui.securityComboBox.setEnabled(True)
			self.ui.closeButton.hide()
			self.ui.openButton.show()

		except subprocess.CalledProcessError as e:
			logger.out("ERROR: "+str(e))
			logger.out(e.output.decode("utf-8"))
			logger.report()
			#print("THIS: ", e.output)
			QMessageBox.warning(self, "Oops!", e.output.decode("utf-8"))
			if self.conf.data[0]['debug']:
				QMessageBox.critical(self, "Warning", str(e))

		except Exception as e:
			QMessageBox.warning(self, "ERROR", str(e))



if __name__ == "__main__":
	try:
		app = QApplication(sys.argv)
		win = Main()
		win.show()
		sys.exit(app.exec_())
	except:
		logger.report()

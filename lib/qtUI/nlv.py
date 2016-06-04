import os, sys, subprocess, random, traceback
from PyQt4        import uic
from PyQt4.QtGui  import *
from PyQt4.QtCore import *
from lib          import logger

class ValidationError(ValueError):
    pass

class CreationError(ValueError):
    pass

class NewLuksUI(QDialog):
    def __init__(self, parent=None):
	#QDialog.__init__(self)
        super(NewLuksUI, self).__init__(parent)
        
        self.ui = uic.loadUi("lib/qtUI/newluks.ui", self)
        
        ### VARIABLES ###
        self.parent       = parent
        self.securityMode = "KEY" #or "PASS"
        self.keygen       = 0
        self.lastgen      = ""
        ### BIND ACTIONS ###
        self.ui.okPushButton.clicked.connect(self.validate)
        self.ui.canclePushButton.clicked.connect(self.reject)
        self.ui.passwordRadioButton.clicked.connect(self.setPasswordSecurity)
        self.ui.keyfileRadioButton.clicked.connect(self.setKeySecurity)
        self.ui.showPwCheckBox.clicked.connect(self.showHidePassword)
        self.ui.newVolBrowseToolButton.clicked.connect(self.browseVolume)
        self.ui.keyFileBrowseToolButton.clicked.connect(self.browseKey)
        self.ui.newVolNewToolButton.clicked.connect(self.saveVolume)
        self.ui.keyFileNewToolButton.clicked.connect(self.saveKey)
        #self.ui.generatePushButton.clicked.connect(self.generateKey)
        
    def generateKey(self):
        #self.ui.generatePushButton.isEnabled(False)
        try:
            os.remove(self.lastgen)
        except:
            pass
        rand = random.getrandbits(128)
        keygen = subprocess.check_output("dd if=/dev/urandom of={0}.key bs=1024 count=1".format(rand), shell=True)
        self.ui.keyFileLineEdit.setText("{0}.key".format(rand))
        self.lastgen = "{0}.key".format(rand)
        
        #self.ui.generatePushButton.isEnabled(True)
        
    def browseVolume(self):
        x = QFileDialog.getOpenFileName()
        if x != "":
            self.ui.newVolLineEdit.setText(x)
    
    def browseKey(self):
        x = QFileDialog.getOpenFileName()
        if x != "":
            self.ui.keyFileLineEdit.setText(x)
            
    def saveVolume(self):
        #QString getSaveFileName (QWidget parent = None, QString caption = QString(), QString directory = QString(), QString filter = QString(), QString selectedFilter = None, Options options = 0)
        x = QFileDialog.getSaveFileNameAndFilter(self, "New LUKS Volume...", "", "Bin (*.bin)")
        if x[0] != "":
            if x[0].split(".")[-1] == "bin":
                self.ui.newVolLineEdit.setText(x[0])
            else:
                self.ui.newVolLineEdit.setText(x[0]+".bin")
		#self.ui.keyFileLineEdit.setText(x[0]+".key")
    
    def saveKey(self):
        x = QFileDialog.getSaveFileNameAndFilter(self, "New Key File...", "", "Keyfile (*.keyfile)")
        if x[0] != "":
            if x[0].split(".")[-1] == "keyfile":
                self.ui.keyFileLineEdit.setText(x[0])
            else:
                self.ui.keyFileLineEdit.setText(x[0]+".keyfile")
                
    def showHidePassword(self):
        if self.ui.showPwCheckBox.isChecked():
            self.ui.passwordLineEdit.setEchoMode(QLineEdit.Password)
            self.ui.retypeLineEdit.setEchoMode(QLineEdit.Password)
        else:
            self.ui.passwordLineEdit.setEchoMode(QLineEdit.Normal)
            self.ui.retypeLineEdit.setEchoMode(QLineEdit.Normal)
            
    def setPasswordSecurity(self):
        self.securityMode = "PASS"
        self.ui.passwordLineEdit.setEnabled(True)
        self.ui.retypeLineEdit.setEnabled(True)
        self.ui.showPwCheckBox.setEnabled(True)
        #self.ui.generatePushButton.setEnabled(False)
        self.ui.keyFileLineEdit.setEnabled(False)
        self.ui.keyFileBrowseToolButton.setEnabled(False)
        self.ui.keyFileNewToolButton.setEnabled(False)
        self.ui.md5CheckBox.setEnabled(False)
    
    def setKeySecurity(self):
        self.securityMode = "KEY"
        self.ui.passwordLineEdit.setEnabled(False)
        self.ui.retypeLineEdit.setEnabled(False)
        self.ui.showPwCheckBox.setEnabled(False)
        #self.ui.generatePushButton.setEnabled(True)
        self.ui.keyFileLineEdit.setEnabled(True)
        self.ui.keyFileBrowseToolButton.setEnabled(True)
        self.ui.keyFileNewToolButton.setEnabled(True)
        self.ui.md5CheckBox.setEnabled(True)
        
    def parseVolumeSize(self):
        x = self.ui.sizeUnitComboBox.currentText()
        if x == "GiB":
            return "G"
        elif x == "MiB":
            return "M"
        elif x == "KiB":
            return "K"
        
    def createMP(self):
        try:
            os.makedirs(self.parent.conf.data[0]["mpoint"])
        except Exception as e:
            logger.out("INFO: {0}".format(str(e)), wrt=0)
        
    def createKey(self):
        logger.out("Creating key...")
        try:
            if not os.path.isfile(self.ui.keyFileLineEdit.text()):
                #logger.out("dd if=/dev/urandom of={0} bs=1024 count=1".format(self.ui.keyFileLineEdit.text()))
                key = subprocess.check_output("dd if=/dev/urandom of=\"{0}\" bs=1024 count=1".format(self.ui.keyFileLineEdit.text()), shell=True)
                
            if self.ui.md5CheckBox.isChecked():
                md5 = subprocess.check_output("md5sum \"{0}\"".format(self.ui.keyFileLineEdit.text()), shell=True)
                print(md5.decode("utf-8").split(" ")[0])
                with open(self.ui.keyFileLineEdit.text()+".md5", "w") as file:
                    file.write(md5.decode("utf-8").split(" ")[0])
        except Exception as e:
            logger.report()
            raise CreationError(str(e))
        
    def createVolume(self):
        try:
            logger.out("Creating Volume")
            volume   = self.ui.newVolLineEdit.text()
            keyfile  = self.ui.keyFileLineEdit.text()
            sizeNumb = self.ui.sizeNumberSpinBox.value()
            if os.path.isfile(self.ui.newVolLineEdit.text()):
                reply = QMessageBox.question(self, "File Conflict", "Encryption will COMPLETELY overwrite this file!\nContinue?", QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.No:
                    raise CreationError("User disallowed volume overwrite...")
            #print("dd if=/dev/zero of=\"{0}\" bs=1 count=0 seek={1}{2}".format(self.ui.newVolLineEdit.text(), self.ui.sizeNumberDoubleSpinBox.value(), self.parseVolumeSize()))
            vol = subprocess.check_output("dd if=/dev/zero of=\"{0}\" bs=1 count=0 seek={1}{2}".format(volume, sizeNumb, self.parseVolumeSize()),stderr=subprocess.STDOUT , shell=True)
            vol = subprocess.check_output("cryptsetup luksFormat {0} {1} --batch-mode".format(volume, keyfile),stderr=subprocess.STDOUT , shell=True)
            
            try:
                vol = subprocess.check_output("cryptsetup luksOpen {0} luksLocker1 --key-file {1} --batch-mode".format(volume, keyfile),stderr=subprocess.STDOUT , shell=True)
            except:
                vol = subprocess.check_output("cryptsetup luksClose luksLocker1",stderr=subprocess.STDOUT , shell=True)
                vol = subprocess.check_output("cryptsetup luksOpen {0} luksLocker1 --key-file {1} --batch-mode".format(volume, keyfile),stderr=subprocess.STDOUT , shell=True)
                
            vol = subprocess.check_output("mkfs.ext4 /dev/mapper/luksLocker1",stderr=subprocess.STDOUT , shell=True)
            vol = subprocess.check_output("mount /dev/mapper/luksLocker1 {0}".format(self.parent.conf.data[0]["mpoint"]),stderr=subprocess.STDOUT , shell=True)
            #print("chown -R {0} {1}".format(self.parent.args.username, self.parent.conf.data[0]["mpoint"]))
            vol = subprocess.check_output("chown -R {0} {1}".format(self.parent.args.username, self.parent.conf.data[0]["mpoint"]),stderr=subprocess.STDOUT , shell=True)
            vol = subprocess.check_output("umount {0}".format(self.parent.conf.data[0]["mpoint"]),stderr=subprocess.STDOUT , shell=True)
            vol = subprocess.check_output("cryptsetup luksClose luksLocker1",stderr=subprocess.STDOUT , shell=True)
            self.parent.ui.volumeLineEdit.setText(volume)
            
        except subprocess.CalledProcessError as e:
            logger.out("ERROR: "+str(e))
            logger.out(e.output.decode("utf-8"))
            logger.report()
            #print("THIS: ", e.output)
            QMessageBox.warning(self, "Oops!", e.output.decode("utf-8"))
            if self.parent.conf.data[0]['debug']:
                QMessageBox.critical(self, "Warning", str(e))
                raise CreationError(str(e.output.decode("utf-8")))
        
        except Exception as e:
            logger.report()
            raise CreationError(str(e))
        
    def create(self):
        try:
            self.createKey()
            self.createMP()
            self.createVolume()
            QMessageBox.information(self, "Warning", "It is recomended that you keep your key and volume seperate. \nIf your volume is on your hard-drive then keep your key on a flashdrive...")
            QMessageBox.information(self, "Finished!", "Volume creation complete!\nYou may now store files in your volume. :D")
        
        except CreationError as e:
            QMessageBox.critical(self, "Volume creation could not countinue.", str(e))
        
        except Exception as e:
            QMessageBox.critical(self, "Unspecified Error", str(e))
            logger.report()
            
    def validateVolume(self):
        x = self.ui.newVolLineEdit.text().split("/")
        x.pop()
        print(x)
        print('/'.join(x))
        if not os.path.isdir('/'.join(x)):
            #QMessageBox.critical(self, "Volume information invalid!", "A Volume cannot be created in the specified location :C\nLocation:"+self.ui.newVolLineEdit.text())
            self.ui.newVolLineEdit.setFocus()
            raise ValidationError("A Volume cannot be created in the specified location :C\nLocation:\""+self.ui.newVolLineEdit.text()+"\"")
        
    def validateKey(self):
        x = self.ui.keyFileLineEdit.text().split("/")
        x.pop()
        if not os.path.isdir('/'.join(x)):
            self.ui.keyFileLineEdit.setFocus()
            raise ValidationError("A key cannot be created in the specified location :C\n\tLocation:"+self.ui.keyFileLineEdit.text())
        
    def validate(self):
        try:
            self.validateVolume()
            self.validateKey()
            self.create()
            self.accept()
        
        except ValidationError as e:
            QMessageBox.critical(self, "Validation Failed", str(e))
        
        except Exception as e:
            QMessageBox.critical(self, "FATAL ERROR", "Volume Creation FAILED!!!\n"+str(e))
            logger.report()
            
    @staticmethod
    def getNewLuksUI(parent=None):
        dialog = NewLuksUI(parent)
        result = dialog.exec_()
        return (result == QDialog.Accepted)

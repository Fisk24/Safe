import os, sys, json, getpass
#from tkinter      import *
#from tkinter.ttk  import *
from lib          import logger 

class Config:
	def __init__(self, cfile = "settings.json", cloc="."):
		self.default = [
			{
				"file"   : cfile,     # The name of the file responsable for storing configuration information
				"ver"    : "a1.0",    # Version number
				"efloc"  : cloc,  	  # Extra Files: Place to write config file and temp info
				"state"  : False,     # state of mounted device, 1 if open, 0 if closed.
				"debug"  : True,      # Enable dev features
				"eShell" : False,     # do or dont show the console when an error occurs; ONLY WHEN DEBUG IS ON
				"sShell" : False,     # do or dont show the console when the program starts; ONLY WHEN DEBUG IS ON
				"mpoint" : "/run/media/fisk/Safe"
			}
		]
		self.data    = []
		self.load()

	def __str__(self):
		x = ""
		for i in self.data:
			x += "Entry "+str(self.data.index(i))+": \n"
			for j in i:
				x += "\t"+j+" : "+str(i[j])+"\n"
		return x

	def save(self):
		with open(self.default[0]["efloc"]+"/"+self.default[0]["file"], 'w') as file:
			json.dump(self.data, file)

	def load(self):
		try:
			with open(self.default[0]["efloc"]+"/"+self.default[0]["file"], 'r') as file:
				self.data = json.load(file)
			logger.out("Loaded settings...", 0)

		except FileNotFoundError:
			logger.out("Configuration not found. Will create a new one.", 0)
			self.gen()
			self.load()

		except Exception as e:
			logger.out("Failed to load configuration, could not continue...")
			logger.out(e)
			sys.exit()

	def gen(self):
		'''
		if sys.platform == "linux":
			self.default[0]["dlloc"] = "/home/"+getpass.getuser()+"/Desktop/NOT_PORN_GO_AWAY"
		elif sys.platform == "win32":
			self.default[0]["dlloc"] = "C:/Users/"+getpass.getuser()+"/Desktop/NOT_PORN_GO_AWAY"
		'''
		with open(self.default[0]["efloc"]+"/"+self.default[0]["file"], 'w') as file:
			json.dump(self.default, file)
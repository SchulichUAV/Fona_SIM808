import time
import serial
import os
import datetime

class at_parser:
	def __init__(self, port='/dev/ttyUSB0', logstate=True, logfile='log.txt'):
		self.serconn = serial.Serial(port=port, baudrate=115200, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
		self.logging = logstate
		self.file = logfile
		self._logclear()
		self.cont = True
		self.apn_config = False
		self.flag = True

	def _logclear(self):
		open('logfile', 'w').close()

	def _log(self, instr):
		with open(self.filename, 'a') as f:
			f.write(instr)
		f.close()

	def _print(self, instr):
		print(instr)
		self._log(instr.rstrip() + '\n')

	def _error(self, command, error):
		self._print('Error: system responded with:\n' + error.rstrip() + '\nTo the command:\n' + command.rstrip())

	def _strcheck(self, instr):
		if type(instr) == str:
			instr = instr.rstrip() + '\r\n'
			return bytes(instr.encode("utf8"))
		elif type(instr) == bytes:
			return instr
		else:
			return None

	def _write(self, instr):
		wrtln = self._strcheck(instr)
		if wrtln == None:
			self._print('Error: write did not recieve a string')
		else:
			self.serconn.write(wrtln)

	def _read(self, instr):
		rdline = ''
		time.sleep(0.5)
		while self.serconn.inWaiting() > 0:
			lnin = ser.read(1)
			lnin = lnin.decode("utf8")
			if lnin != '':
				rdline += lnin

		if rdline.find('ERROR') != -1:
			self._error(instr, rdline)
			return False
		elif rdline != ''
			self._print(rdline)
			return rdline
		else:
			self._print("No response recieved: ensure the device is connected, powered and on the correct port")
			return False

	def executewithaction(self, instr, expect=None):
		self._write(instr)
		o = self._read(instr)
		if o == False:
			self.cont = False
			self.flag = False
		elif expect != None:
			if o.find(expect) != -1:
				self._print("Expect Passed")
				self.cont = True
		else:
			self.cont = True
		if self.cont == True:
			1
			#DO STUFF TO PIXHAWK IF o CONTAINS COMMANDS

	def execute(self, instr, expect=None):
		self._write(instr)
		o = self._read(instr)
		if o == False:
			self.cont = False
			self.flag = False
		elif expect != None:
			if o.find(expect) != -1:
				self._print("Expect Passed")
				self.cont = True
		else:
			self.cont = True

	def loadcommandfile(self, path):
		try:
			with open(path, 'r') as f:
				self.commands = f.readlines()
			f.close()
		except IOError:
			fona_print('Error reading file')
			self.commands = None

	def loaddata(self, path):
		try:
			with open(path, 'r') as f:
				self.data = f.readlines()
			f.close()
		except IOError:
			fona_print('Error reading file')
			self.data = None

	def sms(self, number, message):
		self.execute('AT+CMGF=1', 'OK')
		self.execute('AT+CMGS="' + number + '"')
		self.execute(message + chr(26))

	def configure_apn(self, APN, USER='', PASS=''):
		self.apn = APN
		self.username = USER
		self.password = PASS
		self.apn_config = True

	def datastream(self, URL, datafile):
		if self.apn_config == True:
			self.execute('AT', 'OK')
			self.execute('AT+CGATT=1')
			self.execute('AT+CIPSHUT', 'SHUT OK')
			self.execute('AT+CIPSTATUS', 'INITIAL')
			self.execute('AT+SAPBR=3,1,"APN","' + self.apn + '"')
			self.execute('AT+CSTT="' + self.apn + '","' + self.username + '","' + self.password + '"')
			self.execute('AT+SAPBR=3,1,"USER","' + self.username + '"')
			self.execute('AT+SAPBR=3,1,"PWD","' + self.password + '"')
			self.execute('AT+SAPBR=1,1', 'OK')
			self.execute('AT+CIICR', 'OK')
			self.execute('AT+CIFSR')
			self.execute('AT+HTTPINIT', 'OK')
			self.execute('AT+HTTPPARA="CID",1')
			self.execute('AT+HTTPPARA="UA","PYAT"')
			self.execute('AT+HTTPPARA="URL","' + URL + '"')
			self.execute('AT+HTTPPARA="CID",1')
			while self.flag == True:
				#REPLACE THIS AND ASSIGN PIXHAWK TELEMETRY STUFF TO self.data
				loaddata(datafile)
				if self.data != None
					self.execute('AT+HTTPDATA=' + str(len(' '.join(self.data))) + ',5000')
					self.execute(' '.join(self.data), 'OK')
					time.sleep(5)
					self.execute('AT+HTTPACTION=1')
					self.executewithaction('AT+HTTPREAD')
				else
					self.flag = False


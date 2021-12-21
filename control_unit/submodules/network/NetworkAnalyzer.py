import subprocess
import re
import threading
import time
import sys
import os
from control_unit.submodules.network.ExceptionHandler import *
import pickle

# Import database functionality
from control_unit.submodules.database.database_DONE import Database

ITERATIONS = 1
TIMELIMIT = 2
myLuck = threading.Condition()


class ThroughputBuffer:
	"""Ringbuffer fpr throughput sampling"""

	def __init__(self, maxSize):
		self.max = maxSize
		self.content = []

	class __Full:
		def append(self, x):
			self.content[self.cur] = x
			self.cur = (self.cur+1) % self.max

		def get(self):
			return f'Buffercontent: {self.content}'

		def getVal(self):
			return self.content

	def append(self, x):
		self.content.append(x)
		if len(self.content) == self.max:
			self.cur = 0
			self.__class__=self.__Full

	def getVal(self):
		return self.content

	def get(self):
		return f'Buffercontent: {self.content}'

Buffer = ThroughputBuffer(12)


class NAsM:
	"""Network Analyzer"""
	FinalList = []
	def __init__(self, lock, Buffer, db):
		self.lock = lock
		self.Buffer = Buffer
		self.db = db

	def getData(self):
		self.mcC = "iw wlan0 station dump"
		self.nwC = "vnstat -tr 5 -i wlan0"
		self.mcD = subprocess.Popen([self.mcC], shell=True, stdout = subprocess.PIPE).communicate()[0]
		self.mcD = self.mcD.decode("utf-8")
		self.nwD = subprocess.Popen([self.nwC], shell=True, stdout = subprocess.PIPE).communicate()[0]
		self.nwD = self.nwD.decode("utf-8")

		return self.mcD, self.nwD

	def cleanUp(self, dataString: str, networkData: str):
		"""Remove unwanted data from string"""

		self.ParsedData = []

		# Network Analyzer
		self.Mbit_flag = False
		self.kbit_flag = False
		self.bit_flag = False

		networkData = re.split("\n", networkData)
		networkData = [networkData[4]]
		self.counter = 0
		for data in networkData:
			data = re.split("(\s+)", data)
			self.holdVal = 0
			for content in data:
				self.match = re.search(r'(\s+)', content)
				if self.match:
					del data[self.holdVal]
				self.holdVal += 1
			self.counter += 1

		if data[data.index("tx")+1] != "":
			self.ParsedData.append(data[data.index("tx")+1])
			#print("Throughput: {}".format(data[data.index("tx")+1]))
		else:
			self.ParsedData.append(0)


		if data[data.index("tx")+2] == "Mbit/s":
			self.Mbit_flag = True
		elif data[data.index("tx")+2] == "kbit/s":
			self.kbit_flag = True
		elif data[data.index("tx")+2] == "bit/s":
			self.bit_flag = True
		else:
			self.content = data[data.index("tx")+2]
			raise FlagNotRaisedError(self.content)

		# MAC Address
		dataString = re.sub("\t", "", dataString)
		dataString = re.sub("\(on wlan0\)", "", dataString)
		dataString = re.split("(?=Station)", dataString)

		del dataString[0]
		self.counter = 0
		for data in dataString:
			self.counter += 1
			self.macSearch = re.search(r'Station (\S+)', data)
			if self.macSearch:
				self.mac = self.macSearch.group(1)
				self.ParsedData.append(self.mac.upper())
				#print("MAC: {}".format(self.mac))

		return self.ParsedData, self.Mbit_flag, self.kbit_flag, self.bit_flag

	def convert2Bit(self, data: list, MFlag: bool, KFlag: bool, bFlag: bool):
		"""Convert from Mbit or kbit to bit"""

		self.bit = float(data[0])
		if MFlag:
			self.bit = self.bit * 1000000
		elif KFlag:
			self.bit = self.bit * 1000
		elif bFlag:
			self.bit = self.bit
		else:
			raise UnknownTypeError(self.bit)


		Buffer.append(self.bit)
		#data[0] = int(bit)
		data[0] = int(sum(Buffer.getVal())/len(Buffer.getVal()))
		return data

	def SendData(self):
		"""Send gathered data to database"""
		#db.insert_query('NH', data)
		self.lortepis = 1
		while True:
			myLuck.acquire()
			if self.lortepis == 0:
				#myLuck.wait()
				print(f'Network | Collected data:	 {self.FinalList}') 
				filename = '/dev/shm/networkjar'
				data = {"MAC":self.FinalList[1:],"bits":self.FinalList[0]}
				serialized = pickle.dumps(data)
				with open(filename, 'wb') as file_object:
					file_object.write(serialized)
				
				#self.db.insert_query('NH',self.FinalList)
			myLuck.notify()
			myLuck.release()
			self.lortepis = (self.lortepis+1) % TIMELIMIT
			time.sleep(0.5)


	def RecieveData(self):
		while True:
			myLuck.acquire()
			self.mcD, self.nwD = self.getData()
			self.data, self.Mbit, self.kbit, self.bit = self.cleanUp(self.mcD, self.nwD)
			self.FinalList = self.convert2Bit(self.data, self.Mbit, self.kbit, self.bit)
			#print(f'Data received: {Buffer.get()}')
			#myLuck.notify()
			myLuck.release()
			time.sleep(0.5)
			#variable = db.get_network_bits()
			#print(f'Database output: {variable}')



	def Run(self):
		# for x in range(1, ITERATIONS):
		# 	print(f'Iteration: {x} out of {ITERATIONS-1}')
		# 	self.mcD, self.nwD = self.getData()
		# 	self.data, self.Mbit, self.kbit, self.bit = self.cleanUp(self.mcD, self.nwD)
		# 	self.FinalList = self.convert2Bit(self.data, self.Mbit, self.kbit, self.bit)
		# 	print(self.FinalList)
		# 	self.SendData(self.FinalList)
		# 	print(Buffer.get())
		# 	print("-----------------------------------------------------------------------------------------")
		#db = Database('DB', 'localhost', 'admin', 'root')
		Buffer = self.Buffer
		myLuck = self.lock
		t1 = threading.Thread(target=self.RecieveData)
		t2 = threading.Thread(target=self.SendData)
		t1.start()
		t2.start()

		t1.join()
		t2.join()

		db.disconnect_db()

def MainLoop():
	while True:
		Buffer = ThroughputBuffer(12)
		Analyzer = NAsM()


if __name__ == "__main__":
	db = Database('DB', 'localhost', 'admin', 'root')
	Buffer = ThroughputBuffer(12)
	myLuck = threading.Condition()
	Analyzer = NAsM(myLuck, Buffer, db)

	t1 = threading.Thread(target=Analyzer.RecieveData)
	t2 = threading.Thread(target=Analyzer.SendData)
	t1.start()
	t2.start()

	t1.join()
	t2.join()

	db.disconnect_db()

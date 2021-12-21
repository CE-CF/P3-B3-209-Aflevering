import subprocess
import re
import time
from control_unit.submodules.network.ExceptionHandler import *

BUFFERSIZE = 800
TIMELIMIT = 1
tx_dict = {}
rx_dict = {}

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


class NAsM:
	"""Network Analyzer"""
	FinalList = []

	def getData(self):
		self.mcC = "iw wlan0 station dump"
		self.nwC = "vnstat -tr 5 -i eth0"
		self.mcD = subprocess.Popen([self.mcC], shell=True, stdout = subprocess.PIPE).communicate()[0]
		self.mcD = self.mcD.decode("utf-8")
		self.nwD = subprocess.Popen([self.nwC], shell=True, stdout = subprocess.PIPE).communicate()[0]
		self.nwD = self.nwD.decode("utf-8")

		return self.mcD, self.nwD

	def getBits(self, data, val: str):
		if data[data.index(val)+2] == "Mbit/s":
			self.Mbit_flag = True
		elif data[data.index(val)+2] == "kbit/s":
			self.kbit_flag = True
		elif data[data.index(val)+2] == "bit/s":
			self.bit_flag = True
		else:
			self.content = data[data.index("tx")+2]
			raise FlagNotRaisedError(self.content)

	def cleanUp(self, dataString: str, networkData: str):
		"""Remove unwanted data from string"""

		self.ParsedData = []

		# Network Analyzer
		self.Mbit_flag = False
		self.kbit_flag = False
		self.bit_flag = False

		networkData = re.split("\n", networkData)
		networkData = [networkData[3:]]
		self.counter = 0
		for entries in networkData:
			for data in entries:
				data = re.split("(\s+)", data)
				self.holdVal = 0
				for content in data:
					self.match = re.search(r'(\s+)', content)
					if self.match:
						del data[self.holdVal]
					self.holdVal += 1
				self.counter += 1
				print(f'Datastring: {data}')
				if "tx" in data:
					self.txF = True
					self.rxF = False
					if data[data.index("tx")+1] != "":
						print(f'tx value: {data[data.index("tx")+1]}')
				elif "rx" in data:
					self.rxF = True
					self.txF = False
					if data[data.index("rx")+1] != "":
						print(f'rx value: {data[data.index("rx")+1]}')
				else:
					self.rxF = False
					self.txF = False
					print(f'Nothing interesting in {data}')

		self.tpValue = 0
		if self.txF:
			self.txVal = data[data.index("tx")+1]
			print(f'TX Value: {self.txVal}')
			tx_dict = {data[data.index("tx")+1]: data[data.index("tx")+2]}
			print(f'tx dict: {tx_dict}')

			#self.ParsedData.append(data[data.index("tx")+1])
			#print("Throughput: {}".format(data[data.index("tx")+1]))
		elif self.rxF:
			self.rxVal = data[data.index("rx")+1]
			print(f'RX Value: {self.rxVal}')
			rx_dict = {data[data.index("rx")+1]: data[data.index("rx")+2]}
			print(f'rx dict: {rx_dict}')

		else:
			print("======================================================")
			#self.ParsedData.append(0)


		if self.txF:
			self.getBits(data, "tx")
		elif self.rxF:
			self.getBits(data, "rx")
		else:
			print("Nothing interesting")

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

	def Finalize(self):
		Output = int(sum(Buffer.getVal())/len(Buffer.getVal()))
		return f'Test result: {Output}'

	def RecieveData(self):
		self.mcD, self.nwD = self.getData()
		self.data, self.Mbit, self.kbit, self.bit = self.cleanUp(self.mcD, self.nwD)
		self.data.pop(0)
		
		self.SensorList = self.data
		self.RunTime = time.time() + TIMELIMIT*60
		
		print(f'Initializing test....')
		print(f'Runtime (min): {TIMELIMIT}')
		print(f'Connected Devices: {self.data}')
		
		while time.time() < self.RunTime:
			self.mcD, self.nwD = self.getData()
			self.data, self.Mbit, self.kbit, self.bit = self.cleanUp(self.mcD, self.nwD)
			if self.data[1:] == self.SensorList:
				self.FinalList = self.convert2Bit(self.data, self.Mbit, self.kbit, self.bit)
			else:
				raise ExternalDeviceError(self.data[1:])
			time.sleep(1)

		#self.Finalize()


if __name__ == "__main__":
	Buffer = ThroughputBuffer(BUFFERSIZE)
	Analyzer = NAsM()
	Analyzer.RecieveData()
	print(Analyzer.Finalize())

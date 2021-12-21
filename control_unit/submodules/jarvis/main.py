import time
import pickle
from datetime import datetime
from control_unit.submodules.database.database_DONE import Database
from control_unit.submodules.jarvis.ErrorHandler import *
from control_unit.submodules.power_supply.power_supply import recv

BIT_LOWER = 8415
BIT_UPPER = 5000000

class Jarvis:
	CanRun = True
	db = Database("DB", "localhost", "admin", "root")
	FileName = '/dev/shm/picklejar'
	RoomNames = ["room1", "room2", "room3", "room4", "room5"]
	NumRooms = len(RoomNames)
	Pause = 5
	TempRooms = [0]*NumRooms
	LockTime = [False]*NumRooms
	Weights = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
	BufferWeights = [[2,0], [0,1], [1,0], [0,2]]
	WeightIdx = 0
	treshold = 2
	Motion = None
	MAC = None
	TP = None
	lastFlag = True
	guiFlag = False


	def Retreive(self):
		self.timeScheme = self.db.get_time_schema()
		# ! pickle shared memory alternative
		#self.motion_data = self.db.get_motion_data()
		self.motion_data = self.AccessSHM("Sensor")["sensor"]
		#self.MAC_data = self.db.get_active_mac()
		active_mac_DB = self.db.get_active_mac_str()
		networksData = self.AccessSHM("Network")
		active_mac_network = networksData["MAC"]

		self.MAC_data = False
		for idx, mac in enumerate(active_mac_DB):
			for x in range(len(active_mac_network)):
				if mac == active_mac_network[x]:
					self.MAC_data = True
		
		self.TP_data = networksData["bits"]
		#self.TP_data = self.db.get_network_bits()

		return self.timeScheme, self.motion_data, self.MAC_data, self.TP_data

	def Process(self, motion_data, MAC_data, TP_data):
		print(f'JARVIS - Motion data: {motion_data}')
		if any(motion_data):
			self.Motion = 1
		else:
			self.Motion = 0

		if MAC_data:
			self.MAC = 1
		else:
			self.MAC = 0

		print(f'JARVIS - TP Data: {TP_data}')
		print(f'JARVIS - TP Type: {type(TP_data)}')
		if TP_data > BIT_LOWER:
			if TP_data >= BIT_UPPER:
				self.TP = 1
			else:
				self.TP = (TP_data-BIT_LOWER)/(BIT_UPPER-BIT_LOWER)
		else:
			self.TP = 0

	def GetWeights(self, timeScheme):
		WorkStartStr, WorkEndStr = str(timeScheme[0]).split(".")
		BedtimeStr, WakeUpStr = str(timeScheme[1]).split(".")

		WorkStart = int(WorkStartStr)
		WorkEnd = int(WorkEndStr)
		Bedtime = int(BedtimeStr)
		WakeUp = int(WakeUpStr)

		TransitionTime = [WorkStart, WorkEnd, Bedtime, WakeUp]

		# Get current time
		time = datetime.now()
		floatTimeMin = str((time.minute/60))
		floatTimeMinIdx = floatTimeMin.find(".")
		floatTime = float(str(time.hour) + "." + floatTimeMin[(floatTimeMinIdx + 1):])

		# Iterate through every index in TransitionTime[]
		for idx, t in enumerate(TransitionTime):
			timeDifference = floatTime - float(t)

			# If the current time is within one of the four buffer periods
			if (timeDifference >= -0.5 and timeDifference <= 0.5 and type(self.BufferWeights[idx][0]) is not int):

				# Buffer transition time passed (0-60 minutes -> 0-100 int)
				bufferStartFloatTime = float(str(t-1) + ".5")
				bufferTimePassed = floatTime - bufferStartFloatTime

				# (weight from) - (weight to)
				print(self.BufferWeights)
				weightDifference0 = self.BufferWeights[idx][0][0] - self.BufferWeights[idx][1][0]
				weightDifference1 = self.BufferWeights[idx][0][1] - self.BufferWeights[idx][1][1]
				weightDifference2 = self.BufferWeights[idx][0][2] - self.BufferWeights[idx][1][2]

				# Current buffer weight is calculated
				bufferWeight0 = self.BufferWeights[idx][0][0] - (weightDifference0 * bufferTimePassed)
				bufferWeight1 = self.BufferWeights[idx][0][1] - (weightDifference1 * bufferTimePassed)
				bufferWeight2 = self.BufferWeights[idx][0][2] - (weightDifference2 * bufferTimePassed)

				return [bufferWeight0, bufferWeight1, bufferWeight2]

		else:
			if time.hour >= WorkStart and time.hour < WorkEnd:
				# Work Weights
				return [self.Weights[1][0], self.Weights[1][1], self.Weights[1][2]]
			elif time.hour >= Bedtime and time.hour < WakeUp:
				# Sleep Weights
				return [self.Weights[2][0], self.Weights[2][1], self.Weights[2][2]]
			else:
				# Home Weights
				return [self.Weights[0][0], self.Weights[0][1], self.Weights[0][2]]

	def Probability(self, MotionWeight, MacWeight, TPWeight):
		return self.Motion * MotionWeight + self.MAC * MacWeight + self.TP * TPWeight

	def Determine(self, prob_value):
		print(f'Probability: {prob_value}')
		if prob_value >= self.treshold:
			self.Flag = True
			return [1,1,1,1,1]
		else:
			self.Flag = False
			return [0,0,0,0,0]

	def AccessSHM(self, module, rw=None):
		if module == "Communication":
			filename = '/dev/shm/picklejar'
			if rw == 'rb':
				#print('in rb')
				with open(filename, rw) as FileObject:
					RawData = FileObject.read()

				Shared = pickle.loads(RawData)
				print(f'Jarvis: Shared memory | {module} | {Shared}')
			else:
				#print('in wb')
				Data = {}
				Shared = pickle.dumps(Data)			# check if Data can just be ""

				with open(filename, rw) as FileObject:
					FileObject.write(Shared)

			return Shared
	
		if module == "Sensor":
			filename = '/dev/shm/sensorjar'
			#print('in rb')
			with open(filename, 'rb') as FileObject:
				RawData = FileObject.read()

			Shared = pickle.loads(RawData)
			print(f'Jarvis: Shared memory | {module} | {Shared}')	
			
			return Shared

		if module == "Network":
			filename = '/dev/shm/networkjar'
			#print('in rb')
			with open(filename, 'rb') as FileObject:
				RawData = FileObject.read()

			Shared = pickle.loads(RawData)
			print(f'Jarvis: Shared memory | {module} | {Shared}')
			
			return Shared	

	def CheckSHM(self, Shared):
		if Shared:
			if "All" in Shared:
				for idx in range(self.NumRooms):
					now = int(datetime.now().timestamp())
					if ((now-self.LockTime[idx]) < self.Pause) and (self.LockTime[idx] is not False) and (self.TempRooms[idx] == Shared["All"]):
						if Shared["All"] == 0:
							self.TempRooms[idx] = 0
							self.LockTime[idx] = False
					else:
						self.TempRooms[idx] = Shared["All"]
						self.LockTime[idx] = int(datetime.now().timestamp())
			else:
				for idx, room in enumerate(self.RoomNames):
					if room in Shared:
						now = int(datetime.now().timestamp())
						if ((now-self.LockTime[idx]) < self.Pause) and (self.LockTime[idx] is not False) and (self.TempRooms[idx] == Shared[room]):
							self.TempRooms[idx] = 0
							self.LockTime[idx] = False
					
						else:
							self.TempRooms[idx] = Shared[room]
							self.LockTime[idx] = int(datetime.now().timestamp())

			self.AccessSHM("Communication", 'wb')

	def Execute(self, PowerState):
		print(f'Jarvis: TempRooms 	| {self.TempRooms}')
		print(f'Jarvis: LockTime 	| {self.LockTime} ')
		
		if any(self.LockTime):

			for idx, time in enumerate(self.LockTime):
				now = int(datetime.now().timestamp())
				if ((now-time) < self.Pause) and (time is not False):
					print(f'Jarvis: compariong TempRooms[{idx}]: {self.TempRooms[idx]} != PowerState[{idx}]: {PowerState[idx]}')
					if self.TempRooms[idx] != PowerState[idx]:
						print(f'Jarvis: TempRooms[{idx}] : {self.TempRooms[idx]}')
						PowerState[idx] = self.TempRooms[idx]
						self.guiFlag = self.Flag
					else:
						self.TempRooms[idx] = 0
						self.LockTime[idx] = False
						self.db.power_room(idx+1, PowerState[idx])

						# ! Måske skal der sendes signal til power supply her 
						"""
						if PowerState == 0:
							recv(False, [idx+1])
						else:
							recv(True, [idx+1])
						"""
						
				else:
					self.TempRooms[idx] = 0
					self.LockTime[idx] = False
					self.db.power_room(idx+1, PowerState[idx])
					
					# ! Måske skal der sendes signal til power supply her 
					"""
					if PowerState == 0:
						recv(False, [idx+1])
					else:
						recv(True, [idx+1])
					"""
		"""
		print(f'Jarvis: PowerState before db insert {PowerState}')
		if (self.lastFlag == self.Flag) or (self.Flag == self.guiFlag):
			print(f'(JARVIS) Lastflag: {self.lastFlag}, Flag: {self.Flag}')
			for idx, ps in enumerate(PowerState):

				now = int(datetime.now().timestamp())
				if ps == 0:
					if ((now-self.LockTime[idx]) < self.Pause) and (self.LockTime[idx] is not False):
						print(f'Jarvis: Turning off Room{idx} | Giving back to Jarvis in {self.Pause-(now-self.LockTime[idx])}')
						self.db.power_room(idx+1, ps)
						recv(False, [idx+1])
					else:
						print(f'Jarvis: Turning off Room{idx}')
					
				else:
					if ((now-self.LockTime[idx]) < self.Pause) and (self.LockTime[idx] is not False):
						print(f'Jarvis: Turning on Room{idx} | Giving back to Jarvis in {self.Pause-(now-self.LockTime[idx])}')
						self.db.power_room(idx+1, ps)
						recv(True, [idx+1])
					else:
						print(f'Jarvis: Turning on Room{idx}')
		else:
			print(f'(JARVIS) Lastflag: {self.lastFlag}, Flag: {self.Flag}')
			for idx, ps in enumerate(PowerState):
				if ps == 0:
					self.db.power_room(idx+1, ps)
					recv(False, [idx+1])
				else: 
					self.db.power_room(idx+1, ps)
					recv(True, [idx+1])
		print("")
		"""
		print(f'Jarvis: PowerState before db insert {PowerState}')
		
		print(f'(JARVIS) Lastflag: {self.lastFlag}, Flag: {self.Flag}')
		for idx, ps in enumerate(PowerState):

			now = int(datetime.now().timestamp())
			if ps == 0:
				if ((now-self.LockTime[idx]) < self.Pause) and (self.LockTime[idx] is not False):
					print(f'Jarvis: Turning off Room{idx} | Giving back to Jarvis in {self.Pause-(now-self.LockTime[idx])}')
					self.db.power_room(idx+1, ps)
					recv(False, [idx+1])
				else:
					print(f'Jarvis: Turning off Room{idx}')
					if (self.lastFlag == self.Flag) or (self.guiFlag == self.Flag):
						recv(False, [idx+1])
				
			else:
				if ((now-self.LockTime[idx]) < self.Pause) and (self.LockTime[idx] is not False):
					print(f'Jarvis: Turning on Room{idx} | Giving back to Jarvis in {self.Pause-(now-self.LockTime[idx])}')
					self.db.power_room(idx+1, ps)
					recv(True, [idx+1])
				else:
					print(f'Jarvis: Turning on Room{idx}')
					if (self.lastFlag == self.Flag) or (self.guiFlag == self.Flag):
						recv(True, [idx+1])
	
		print(f'(JARVIS) Lastflag: {self.lastFlag}, Flag: {self.Flag}')
		for idx, ps in enumerate(PowerState):
			if ps == 0:
				self.db.power_room(idx+1, ps)
				recv(False, [idx+1])
			else: 
				self.db.power_room(idx+1, ps)
				recv(True, [idx+1])
		print("")


		
		self.lastFlag = self.Flag

	def Run(self):
		while self.CanRun:
			timeScheme, motion_data, MAC_data, TP_data = self.Retreive()
			self.Process(motion_data, MAC_data, TP_data)
			currentWeights = self.GetWeights(timeScheme)
			self.value = self.Probability(currentWeights[0], currentWeights[1], currentWeights[2])
			# Set power state based on probability
			PowerState = self.Determine(self.value)
			print(f'Jarvis: PowerState = {PowerState}')
			Shared = self.AccessSHM("Communication", 'rb')
			self.CheckSHM(Shared)
			self.Execute(PowerState)

			time.sleep(1)


if __name__ == "__main__":

	JARVIS = Jarvis()
	JARVIS.Run()

#!/usr/bin/env python3
from control_unit.communication.coms import app as backend
from control_unit.gui.run import run_gui
from control_unit.submodules.network.NetworkAnalyzer import NAsM, myLuck, Buffer
from control_unit.submodules.database.database_DONE import Database
from threading import Thread
import argparse
import pickle

db = Database('DB', 'localhost', 'admin', 'root')
gui_thread = Thread(target=run_gui)
run_networkAnalyzer = NAsM(myLuck, Buffer, db)
NetworkAnalyzer_thread = Thread(target=run_networkAnalyzer.Run)

def start_gui():
	print("Create GUI thread")

	print("Starting GUI thread")

	gui_thread.join()

def create_shm():
	
	print("Creating /dev/shm/picklejar")
	filename = '/dev/shm/picklejar'
	data = {}
	serialized = pickle.dumps(data)
	with open(filename, 'wb') as file_object:
		file_object.write(serialized)

	print("Creating /dev/shm/sensorjar")
	filename = '/dev/shm/sensorjar'
	data = {"sensor":[0,0,0,0,0]}
	serialized = pickle.dumps(data)
	with open(filename, 'wb') as file_object:
		file_object.write(serialized)

	print("Creating /dev/shm/networkjar")
	filename = '/dev/shm/networkjar'
	data = {"MAC":[],"bits":0}
	serialized = pickle.dumps(data)
	with open(filename, 'wb') as file_object:
		file_object.write(serialized)

def main():
	create_shm()
	from control_unit.submodules.jarvis.main import Jarvis
	parser = argparse.ArgumentParser()
	parser.add_argument("--gui", action="store_true")
	parser.add_argument("--nw", action="store_true")
	args = parser.parse_args()
	print("Creating Back-end thread")
	backend_thread = Thread(target=backend.run,
							kwargs={
								'host':"0.0.0.0",
								'port':8000
							})
	print("Starting Back-end...")
	print("Creating Network Analyzer")

	print("Creating Jarvis")
	jarvis = Jarvis()
	try:
		print("Creating Jarvis thread")
		jarvis_thread = Thread(target=jarvis.Run)	
		
		print("Starting Jarvis...")	
		jarvis_thread.start()
		backend_thread.start()
		if args.gui:
			print("Starting GUI...")
			gui_thread.start()
		if args.nw:
			print("Starting Network Analyzer...")
			NetworkAnalyzer_thread.start()
		
	except KeyboardInterrupt:
		jarvis.CanRun = False
		backend_thread.join()
		if args.nw:
			NetworkAnalyzer_thread.join()
		jarvis_thread.join()
	

if __name__ == '__main__':
    main()

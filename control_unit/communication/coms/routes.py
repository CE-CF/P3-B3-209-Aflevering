from control_unit.communication.coms import app, db#, bcrypt
from flask import render_template, url_for, flash, redirect, request, jsonify, json
import requests as req
import datetime
from flask_login import login_user, current_user, logout_user
import pickle
import time
#from control_unit.communication.coms.forms import RegistrationForm, LoginForm, UserInputForm
#from control_unit.communication.coms.models import User, UserInput, SensorData
#from ...submodules.database.database_DONE import Database
# gui server
url = 'http://127.0.0.1:5000'

# Smarthouse specifications
num_rooms = 5

# Defining the home page of our site
@app.route("/") # the "/" set the route to current page
def home():
	return render_template("index.html", head="Smart-house", content="Super awesome communication module") # basic inline html for testing

# Adding a dynamic URL, creating output based on url
"""
@app.route("/<usr>", methods=['GET'])
def user(usr):
	if current_user.is_authenticated:
		user = User.query.filter_by(username=usr).first()
		user_input = UserInput.query.filter_by(user_id=user.id).first()
		return render_template("user.html", title=usr, head=usr, user_input=user_input)
	else:
		return render_template("index.html", title=usr, head=usr, content=f"Er det Faurs lille {usr}-mus?!")

# Adding a redirect url to troll P3-B3-209
@app.route("/taber")
def taber():
	return "<h1> Lol nice try hacker <h1>"

# Redirecting from a url to another url
@app.route("/admin")
def admin():
	return redirect(url_for("user", usr="Admin!"))

# Creating a way to register new users
@app.route("/register", methods=['GET','POST'])
def register():
	# Check to see if the user is already logged in, if yes redirect to home page
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	# If registered swap to home page and display success message
	if form.validate_on_submit():
		# Hashing the password input
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		# Creating and input for the user table and commit to table
		user = User(username=form.username.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Account created for {form.username.data}!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

# Testing GET and POST
@app.route("/login", methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	# If login successful swap to home page and display succes message
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		# check if password input matches the users password in the database
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			flash(f'{user.username} has been logged in!', 'success')
			return redirect(url_for('home'))
		else:
			flash(f'login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	if current_user.is_authenticated:
		logout_user()
		return redirect(url_for("home"))
	return redirect(url_for("home"))

@app.route("/User-<usr>", methods=['GET','POST'])
def userinput(usr):
	form = UserInputForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=usr).first()
		exists = UserInput.query.filter_by(user_id=user.id).first()
		if exists:
			DB
			Update user input in the database

			exists.mac = form.mac.data
			exists.work_start = form.work_start.data
			exists.work_end = form.work_end.data
			exists.sleep_start = form.sleep_start.data
			exists.sleep_end = form.sleep_end.data
			db.session.commit()
			flash(f'Data for {user.username} succesfully updated!', 'success')
			return redirect(url_for('home'))
		else:
			DB
			Create new row with the new user input

			user_input = UserInput(mac=form.mac.data, work_start=form.work_start.data, work_end=form.work_end.data, sleep_start=form.sleep_start.data, sleep_end=form.sleep_end.data, user_id=user.id)
			db.session.add(user_input)
			db.session.commit()
			flash(f'Data for {user.username} succesfully created!', 'success')
			return redirect(url_for('home'))
	return render_template('userinput.html', title=usr, form=form)
"""
@app.route("/api/sensor/<sensor_id>", methods=['POST'])
def sensor(sensor_id):
	if request.method =='POST':
		

		sensor = str(sensor_id)
		sensor = sensor.replace("_", " ")
		print(f'Coms: Sensor der skriver {sensor}')
		data = request.form

		if (data.get("temp") != "nan") and (data.get("hum") != "nan"):
			temp = float(data.get("temp"))
			hum = int(float(data.get("hum")))
			mot = int(data.get("mot"))
			insertData = (sensor, temp, hum, mot)
			print(f'coms: sensor data {insertData}')
			#db.insert_query("RH", insertData)

		elif (data.get("temp") == "nan") and (data.get("hum") == "nan"):
			print(f'coms: received temp & hum = "nan" from sensor')
			temp = 99.1
			hum = 125
			mot = int(data.get("mot"))
			insertData = (sensor, temp, hum, mot)
			print(f'coms: sensor data {insertData}')
			#db.insert_query("RH", insertData)

		elif (data.get("temp") == "nan"):
			print(f'coms: received temp = "nan" from sensor')
			temp = 99.1
			hum = int(float(data.get("hum")))
			mot = int(data.get("mot"))
			insertData = (sensor, temp, hum, mot)
			print(f'coms: sensor data {insertData}')
			#db.insert_query("RH", insertData)

		elif (data.get("hum") == "nan"):
			print(f'coms: received hum = "nan" from sensor')
			temp = float(data.get("temp"))
			hum = 125
			mot = int(data.get("mot"))
			insertData = (sensor, temp, hum, mot)
			print(f'coms: sensor data {insertData}')
			#db.insert_query("RH", insertData)
		
		db.insert_query("RH", insertData)

		#------- Alt over skal markeres ud ------------#

		rooms = ['Bathroom', 'Bedroom', 'Garage', 'Kitchen', 'Living room']

		for idx, room in enumerate(rooms):
		    if room == sensor:
		        index_value = idx
		        break

		print("Creating /dev/shm/sensorjar")
		filename = '/dev/shm/sensorjar'

		with open(filename, 'rb') as FileObject:
			RawData = FileObject.read()
		motion_list = pickle.loads(RawData)
		motion_list = motion_list["sensor"]
		motion_list[index_value] = int(data.get("mot"))
		data = {"sensor":motion_list}
		serialized = pickle.dumps(data)
		with open(filename, 'wb') as file_object:
			file_object.write(serialized)

		return 'ok', 200
	else:
		return 'failed', 404

@app.route("/api/gui/<sub>/", methods=['GET', 'POST'])
def gui(sub):
	if sub == 'power':
		if request.method =='GET':
			# ? Test me
			'''
			DB: return current status of rooms
			1. get all current status data
			2. format data to get only
				- room id
				- power state
			rooms_power_state = {
				'room1': True,
				'room2': True,
				'room3': False,
				'room4': True,
				'room5': True
			}
			'''

			room_names = ['room1', 'room2', 'room3', 'room4', 'room5']
			GetRoomState = []
			GetRoomState = db.get_power_state()
			print(f'Coms: GET | Database PowerState: {GetRoomState}')
			get_rooms_power_state = {}
			for i, room in enumerate(room_names):
				if GetRoomState[i] == 1:
					get_rooms_power_state[room] = True
				else:
					get_rooms_power_state[room] = False
			print(f'coms: GET | get_rooms_power_state {get_rooms_power_state}')
			"""
			#jsonify(success=True)
			message = {
			  'message': "OK",
			  'powerstate': get_rooms_power_state,
			  'status': 200
			}
			resp = jsonify(message)
			resp.status_code = 200
			resp.headers.add('Access-Control-Allow-Origin', '*')
			"""
			return get_rooms_power_state, 200

		elif request.method =='POST':

			room_names = ['room1', 'room2', 'room3', 'room4', 'room5']
			received_rooms_power_state = {}
			for i in range(5):
				#print(request.form.get(room_names[i]))
				if(request.form.get(room_names[i]) == 'True'):

					received_rooms_power_state[room_names[i]] = True
				else:
					received_rooms_power_state[room_names[i]] = False
			print(f'coms: POST | received_rooms_power_state: {received_rooms_power_state}')
			# TODO Jarvis skal tilføjes til backend
			'''
			------------ Back End Server --------------
			To Jarvis: change power-status of room(s)
			1. update room(s) with id from request.form['rooms']
			2. return success or error response
			3. if error respons: try to forward the cmd to Jarvis again
			4. else: return success response with cmd just applied
			------------ Front End Server --------------
			5.
			'''
			PostRoomState = []
			PostRoomState = db.get_power_state()
			#print(f'Coms: POST | Current power_state {PostRoomState}')
			post_rooms_power_state = {}
			for i, room in enumerate(room_names):
				if PostRoomState[i] == 1:
					post_rooms_power_state[room] = True
				elif PostRoomState[i] == 0:
					post_rooms_power_state[room] = False
			print(f'Coms: POST | post_rooms_power_state: {post_rooms_power_state}')
			Current_keys = list(post_rooms_power_state.keys())
			Current_values = list(post_rooms_power_state.values())
			Received_keys = list(received_rooms_power_state.keys())
			Received_values = list(received_rooms_power_state.values())

			print(f'Coms: POST | Received_values: {Received_values}')
			print(f'Coms: POST | Current_values: {Current_values}')

			data = {}
			response_state = received_rooms_power_state
			counter = 0
			for i, value in enumerate(Current_values):
				if value is not Received_values[i]:
					if Received_values[i] == True:
 						data[Received_keys[i]] = 1
 						response_state[room_names[i]] = True
					else:
						data[Received_keys[i]] = 0
						response_state[room_names[i]] = False
					counter += 1

			if counter == 5:
				print('all(rv)', all(Received_values))
				if all(Received_values):
					data = {"All":1}
				elif any(Received_values) == False:
					data = {"All":0}

			#print(data)
			filename = '/dev/shm/picklejar'
			print(f'Coms: Shared data to be inserted: {data}')
			serialized = pickle.dumps(data)

			with open(filename,'wb') as file_object:
			    file_object.write(serialized)

			"""
			print(f'Coms: POST RESPONSE | response_state {response_state}')
			for i, key in enumerate(data):
				print(f'Coms: key: {key} | value: {data[key]}')
				db.power_room(i+1, data[key])
			"""

			return response_state, 200

	elif sub == 'history':
		if request.method =='GET':
			# ? Test me
			'''
			DB: return room history
			1. get all room history data
			2. format data to get only
				- time
				- room id
				- power state
				- temperature
				- humidity
			'''


			room_data = [0 for x in range(num_rooms)]
			power_data = [0 for x in range(num_rooms)]
			room = ['Bathroom', 'Bedroom', 'Garage', 'Kitchen', 'Living room']

			for i, roomID in enumerate(room):
				room_data[i], power_data[i] = db.get_plot_data(roomID)

			print(type(room_data))
			power_data_parsed = []
			for x in range(num_rooms):
				for room in room_data[x]:
					timestamp = room[0]
					timestamp = timestamp.strftime('%d-%m, %H:%M:%S')
					room[0] = timestamp

				for room in power_data[x]:
					room = list(room)
					timestamp = room[0]
					timestamp = timestamp.strftime('%d-%m, %H:%M:%S')
					room[0] = timestamp
					power_data_parsed.append(room)

			#print("Sorted samlet room_data")
			#print(room_data)

			#print("-------------------------")
			for x in range(num_rooms):
				#print("Room data:")
				#print(room_data[x])
				#print("Power data:")
				#print(power_data_parsed[x])
				for y in range(len(power_data_parsed)):
					room_data[x].extend([power_data_parsed[y]])
			for i in room_data:
				print(i)
			for x in range(num_rooms):
				roomNum = 1
				lastTemp = 0
				lastHum = 0
				lastPower = [0 for x in range(2)]
				for i, data in enumerate(room_data[x]):
					if  i == 0:
						if len(data) == 2:
							for sensordata in room_data[x]:
								if len(sensordata) != 2:
									lastTemp = sensordata[1]
									lastHum = sensordata[2]
									break
						else:
							for powerdata in room_data[x]:
								if len(powerdata) == 2:
									if powerdata[1] == 0:
										lastPower = 1
									else:
										lastPower = 0
									break

					if len(data) == 2:
						#print(f'Iteration {i}, power_data |> sidste temp {lastTemp}, sidste hum {lastHum}')
						data.insert(1, (x+1))
						data.insert(3, lastTemp)
						data.insert(4, lastHum)
						lastPower = data[2]
					else:
						#print(f'Iteration {i}, room_data |> sidste power {lastPower}')
						data.insert(1, (x+1))
						data.insert(2, lastPower)
						lastTemp = data[3]
						lastHum = data[4]

			house_data = []
			for x in range(num_rooms):
				house_data.extend(room_data[x])

			#print(house_data)
			house_data = sorted(house_data)

			#print("-------------------------")
			#print("Færdig formateret")
			#print(room_data)

			house_data_json = {"load":house_data}
			print(house_data_json)
			return house_data_json, 200

	elif sub == 'settings':
		if request.method =='GET':
			# ? Test me
			'''
			DB: return all user data
			1. get all user data
			2. format user data

			Formatering af json package:
			-------------------------
			test_user_data = {
				'user_data': [
					['G7:1A:Y2:4T:80:40', 8.16, 22.06],
					['00:1A:C2:7B:00:50', 8.15, 23.07]
				]
			}
			'''

			user_data = db.get_user_data()
			if user_data:
				for user in user_data:
					del user[0]

			else:
				user_data = ''

			user_json = {'user_data':user_data}
			action = 'User updated'
			return user_json, 200

		elif request.method == 'POST':
			# ? Test me
			mac_addr = request.form['mac_addr']
			work_start = int(request.form['work_start'])
			work_end = int(request.form['work_end'])
			sleep_start = int(request.form['bedtime'])
			sleep_end = int(request.form['wakeup_time'])

			'''
			DB: are the post-request data the same as the database data?
			1. get all user data
			2. for each mac-address in database, check if the
			request.form['mac_addr'] equal any of these
			3. if it doesn't: create new user
			4. if it does:
				5. does the other request.form info match the database data?
				6. if it doesn't: update the user/mac in database with new info
				7. if it does: don't update or add anything
			'''
			sleep_end = sleep_end/100
			sleep = sleep_start+sleep_end
			work_end = work_end/100
			work = work_start+work_end

			user_data = db.get_user_data()
			if user_data:
				for user in user_data:
					if user[1] == mac_addr:
						action = f'User {mac_addr} updated'
						break
					else:
						action = f'User {mac_addr} Created'
			else:
				action = 'First User Created'
			data = (mac_addr, work, sleep)
			db.insert_query("UI", data)

			return jsonify({'action': action}), 200
"""
@app.route("/database", methods=['GET'])
def database():
	users = User.query.all()
	userinputs = UserInput.query.all()
	sensordata = SensorData.query.all()


	return render_template('database.html', title="Database", head="Database", users=users, userinputs=userinputs, sensordata=sensordata)
	"""

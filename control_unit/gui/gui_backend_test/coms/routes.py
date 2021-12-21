from coms import app
from flask import render_template, flash, request, jsonify
import requests as req
import datetime

# gui server
url = 'http://127.0.0.1:5000'

# database
rooms_power_state = {
	'room1': True,
	'room2': True,
	'room3': False,
	'room4': True,
	'room5': True
}

@app.route("/api/gui/<sub>/", methods=['GET', 'POST'])
def gui(sub):
	global rooms_power_state
	if sub == 'power':
		if request.method =='GET':
			'''
			DB: return current status of rooms
			1. get all current status data
			2. format data to get only
				- room id
				- power state
			'''

			return rooms_power_state, 200

		elif request.method =='POST':

			room_names = ['room1', 'room2', 'room3', 'room4', 'room5']

			for i in range(5):
				if(request.form[room_names[i]] == 'True'):
					rooms_power_state[room_names[i]] = True
				else:
					rooms_power_state[room_names[i]] = False

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

			print(rooms_power_state)

			return rooms_power_state, 200

	elif sub == 'history':
		if request.method =='GET':
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
			dict_data = {
				"load": [
					['6-12, 13:45', 1, True, 24.1, 55.2],
					['6-12, 13:45', 2, False, 20.9, 48.2],
					['6-12, 13:45', 3, False, 21.2, 49.4],
					['6-12, 13:45', 4, True, 23.0, 44.7],
					['6-12, 13:45', 5, False, 22.8, 48.5],
					['6-12, 21:45', 1, True, 24.1, 55.2],
					['6-12, 21:45', 2, True, 20.9, 48.2],
					['6-12, 21:45', 3, False, 21.2, 49.4],
					['6-12, 21:45', 4, True, 23.0, 44.7],
					['6-12, 21:45', 5, False, 22.8, 48.5],
					['7-12, 13:50', 1, False, 22.1, 52.2],
					['7-12, 13:50', 2, True, 20.9, 48.0],
					['7-12, 13:50', 3, True, 21.2, 49.0],
					['7-12, 13:50', 4, True, 23.1, 44.9],
					['7-12, 13:55', 5, True, 22.7, 47.2],
					['7-12, 21:50', 1, False, 22.1, 52.2],
					['7-12, 21:50', 2, True, 20.9, 46.0],
					['7-12, 21:50', 3, True, 21.2, 49.0],
					['7-12, 21:50', 4, True, 23.1, 44.9],
					['7-12, 21:55', 5, True, 22.7, 48.2],
					['8-12, 13:55', 1, False, 22.1, 51.4],
					['8-12, 13:55', 2, True, 20.9, 47.8],
					['8-12, 13:55', 3, False, 21.4, 49.4],
					['8-12, 13:55', 4, False, 23.2, 44.4],
					['8-12, 13:55', 5, False, 22.5, 48.0],
					['8-12, 21:55', 1, False, 22.1, 51.4],
					['8-12, 21:55', 2, True, 20.9, 47.8],
					['8-12, 21:55', 3, False, 21.4, 49.4],
					['8-12, 21:55', 4, False, 23.2, 44.4],
					['8-12, 21:55', 5, False, 22.5, 48.0],
					['9-12, 14:00', 1, True, 22.1, 51.4],
					['9-12, 14:00', 2, False, 20.9, 47.8],
					['9-12, 14:00', 3, True, 21.4, 49.4],
					['9-12, 14:00', 4, True, 23.2, 44.4],
					['9-12, 14:00', 5, False, 22.5, 48.0],
					['9-12, 22:00', 1, True, 22.1, 51.4],
					['9-12, 22:00', 2, False, 20.6, 47.8],
					['9-12, 22:00', 3, True, 21.1, 49.4],
					['9-12, 22:00', 4, True, 23.2, 44.4],
					['9-12, 22:00', 5, False, 22.5, 48.0],
				]
			}

			return dict_data, 200

	elif sub == 'settings':
		if request.method =='GET':
			'''
			DB: return all user data
			1. get all user data
			2. format user data
			'''
			test_user_data = {
				'user_data': [
					['G7:1A:Y2:4T:80:40', 8.16, 22.06],
					['00:1A:C2:7B:00:50', 8.15, 23.07]
				]
			}

			return test_user_data, 200

		elif request.method == 'POST':
			mac_addr = request.form['mac_addr']
			work_start = request.form['work_start']
			work_end = request.form['work_end']
			sleep_start = request.form['bedtime']
			sleep_end = request.form['wakeup_time']
			print(mac_addr, work_start, work_end, sleep_start, sleep_end)

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

			action = 'New User Created'

			return jsonify({'action': action}), 200

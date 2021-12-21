from . import app
from .forms import SettingsForm
from flask import Flask, render_template, flash, redirect, url_for, after_this_request, make_response, jsonify
from flask import request as flask_req
import requests as req
import json
import time

# control unit server url
#url = 'http://172.26.24.142:8000'
url = 'http://localhost:8000'
# url = 'http://192.168.63.165:8000'

@app.route('/')
def index():
    return render_template('index.html')



# # # # # POWER ROUTES # # # # #

local_rooms_power_state = {
	'room1': None,
	'room2': None,
	'room3': None,
	'room4': None,
	'room5': None
}

@app.route('/power', methods=['GET', 'POST'])
def power():
    global local_rooms_power_state

    if flask_req.method == 'GET':
        try:
            res = req.get(url + '/api/gui/power/')
            local_rooms_power_state = res.json()
            print(f'GUI: local_rooms_power_state {local_rooms_power_state}')
        except req.Timeout:
            flash(f'timeout', 'error')
        except req.ConnectionError:
            flash(f'connection error', 'error')

        return render_template('power.html', data=local_rooms_power_state)

    elif flask_req.method == 'POST':

        btn = flask_req.form['power_btn']

        #print('before', local_rooms_power_state)

        if btn == 'house on':
            local_rooms_power_state['room1'] = True
            local_rooms_power_state['room2'] = True
            local_rooms_power_state['room3'] = True
            local_rooms_power_state['room4'] = True
            local_rooms_power_state['room5'] = True
        if btn == 'house off':
            local_rooms_power_state['room1'] = False
            local_rooms_power_state['room2'] = False
            local_rooms_power_state['room3'] = False
            local_rooms_power_state['room4'] = False
            local_rooms_power_state['room5'] = False
        elif btn == 'bathroom':
            #print('1', local_rooms_power_state['room1'])
            local_rooms_power_state['room1'] = not local_rooms_power_state['room1']
            #print('2', local_rooms_power_state['room1'], '=', not local_rooms_power_state['room1'])
            #print('test', type(not local_rooms_power_state['room1']))
            #print('3', local_rooms_power_state)
        elif btn == 'bedroom':
            local_rooms_power_state['room2'] = not local_rooms_power_state['room2']
        elif btn == 'garage':
            local_rooms_power_state['room3'] = not local_rooms_power_state['room3']
        elif btn == 'kitchen':
            local_rooms_power_state['room4'] = not local_rooms_power_state['room4']
        elif btn == 'living room':
            local_rooms_power_state['room5'] = not local_rooms_power_state['room5']

        #print('after', local_rooms_power_state)

        try:
            res = req.post(url + '/api/gui/power/', data=local_rooms_power_state, timeout=1)
            # overwriting the "local power states" with the database response
            local_rooms_power_state = res.json()
            print(local_rooms_power_state)
            print('GUI: POWER POST RESPONSE', local_rooms_power_state)
        except req.Timeout:
            flash(f'timeout', 'error')
        except req.ConnectionError:
            flash(f'connection error', 'error')
        #time.sleep(1)
        #return redirect(url_for('power'))
        return render_template('power.html', data=local_rooms_power_state)
        #return render_template('power.html', data=local_rooms_power_state, res=local_rooms_power_state)




# # # # # HISTORY ROUTES # # # # #

@app.route('/history', methods=['GET'])
def history():
    try:
        res = req.get(url + '/api/gui/history/')
    except req.Timeout:
        flash(f'timeout', 'error')
    except req.ConnectionError:
        flash(f'connection error', 'error')

    return render_template('history.html', data=res.json())



# # # # # SETTINGS ROUTES # # # # #

settings_res = 0

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global settings_res
    form = SettingsForm()

    if flask_req.method == 'GET':
        user_chosen = None

        try:
            res = req.get(url + '/api/gui/settings/')
            json_res = res.json()
            #print(json_res)
        except req.Timeout:
            flash(f'timeout', 'error')
        except req.ConnectionError:
            flash(f'connection error', 'error')

        res_data = {
            'post_response': settings_res,
            'user_list': json_res['user_data']
        }

        # when click on user/mac in "Update Existing Users" dropdown
        if flask_req.args.get('user'):
            user_chosen = int(flask_req.args.get('user')) - 1

            form['mac_addr'].default = json_res['user_data'][user_chosen][0]
            form['work_start'].default = int(str(json_res['user_data'][user_chosen][1]).split(".")[0])
            form['work_end'].default = int(str(json_res['user_data'][user_chosen][1]).split(".")[1])
            form['sleep_start'].default = int(str(json_res['user_data'][user_chosen][2]).split(".")[0])
            form['sleep_end'].default = int(str(json_res['user_data'][user_chosen][2]).split(".")[1])
            form.process()

        # make "user created" pop up dissapear next time settings.html is rendered
        if settings_res:
            settings_res = 0

        return render_template('settings.html', data=res_data, form=form)

    if flask_req.method == 'POST':
        mac_addr = flask_req.form['mac_addr']
        work_start = flask_req.form['work_start']
        work_end = flask_req.form['work_end']
        sleep_start = flask_req.form['sleep_start']
        sleep_end = flask_req.form['sleep_end']

        settings_data = {
            'mac_addr': mac_addr,
            'work_start': work_start,
            'work_end': work_end,
            'bedtime': sleep_start,
            'wakeup_time': sleep_end
        }

        try:
            res = req.post(url + '/api/gui/settings/', data=settings_data, timeout=1)
            settings_res = (json.loads(res.text)['action'])
        except req.Timeout:
            flash(f'timeout', 'error')
        except req.ConnectionError:
            flash(f'connection error', 'error')

        return redirect(url_for('settings'))

import time
import sys

from control_unit.submodules.power_supply.seeed.seeed_relay_test import Relay
from control_unit.submodules.power_supply.single_relay import SingleRelay

relay_board = Relay()
single_relay = SingleRelay()


def control_power(on: bool, room: int):
	if on and room == 1:
		relay_board.OFF_1()
	elif on and room == 5:
		relay_board.OFF_2()
	elif on and room == 4:
		relay_board.OFF_3()
	elif on and room == 3:
		relay_board.OFF_4()
	elif on and room == 2:
		single_relay.OFF()
	elif not on and room == 1:
		relay_board.ON_1()
	elif not on and room == 5:
		relay_board.ON_2()
	elif not on and room == 4:
		relay_board.ON_3()
	elif not on and room == 3:
		relay_board.ON_4()
	elif not on and room == 2:
		single_relay.ON()

def recv(pwr: bool, rooms: list):
	'''
	The boolean 'pwr' controls if power should be on or off (0 = off, 1 = on)
	The list 'rooms' indicate which rooms are affected by the action. The list [1,2,5] tells that room 1, 2 and 5 are affected. All values in the list should be integers
	'''
	for i in rooms:
		control_power(pwr, i)

	return True

#recv(False, [1,2,3,4,5])

import sys
import os
import RPi.GPIO as GPIO
import time
import math
import re
import signal

from itertools import groupby
from xi_client.xively_client import XivelyClient
from xi_client.xively_connection_parameters import XivelyConnectionParameters
from xi_client.xively_error_codes import XivelyErrorCodes

def signal_handler(signal, frame):
	GPIO.cleanup()
	print('GPIO shutdown')
	selfclient.unsubscribe(topic)
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

c = XivelyClient()

topic = ""

params = XivelyConnectionParameters()
params.client_id = ""
params.username = ""
params.password = ""
params.use_websocket = False
params.clean_session = True

GPIO.setmode(GPIO.BOARD)

ControlPinX = [12, 16, 18, 22]
ControlPinY = [11, 13, 15, 7]

for pin in ControlPinX:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, 0)

for pin in ControlPinY:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, 0)

print('GPIO initialized')

seq_left = [
		[1, 0, 0, 1],
		[0, 0, 0, 1],
		[0, 0, 1, 1],
		[0, 0, 1, 0],
		[0, 1, 1, 0],
		[0, 1, 0, 0],
		[1, 1, 0, 0],
		[1, 0, 0, 0]
]

seq_right = list(reversed(seq_left))

started = False
yaw, pitch, roll = 0, 0, 0
yaw_new, pitch_new, roll_new = 0, 0, 0

def turn(control, seq_direction, degrees, speed):
	sleep = 0.001 / speed
	for i in range(int(degrees / 360.0 * 512)):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(control[pin], seq_direction[halfstep][pin])
				time.sleep(sleep)

def turnGenerator(prefix, seq_direction, degrees):
	for i in range(int(degrees / 360.0 * 512)):
		for halfstep in range(8):
			yield [prefix, seq_direction[halfstep]]

def move(angle_x, angle_y, speed):
	if angle_x > 0:
		x = list(turnGenerator("x", seq_left, angle_x))
	else:
		x = list(turnGenerator("x", seq_right, abs(angle_x)))
	if angle_y > 0:
		y = list(turnGenerator("y", seq_left, angle_y))
	else:
		y = list(turnGenerator("y", seq_right, abs(angle_y)))

	if len(x) == 0:
		steps = y
	if len(y) == 0:
		steps = x

	if len(x) > 0 and len(y) > 0:
		if len(x) > len(y):
			len_xy = len(x) + len(y)
			groups = groupby(((x[len(x)*i//len_xy], y[len(y)*i//len_xy]) for i in range(len_xy)),
        		         key=lambda a:a[0])
		else:
			len_xy = len(x) + len(y)
			groups = groupby(((y[len(y)*i//len_xy], x[len(x)*i//len_xy]) for i in range(len_xy)),
        		         key=lambda a:a[0])
		steps = [j[i] for k,g in groups for i,j in enumerate(g)]
	
	for step in steps:
		if step[0] == "x":
			control = ControlPinX
		else:
			control = ControlPinY
		for pin in range(4):
			GPIO.output(control[pin], step[1][pin])
			time.sleep(0.0001)

def on_connect_finished(client, result):
	print('Connect result:', result)
	success, rid = selfclient.subscribe((topic, 0))

def on_disconnect_finished(client, result):
	print('Disconnected')

def on_subscribe_finished(client, rid, granted_qos):
	print('Subscribed ', rid, granted_qos)

def on_message_received(client, message):
	global started, yaw, pitch, roll, yaw_new, pitch_new, roll_new
	m = re.match("yaw:(.*);pitch:(.*);roll:(.*)", message.payload)
	if m:
		y = float(m.group(1))	
		r = float(m.group(3))
		if started:
			yaw_new = y
			roll_new = r
		else:
			yaw = y
			roll = r
			started = True

def on_unsubscribe_finished(client, rid):
	print('Unsubscribed')
	selfclient.disconnect()

selfclient = XivelyClient()
selfclient.on_connect_finished = on_connect_finished
selfclient.on_disconnect_finished = on_disconnect_finished
selfclient.on_subscribe_finished = on_subscribe_finished
selfclient.on_message_received = on_message_received
selfclient.on_unsubscribe_finished = on_unsubscribe_finished
selfclient.connect(params)

while True:
	y = yaw_new
	p = pitch_new
	r = roll_new
	yd = round(y - yaw, 2)
	pd = round(p - pitch, 2)
	rd = round(r - roll, 2)

	sys.stdout.write('yaw:%8.2f pitch:%8.2f roll:%8.2f\r' % (yaw, pitch, roll))
	sys.stdout.flush()

	if started and (abs(yd) > 0.02 or abs(rd) > 0.02): 
		while (yd < -3.14): yd += 6.28
		while (yd > 3.14): yd -= 6.28
		while (rd < -3.14): rd += 6.28
		while (rd > 3.14): rd -= 6.28
		angle_x = round(180.0 / math.pi * yd * -1)
		angle_y = round(180.0 / math.pi * rd)
		move(angle_x, angle_y, 10)
		yaw = y
		pitch = p
		roll = r
	else:
		time.sleep(0.01)



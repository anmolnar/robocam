import os
from xi_client.xively_client import XivelyClient
from xi_client.xively_connection_parameters import XivelyConnectionParameters
from xi_client.xively_error_codes import XivelyErrorCodes

c = XivelyClient()

topic = ""

params = XivelyConnectionParameters()
params.client_id = ""
params.username = ""
params.password = ""
params.use_websocket = False
params.clean_session = True

selfrid = 0

def on_connect_finished(client, result):
	print('Connect result:', result)
	success, selfrid = selfclient.subscribe((topic, 0))

def on_disconnect_finished(client, result):
	print('Disconnected')

def on_subscribe_finished(client, rid, granted_qos):
	print('Subscribed ', rid, granted_qos)

def on_message_received(client, message):
	print('Message received')
	print(message)

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

selfclient._thread.join(100.0)

os.system('read -r -p "Press any key..." key')

selfclient.unsubscribe(topic)



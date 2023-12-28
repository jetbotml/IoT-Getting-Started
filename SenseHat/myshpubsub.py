# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import json
from utils.command_line_utils import CommandLineUtils
from sense_hat import SenseHat


# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a topic, and begins publishing messages to that topic.
# The device should receive those same messages back from the message broker,
# since it is subscribed to that same topic.

# cmdData is the arguments/input from the command line placed into a single struct for
# use in this sample. This handles all of the command line parsing, validating, etc.
# See the Utils/CommandLineUtils for more information.
cmdData = CommandLineUtils.parse_sample_input_pubsub()

received_count = 0
received_all_event = threading.Event()

# My Code -----------------------------
from gpiozero import DiskUsage, CPUTemperature
from datetime import datetime
import subprocess
import logging
from time import gmtime, strftime
import sys
import os
import socket
import uuid

sense = SenseHat()

ScriptVersion = "20231227.0"

def get_ip_address():
	ip_address = '';
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8",80))
	ip_address = s.getsockname()[0]
	s.close()
	return ip_address

def get_mac():
    mac_address = uuid.getnode()
    mac_address_hex = ':'.join(['{:02x}'.format((mac_address >> elements) & 0xff) for elements in range(0,8*6,8)][::-1])
    s3_mac_address = mac_address_hex.replace(':', '').lower()
    return s3_mac_address

def addPiDeviceData():
	#disk = DiskUsage()

	cpu = CPUTemperature()

	devicemessage = {}

	devicemessage['mac'] = get_mac()

	cmd = "cat /proc/device-tree/model"
	input_string = subprocess.check_output(cmd, shell=True).decode("utf-8")
	devicemessage['HW'] = input_string.replace("\x00", "")

	input_string = sys.version
	index_of_open_parenthesis = input_string.find("(")
	if index_of_open_parenthesis != -1:
	    # Extract the substring before the opening parenthesis
	    devicemessage['Python'] = input_string[:index_of_open_parenthesis].strip()
	else:
	    devicemessage['Python'] = sys.version

	cmd = "top -bn1 | grep load | awk '{printf \" %.2f\", $(NF-2)}'"
	devicemessage['CPU'] = subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "df -h | awk '$NF==\"/\"{printf \" %d/%d GB %s\", $3,$2,$5}'"
	devicemessage['DiskUsage']= subprocess.check_output(cmd, shell=True).decode("utf-8")

	cmd = "free -m | awk 'NR==2{printf \" %s/%s MB %.2f%%\", $3,$2,$3*100/$2 }'"
	devicemessage['MemUsage'] = subprocess.check_output(cmd, shell=True).decode("utf-8")

	devicemessage['CPUtemp'] = round(cpu.temperature * (9 / 5) + 32, 1)

	devicemessage['HoursRunning'] = round(float(os.popen("awk '{print $1}' /proc/uptime").readline())/60/60, 2)

	devicemessage['SenseHat temp'] = round(sense.get_temperature_from_pressure() * (9 / 5) + 32, 1)

	devicemessage['SenseHat pressure'] = round(sense.get_pressure(), 1)

	devicemessage['SenseHat humidity'] = round(sense.get_humidity(), 1)

	return devicemessage


# My Code -----------------------------



# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    Red = 0
    Green = 0
    Blue = 0

    if topic == message_Subtopic:
        message = str(payload)
        message = message.lower()
        print("Message = " + message)
        # Example processing for a specific topic
        if "red" in message:
            Red = 255
        if "green" in message:
            Green = 255
        if "blue" in message:
            Blue = 255
 
    print("Color set to (" + str(Red) + ", " + str(Green) + ", " + str(Blue) +")" )
        
    sense.clear(Red, Green, Blue)

    global received_count
    received_count += 1
    if received_count == cmdData.input_count:
        received_all_event.set()


# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailuredata)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")

if __name__ == '__main__':
    # Create the proxy options if the data is present in cmdData
    proxy_options = None
    if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
        proxy_options = http.HttpProxyOptions(
            host_name=cmdData.input_proxy_host,
            port=cmdData.input_proxy_port)

    # Create a MQTT connection from the command line data
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=cmdData.input_endpoint,
        port=cmdData.input_port,
        cert_filepath=cmdData.input_cert,
        pri_key_filepath=cmdData.input_key,
        ca_filepath=cmdData.input_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=cmdData.input_clientId,
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=proxy_options,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)

    if not cmdData.input_is_ci:
        print(f"Connecting to {cmdData.input_endpoint} with client ID '{cmdData.input_clientId}'...")
    else:
        print("Connecting to endpoint with client ID")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    message_count = 0
    message_topic = "mypi/publish"
    message_Subtopic = "mypi/subscribe"
    message_string = cmdData.input_message
    print(message_topic)
    print(message_Subtopic)

    # Subscribe
    print("Subscribing to topic '{}'...".format(message_Subtopic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=message_Subtopic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if message_string:
        if message_count == 0:
            print("Sending messages until program killed")
        else:
            print("Sending {} message(s)".format(message_count))

        publish_count = 1
        while (publish_count <= message_count) or (message_count == 0):
#            message = "{} [{}]".format(message_string, publish_count)
#            print("Publishing message to topic '{}': {}".format(message_topic, message))
            message = {}
            message['Script Version'] = ScriptVersion 
            message['WiFiIP'] = get_ip_address()
            message.update(addPiDeviceData())
            message['datetime'] = time.strftime("%Y-%m-%dT%H:%M:%S", gmtime())
            print("Publishing message to topic '{}': {}".format(message_topic, message))
            message_json = json.dumps(message)
            mqtt_connection.publish(
                topic=message_topic,
                payload=message_json,
                qos=mqtt.QoS.AT_LEAST_ONCE)
            time.sleep(10)
            publish_count += 1

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if message_count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")

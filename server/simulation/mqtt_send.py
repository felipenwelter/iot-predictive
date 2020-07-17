#------------------------------------------
# Author: Felipe Nathan Welter
# Date: 07th July 2020
# Version: 1.0
# Python Ver: 3.0
#------------------------------------------

import paho.mqtt.client as mqtt
import time
import read_data as rd

# MQTT Settings
MQTT_Broker = "192.168.0.25" #"192.168.0.25"
MQTT_Port = 1883
Keep_Alive_Interval = 45
MQTT_Topic = "equipment/dash/reset"
in_loop = True

#Subscribe to all Sensors at Base Topic
def on_connect(mqtt_client, obj, flags, rc):
    #mqttc.subscribe(MQTT_Topic, 0)
	mqttc.subscribe(MQTT_Topic, 0)
    #pass

def on_message(mqtt_client, obj, msg):
    if (msg.topic == MQTT_Topic):
        rd.setOffsets()
    print ("MQTT Topic: " + msg.topic)


def configure():
    mqttc.publish("equipment/actions", '{"action":"configure"}')
    # Continue the network loop
    #mqttc.loop_forever()

#0 for clear
#1 for yellow
#2 for green
#3 for red
def led(level):
    mqttc.publish("equipment/actions", '{"action":"status", "vibration_level": '+str(level)+'}')
    mqttc.publish("equipment/dash/led", level)

def vibration(value):
    mqttc.publish("equipment/dash/vibration", value)
    
def alert(value):
    mqttc.publish("equipment/dash/alertcount",value)

def stop():
    global in_loop
    in_loop = False

def loop():
    #mqttc.loop_forever()
    #print("loop")
    global in_loop
    while in_loop:
        mqttc.loop_start()  #Start loop 
        time.sleep(2) # Wait for connection setup to complete
        mqttc.loop_stop()    #Stop loop 
        #mqttc.loop_forever()

mqttc = mqtt.Client()

# Assign event callbacks
mqttc.on_connect = on_connect
mqttc.on_message = on_message

# Connect
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))

# Continue the network loop
#mqttc.loop_forever()
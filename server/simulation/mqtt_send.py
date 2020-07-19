import paho.mqtt.client as mqtt
import time
import read_data as rd

# MQTT Settings
MQTT_Broker = "192.168.0.25" #"192.168.0.25"
MQTT_Port = 1883
Keep_Alive_Interval = 45
MQTT_Topic = "equipment/dash/reset"
in_loop = True


#---------------------------------------------------------------------------
# Função: Callback de conexão MQTT, subscreve a topic do dashboard mobile
#---------------------------------------------------------------------------
#Subscribe to all Sensors at Base Topic
def on_connect(mqtt_client, obj, flags, rc):
	mqttc.subscribe(MQTT_Topic, 0)
    #pass


#---------------------------------------------------------------------------
# Função: Callback de recebimento de mensagens MQTT, redefine offsets
#---------------------------------------------------------------------------
def on_message(mqtt_client, obj, msg):
    if (msg.topic == MQTT_Topic):
        rd.setOffsets()
    print ("MQTT Topic: " + msg.topic)


#---------------------------------------------------------------------------
# Função: Envia "configure" para acionamento de leds no ESP32
#---------------------------------------------------------------------------
def configure():
    mqttc.publish("equipment/actions", '{"action":"configure"}')
    # mqttc.loop_forever() # Continue the network loop


#---------------------------------------------------------------------------
# Função: Envia "actions" para acionamento de leds no ESP32 e dash mobile
# Parâmetros: level: 0-clear 1-amarelo 2-verde 3-vermelho
#---------------------------------------------------------------------------
def led(level):
    mqttc.publish("equipment/actions", '{"action":"status", "vibration_level": '+str(level)+'}')
    mqttc.publish("equipment/dash/led", level)


#---------------------------------------------------------------------------
# Função: Envia dados de vibração para dash mobile
#---------------------------------------------------------------------------
def vibration(value):
    mqttc.publish("equipment/dash/vibration", value)


#---------------------------------------------------------------------------
# Função: Envia dados de contagem de alertas para dash mobile
#---------------------------------------------------------------------------
def alert(value):
    mqttc.publish("equipment/dash/alertcount",value)


#---------------------------------------------------------------------------
# Função: Finaliza conexão com broker MQTT
#---------------------------------------------------------------------------
def stop():
    global in_loop
    in_loop = False


#---------------------------------------------------------------------------
# Função: Loop de leitura MQTT
#---------------------------------------------------------------------------
def loop():
    global in_loop
    while in_loop:
        mqttc.loop_start()  #Start loop 
        time.sleep(2) # Wait for connection setup to complete
        mqttc.loop_stop()    #Stop loop 



mqttc = mqtt.Client()

# Assign event callbacks
mqttc.on_connect = on_connect
mqttc.on_message = on_message

# Connect
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))
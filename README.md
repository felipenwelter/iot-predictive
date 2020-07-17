# iot-predictive
IoT project using ESP32 + MPU6050 for vibration monitoring


### To install Mosquitto (MAC):
brew install mosquitto
/usr/local/sbin/mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf

mosquitto_pub -t xpto/temperature -m 22
mosquitto_sub -h 192.168.0.25 -p 1883 -v -t 'xpto/temperature'

brew install libwebsockets (to use websockets on webpage)


## To install paho-mqtt locally
pip3 install paho–mqtt

### To install Arduino:

## To run node.js server
node index.js at folder named http/server


Dummy:
(at correct folder) >> python3 initialize_DB_Tables.py
one terminal to publish dummy: python3 mqtt_Publish_Dummy_Data.py 
one terminal to read dummy: python3 mqtt_Listen_Sensor_Data.py
with mosquitto running on the backgroud


Open database: >> sqlite3 IoT.db



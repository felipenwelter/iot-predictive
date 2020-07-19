#------------------------------------------
# Author: Felipe Nathan Welter
# Date: 11th June 2020
# Version: 1.0
# Python Ver: 3.0
# Reference: https://iotbytes.wordpress.com/store-mqtt-data-from-sensors-into-sql-database/
#------------------------------------------
import json
import sqlite3
import datetime

# SQLite DB Name
DB_Name =  "IoT.db"

#===============================================================
# Database Manager Class

class DatabaseManager():
	def __init__(self):
		self.conn = sqlite3.connect(DB_Name)
		self.conn.execute('pragma foreign_keys = on')
		self.conn.commit()
		self.cur = self.conn.cursor()
		
	def add_del_update_db_record(self, sql_query, args=()):
		self.cur.execute(sql_query, args)
		self.conn.commit()
		return

	def __del__(self):
		self.cur.close()
		self.conn.close()

#===============================================================
# Functions to push Sensor Data into Database

# Function to save Temperature to DB Table
def equipment_Temperature_Handler(jsonData):
	#Parse Data 
	json_Dict = json.loads(jsonData)
	SensorID = json_Dict['Sensor_ID']
	DateTime = json_Dict['Date']
	Temperature = json_Dict['Temperature']
	
	#Push into DB Table
	dbObj = DatabaseManager()
	dbObj.add_del_update_db_record("insert into equipment_temperature (SensorID, DateTime, Temperature) values (?,?,?)",[SensorID, DateTime, Temperature])
	del dbObj
	now = datetime.datetime.now()
	print ("["+now.strftime("%H:%M:%S") + "] Inserted Temperature Data into Database.")

# Function to save Vibration to DB Table
def equipment_Vibration_Handler(jsonData):
	info_count = 0
	#Parse Data 
	json_Dict = json.loads(jsonData)
	SensorID = json_Dict['Sensor_ID']

	for measure in json_Dict['measure']:
		
		DateTime = measure['Date']
		Pitch = measure['Pitch']
		Roll = measure['Roll']
		
		#Push into DB Table
		dbObj = DatabaseManager()
		dbObj.add_del_update_db_record("insert into equipment_vibration (SensorID, DateTime, Pitch, Roll) values (?,?,?,?)",[SensorID, DateTime, Pitch, Roll])
		del dbObj
		info_count += 1

	if (info_count > 0):
		now = datetime.datetime.now()
		print ("["+now.strftime("%H:%M:%S") + "] Inserted Vibration Data into Database.")
	

#===============================================================
# Master Function to Select DB Funtion based on MQTT Topic

def sensor_Data_Handler(Topic, jsonData):
	if Topic == "equipment/temperature":
		equipment_Temperature_Handler(jsonData)
	elif Topic == "equipment/vibration":
		equipment_Vibration_Handler(jsonData)

#===============================================================
#------------------------------------------
# Author: Felipe Nathan Welter
# Date: 11th June 2020
# Version: 1.0
# Python Ver: 3.0
# Reference: https://iotbytes.wordpress.com/store-mqtt-data-from-sensors-into-sql-database/
#------------------------------------------

import sqlite3
import os

# SQLite DB Name

#DB_Name =  "IoT.db"
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
DB_Name = os.path.join(script_dir, "IoT.db")
DB_Name = os.path.abspath(os.path.realpath(DB_Name))


# SQLite DB Table Schema
TableSchema="""
drop table if exists equipment_temperature ;
create table equipment_temperature (
  id integer primary key autoincrement,
  SensorID text,
  DateTime text,
  Temperature text
);

drop table if exists equipment_vibration ;
create table equipment_vibration (
  id integer primary key autoincrement,
  SensorID text,
  DateTime text,
  Pitch text,
  Roll text
);
"""

#Connect or Create DB File
conn = sqlite3.connect(DB_Name)
curs = conn.cursor()

#Create Tables
sqlite3.complete_statement(TableSchema)
curs.executescript(TableSchema)

#Close DB
curs.close()
conn.close()

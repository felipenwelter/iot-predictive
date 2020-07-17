#------------------------------------------
# Author: Felipe Nathan Welter
# Date: 11th June 2020
# Version: 1.0
# Python Ver: 3.0
#------------------------------------------

import sqlite3

# SQLite DB Name
DB_Name =  "IoT.db"

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

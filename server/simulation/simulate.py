import numpy as np
import sqlite3
from datetime import datetime
import time
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from random import randrange
import read_data as rd
import threading
import os

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
orig = os.path.join(script_dir, '../examples/db/IoT-long.db')
dest = os.path.join(script_dir, '../IoT.db')
dest = os.path.abspath(os.path.realpath(dest))

#orig = 'IoT-long.db'
#dest =  'IoT.db'

#simulate data getting from the IoT sensor
def sensorReceive(offset):
    conn = sqlite3.connect(orig)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM equipment_vibration LIMIT 10 OFFSET "+str(offset)+";")
    result = list(cursor.fetchall())

    conn.close()
    return result

#simulate data insertion from the IoT sensor to the DB
def insertIntoDB(records):
    conn = sqlite3.connect(dest)
    cursor = conn.cursor()

    for i in records:
        var_string = ', '.join('?' * len(i))
        query = 'INSERT INTO equipment_vibration VALUES (%s);' % var_string
        cursor.execute(query, i)

    conn.commit()
    conn.close()
    return 0

# count records to keep-alive
def countRecords():
    conn = sqlite3.connect(orig)
    cursor = conn.cursor()

    # calcula a média para utilizar como offset (levando os valores a zero)
    cursor.execute("SELECT count(id) FROM equipment_vibration;")
    total = cursor.fetchone()[0]
    conn.close()

    return total

def run():
    #first create the empty .db file

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    filename = os.path.join(script_dir, "../initialize_DB_Tables.py")
    filename = os.path.abspath(os.path.realpath(filename))
    exec(open(filename).read())

    # count records to keep-alive
    total = countRecords()
    loop_control = 0

    while loop_control < total:

        #simulate data getting from the IoT sensor
        data = sensorReceive(loop_control)
        loop_control += len(data)

        #simulate data insertion from the IoT sensor to the DB
        insertIntoDB(data)

        time.sleep(0.5)
import numpy as np
import sqlite3
from datetime import datetime

IoTdb = 'IoT-run-20-sec-middle-double-hit-at-10.db'

def isEmpty(cursor, table):
    cursor.execute("SELECT count(*) FROM "+table+";")
    return ( cursor.fetchone()[0] == 0)
    

def getPitchData():
    pitch_array = np.array([])
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    if isEmpty(cursor,'equipment_vibration') == False:

        # calcula a média para utilizar como offset (levando os valores a zero)
        cursor.execute("SELECT AVG(Pitch) FROM equipment_vibration LIMIT 10;")
        offset = cursor.fetchone()[0]
        
        cursor.execute("SELECT Pitch - "+str(offset)+" FROM equipment_vibration;")

        result = list(cursor.fetchall())
        result2 = [float(i[0]) for i in result]
        pitch_array = np.array(result2)

    conn.close()

    return pitch_array




def getRollData():
    roll_array = np.array([])
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    if isEmpty(cursor,'equipment_vibration') == False:

        # calcula a média para utilizar como offset (levando os valores a zero)
        cursor.execute("SELECT AVG(Roll) FROM equipment_vibration LIMIT 10;")
        offset = cursor.fetchone()[0]
        
        cursor.execute("SELECT Roll - "+str(offset)+" FROM equipment_vibration;")

        result = list(cursor.fetchall())
        result2 = [float(i[0]) for i in result]
        roll_array = np.array(result2)

    conn.close()

    return roll_array

def getPitchRollSum():
    pitch_roll = np.array([])
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    if isEmpty(cursor,'equipment_vibration') == False:
    
        # calcula a média para utilizar como offset (levando os valores a zero)
        cursor.execute("SELECT AVG(Pitch), AVG(Roll) FROM equipment_vibration LIMIT 10;")
        offset = cursor.fetchone()

        #cursor.execute("SELECT abs(Pitch), abs(Roll), (abs(Pitch) + abs(Roll)) * 2 "
        #       "FROM equipment_vibration;")

        cursor.execute("SELECT ( abs(Pitch - ("+str(offset[0])+")) + abs(Roll - ("+str(offset[1])+")) ) * 2 "
            "FROM equipment_vibration;")


        result = list(cursor.fetchall())
        result2 = [float(i[0]) for i in result]
        pitch_roll = np.array(result2)

    conn.close()

    return pitch_roll

def getSecondsDiff():
    result = 0
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    if isEmpty(cursor,'equipment_vibration') == False:
    
        # lendo os dados
        cursor.execute("SELECT DateTime FROM equipment_vibration order by id asc;")
        result1 = cursor.fetchone()
        
        result1 = datetime.strptime(result1[0].strip(),'%d-%b-%Y %H:%M:%S.%f')
        
        # lendo os dados
        cursor.execute("SELECT DateTime FROM equipment_vibration order by id desc;")

        result2 = cursor.fetchone()
        result2 = datetime.strptime(result2[0].strip(),'%d-%b-%Y %H:%M:%S.%f')

        result = (result2 - result1).seconds

    conn.close()

    return result

p = getPitchData()
r = getRollData()
m = getPitchRollSum()
s = getSecondsDiff()
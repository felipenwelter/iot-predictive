import numpy as np
import sqlite3
import settings
from datetime import datetime
import os

#IoTdb = 'server/IoT.db'
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
IoTdb = os.path.join(script_dir, "../IoT.db")
IoTdb = os.path.abspath(os.path.realpath(IoTdb))

settings.init() # Call only once


def isEmpty(cursor, table):
    cursor.execute("SELECT count(*) FROM "+table+";")
    return ( cursor.fetchone()[0] == 0)


def setOffsets():
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    print("# reseted offsets")

    if isEmpty(cursor,'equipment_vibration') == False:
        
        # calcula a média para utilizar como offset (levando os valores a zero)
        cursor.execute("SELECT AVG(Pitch), AVG(Roll) FROM ( SELECT Pitch, Roll FROM equipment_vibration ORDER BY id DESC LIMIT 10);")
        offset = cursor.fetchone()

        if len(offset) > 0:
            settings.pitch_offset = offset[0]
            settings.roll_offset = offset[1]
            settings.saveOffsets()

    conn.close()

    return


def getOffsets():

    # se offsets ja foram calculados, retorna valores salvos
    if settings.pitch_offset == 0 and settings.roll_offset == 0:
       setOffsets()

    return (settings.pitch_offset, settings.roll_offset)


#set type as 1 for Pitch, 2 for Roll and 3 for Pitch and Roll calculation
def getAllData(type=0, limit=200):
    result_array = np.array([])
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    if isEmpty(cursor,'equipment_vibration') == False:

        offset = getOffsets()
        cursor.execute("SELECT Pitch - "+str(offset[0])+"," #get the last 200 results
                             " Roll - "+str(offset[1])+ ","
                             " ( abs(Pitch - ("+str(offset[0])+")) + abs(Roll - ("+str(offset[1])+")) ) * 2, "
                             " DateTime "
                             " FROM equipment_vibration ORDER BY id DESC LIMIT "+str(limit)+";")
        result = list(cursor.fetchall())

        if type == 1: #Pitch
            result_array = np.array( [float(i[0]) for i in result] )
        elif type == 2: #Roll
            result_array = np.array( [float(i[1]) for i in result] )
        elif type == 3: #Pitch and roll calculation
            result_array = np.array( [float(i[2]) for i in result] )
        elif type == 0:
            result_array = ( np.array( [float(i[0]) for i in result][::-1] ), #::-1 to invert the array
                             np.array( [float(i[1]) for i in result][::-1] ),
                             np.array( [float(i[2]) for i in result][::-1] ),
                             np.array( [i[3] for i in result][::-1] ) )

    conn.close()

    return result_array


def getPitchData():
    pitch_array = np.array([])
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    if isEmpty(cursor,'equipment_vibration') == False:

        # calcula a média para utilizar como offset (levando os valores a zero)
        cursor.execute("SELECT AVG(Pitch) FROM ( SELECT Pitch FROM equipment_vibration LIMIT 10);")
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
        cursor.execute("SELECT AVG(Roll) FROM ( SELECT Roll FROM equipment_vibration LIMIT 10);")
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
        cursor.execute("SELECT AVG(Pitch), AVG(Roll) FROM ( SELECT Pitch, Roll FROM equipment_vibration LIMIT 10);")
        offset = cursor.fetchone()

        #cursor.execute("SELECT abs(Pitch), abs(Roll), (abs(Pitch) + abs(Roll)) * 2 "
        #       "FROM equipment_vibration;")

        query = "SELECT ( abs(Pitch - ("+str(offset[0])+")) + abs(Roll - ("+str(offset[1])+")) ) * 2 "
        query += "FROM equipment_vibration;"
        cursor.execute(query)


        result = list(cursor.fetchall())
        result2 = [float(i[0]) for i in result]
        pitch_roll = np.array(result2)


        #x2 = getAllData(3)
        
        #comparison = pitch_roll == x2
        #equal_arrays = comparison.all()
        #print(equal_arrays)


    conn.close()

    return pitch_roll


def getSecondsDiff(limit=200):
    result = 0
    conn = sqlite3.connect(IoTdb)
    cursor = conn.cursor()

    if isEmpty(cursor,'equipment_vibration') == False:
    
        # lendo os dados
        cursor.execute("SELECT DateTime FROM equipment_vibration order by id desc LIMIT "+str(limit)+";")
        result = cursor.fetchall()
        
        result1 = datetime.strptime(result[limit-1][0].strip(),'%d-%b-%Y %H:%M:%S.%f')
        result2 = datetime.strptime(result[0][0].strip(),'%d-%b-%Y %H:%M:%S.%f')
        
        # lendo os dados
        #cursor.execute("SELECT DateTime FROM equipment_vibration order by id desc LIMIT "+str(limit)+";")

        #result2 = cursor.fetchone()
        #result2 = datetime.strptime(result2[0].strip(),'%d-%b-%Y %H:%M:%S.%f')

        result = (result2 - result1).seconds

    conn.close()

    return result


#p = getPitchData()
#r = getRollData()
#m = getPitchRollSum()
#s = getSecondsDiff()
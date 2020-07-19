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


#-----------------------------------------------
# Função: Verifica se há registros na tabela
# Parâmetros: cursor - objeto de conexão ao BD
#             table - tabela a verificar
# Retorno: true para o caso de haver registros
#-----------------------------------------------
def isEmpty(cursor, table):
    cursor.execute("SELECT count(*) FROM "+table+";")
    return ( cursor.fetchone()[0] == 0)


#-----------------------------------------------------------------------------
# Função: Redefine os offsets com base nas informações mais atuais da tabela
# Retorno: null
#-----------------------------------------------------------------------------
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
    

#-------------------------------------------------------------------
# Função: Busca os offsets armazenados, e se não houver, os define
# Retorno: array no formato (pitch,roll)
#-------------------------------------------------------------------
def getOffsets():

    # se offsets ja foram calculados, retorna valores salvos
    if settings.pitch_offset == 0 and settings.roll_offset == 0:
       setOffsets()

    return (settings.pitch_offset, settings.roll_offset)


#---------------------------------------------------------------
# Função: Busca as leituras armazenadas de pitch e roll
# Parâmetros: type - define o que deseja obter (def: 0), sendo:
#                    0: pitch, roll, pitch+roll
#                    1: pitch
#                    2: roll
#                    3: pitch + roll
#             limit - número de registros para busca (def: 200)
# Retorno: array (np) com as informações armazenadas
#---------------------------------------------------------------
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


#-------------------------------------------------------------------------------
# Função: Retorna a diferença de tempo entre duas leituras
# Parâmetros: limit - número de registros para busca (def: 200)
# Retorno: a diferença, em segundos, da primeira e última leitura do intervalo
#-------------------------------------------------------------------------------
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

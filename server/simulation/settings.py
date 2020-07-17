pitch_offset = 0
roll_offset = 0

def init():
    global pitch_offset, roll_offset
    file1 = open('server/simulation/settings.ini', 'rb')
    lines = file1.readlines()
    pitch_offset = float(lines[0].decode('ascii'))
    roll_offset = float(lines[1].decode('ascii'))
    file1.close()

def saveOffsets():
    global pitch_offset, roll_offset
    file1 = open('server/simulation/settings.ini', 'w')
    file1.write(str(pitch_offset) + "\n" + str(roll_offset) )
    file1.close()



    #TODO colocar um grafico em baixo com maior dimensao pra ver o historico de longo prazo
    #TODO subir github
    #TODO tempo de piscar vermelho aumentar um pouco (pelo arduino mesmo)
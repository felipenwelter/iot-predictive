import os

pitch_offset = 0
roll_offset = 0

def init():
    global pitch_offset, roll_offset
    
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "settings.ini"
    abs_file_path = os.path.join(script_dir, rel_path)
    #print(abs_file_path)
    file1 = open(abs_file_path, 'rb')

    lines = file1.readlines()
    pitch_offset = float(lines[0].decode('ascii'))
    roll_offset = float(lines[1].decode('ascii'))
    file1.close()

def saveOffsets():
    global pitch_offset, roll_offset
    
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "settings.ini"
    abs_file_path = os.path.join(script_dir, rel_path)
    #print(abs_file_path)
    file1 = open(abs_file_path, 'w')

    file1.write(str(pitch_offset) + "\n" + str(roll_offset) )
    file1.close()

init()
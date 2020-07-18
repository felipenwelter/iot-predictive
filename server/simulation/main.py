import numpy as np
import sqlite3
from datetime import datetime
import time
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from random import randrange
import read_data as rd
import mqtt_send as mqtt
import threading
#from threading import Thread
import simulate as sim
import calc as cl

# 0 for Pitch, 1 for Roll, 2 for PitchRollSum
calc_type = 2

pyplot.rcParams['figure.figsize'] = [14,7]
pyplot.rcParams.update({'font.size':18})


t, p, r = [], [], []
p_hist, t_hist = [], []


#figure = pyplot.figure()

figure, axes = pyplot.subplots(
        nrows=2, ncols=1, sharex=True, sharey=False, 
        gridspec_kw={'height_ratios':[3,1]}
        )

# remove labels
for label in axes[1].get_xticklabels():
    label.set_visible(False)

axes[0].set_ylabel('Recent')
axes[1].set_ylabel('Historic')


pLine, = axes[0].plot(t,p,color='c',LineWidth=1.5,label='Pitch',)
rLine, = axes[0].plot(t,r,color='m',LineWidth=1.5,label='Pitch')
smaLine, = axes[0].plot([],[],color='#ff0000',LineWidth=0.5)
ewmaLine, = axes[0].plot([],[],color='#e4239d',LineWidth=0.5)

#maxLine, = pyplot.plot( [], [],color='r',LineWidth=0.2)
#minLine, = pyplot.plot( [], [],color='r',LineWidth=0.2)
lineStopped_max, = axes[0].plot( [], [],color='#ff9933',LineWidth=0.2)
#lineStopped_min, = axes[0].plot( [], [],color='#ff9933',LineWidth=0.2)
#lineOperating_min, = axes[0].plot( [], [],color='#ff0000',LineWidth=0.2)
lineOperating_max, = axes[0].plot( [], [],color='#ff0000',LineWidth=0.2)
symbol_operating, = axes[0].plot([],[],'go',alpha=0.4)
symbol_alert, = axes[0].plot([],[],'r*',alpha=0.4)
symbol_signal_operating, = axes[0].plot([],[],'kv',alpha=0.8)
symbol_signal_alert, = axes[0].plot([],[],'rv',alpha=0.8)

pLine_hist, = axes[1].plot(t,p,color='#808080',LineWidth=1.5,label='Pitch',)




# 1 for stopped; 2 for operating; 3 for alert
currentStatus = -1
lastRec = ''
msgsent = 0
alertCount = 0


def update(frame):
    count = 0
    count_ope = 0
    count_ale = 0

    x_alerts = []
    y_alerts = []
    x_operating = []
    y_operating = []
    x_signal_alert = []
    y_signal_alert = []
    x_signal_operating = []
    y_signal_operating = []

    data = rd.getAllData()
    p = data[0] #rd.getPitchData()
    r = data[1] #rd.getRollData()
    pr = data[2] #rd.getPitchRollSum()
    dt = data[3]

    p_hist = rd.getAllData(limit=500)[2]

    if len(p) == 0:
        print('como assim')

    #p = rd.getPitchData()
    #r = rd.getRollData()
    #pr = rd.getPitchRollSum()

    if (len(p) != len(r) ) or (len(r) != len(pr) ) or (len(p) != len(pr)):
        print("variaveis tem tamanho diferente", len(p), len(r), len(pr))

    newStatus = 1 #set stopped
    #----------------------
    if calc_type == 1:
        p = r
    else:
        if calc_type == 2:
            p = pr
    #----------------------
    n = p.size
    tx = rd.getSecondsDiff()
    t = np.linspace(0,tx,n)

    n2 = p_hist.size
    tx_hist = rd.getSecondsDiff()
    t_hist = np.linspace(0,tx,n2)

    sma = cl.calcSMA(p)
    #sma2 = [i[0] for i in sma] #for fill_between
    ewma = cl.calcEWMA(p)
    #ewma2 = [i[0] for i in ewma] #for fill_between


    limits = cl.getSMARanges()
    range_stopped = limits[0]
    range_operating = limits[1]
    range_alert = limits[2]

    #if len(p) > 200: # keep the last x elements
    #    p = p[-200:]
    #    t = t[-200:]
    #    sma = sma[-200:]
    #    ewma = ewma[-200:]

    pLine.set_data(t, p)
    smaLine.set_data(t,sma)
    #ewmaLine.set_data(t,ewma)
    #lineStopped_min.set_data([t[0],tx], [range_stopped[0],range_stopped[0]])
    lineStopped_max.set_data([t[0],tx], [range_stopped[1],range_stopped[1]])
    #lineOperating_min.set_data([t[0],tx], [range_operating[0][0],range_operating[0][0]])
    lineOperating_max.set_data([t[0],tx], [range_operating[1][1],range_operating[1][1]])


    pLine_hist.set_data(t_hist, p_hist)
    #pyplot.gca().collections.clear()
    #pyplot.fill_between(t, sma2 , color='#11ff00',alpha=0.1) # p or sma2 or ewma2

    for i in sma: #could use p (p,r,pr) or sma or ewma
        
        status = cl.checkSMARanges(i)
        isOperating = status[0]
        isAlert = status[1]

        if isOperating:
            x_operating.append(t[count])
            y_operating.append(i)
            if (count >= sma.size-20): #count if is recent data (20 latest)
                count_ope += 1

        if isAlert:
            x_alerts.append(t[count])
            y_alerts.append(i)
            if (count >= sma.size-20): #count if is recent data (20 latest)
                count_ale += 1

        count = count + 1

    tot = sma[-20:].size # count if have at least 20 last elements
    pct_ope = (count_ope * 100) / tot
    pct_ale = (count_ale * 100) / tot

    if pct_ope > 40:
        x_signal_operating.append(t[count-1])
        y_signal_operating.append(sma[count-1])
        newStatus = 2 #set operating

    if pct_ale > 40:
        x_signal_alert.append(t[count-1])
        y_signal_alert.append(sma[count-1])
        newStatus = 3 #set alert

    global currentStatus #forces to get the global variable
    global alertCount #forces to get the global variable
    if newStatus != currentStatus:
        if newStatus == 1: #stopped
            mqtt.led(1) #set yellow
        elif newStatus == 2: #operating
            mqtt.led(2) #set green
        elif newStatus == 3: #alert
            mqtt.led(3) #set red
            alertCount += 1
            mqtt.alert(alertCount)
        else:
            mqtt.led(0) #clear
        currentStatus = newStatus


    global lastRec #forces to get the global variable
    index = -1
    if list(dt).count(lastRec) > 0:
        index = list(dt).index(lastRec)
    if index < len(sma):
        index += 1 #go to next record
        #global msgsent    
        #print(msgsent, index)
        while index < len(sma):
            #if index < 2:
            #    print("opa")
            mqtt.vibration(round(sma[index][0],2))
            #msgsent += 1
            
            index += 1
    lastRec = dt[-1]


    #set the alert icon
    symbol_alert.set_data(x_alerts,y_alerts)
    symbol_operating.set_data(x_operating,y_operating)
    symbol_signal_alert.set_data(x_signal_alert,y_signal_alert)
    symbol_signal_operating.set_data(x_signal_operating,y_signal_operating)

    #figure.gca().relim()
    axes[0].relim()
    axes[1].relim()
    axes[0].autoscale_view()
    axes[1].autoscale_view()
    

    return pLine,

#t1 = threading.Thread(target=sim.run, args=[])
#t1.start()

t2 = threading.Thread(target=mqtt.loop, args=[])
t2.start()

#clear the alertCount
mqtt.alert(0)
#clear the led
mqtt.led(0)

animation = FuncAnimation(figure, update, interval=5)
#pyplot.tight_layout()
pyplot.show()

mqtt.stop()
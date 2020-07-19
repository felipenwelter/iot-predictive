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
import simulate as sim
import calc as cl

# definição de apresentação do gráfico
pyplot.rcParams['figure.figsize'] = [14,7]
pyplot.rcParams.update({'font.size':18})

figure, axes = pyplot.subplots(
        nrows=2, ncols=1, sharex=True, sharey=False, 
        gridspec_kw={'height_ratios':[3,1]}
        )

# remove labels no eixo x
for label in axes[1].get_xticklabels():
    label.set_visible(False)

# adiciona nome de label no eixo y
axes[0].set_ylabel('Recent')
axes[1].set_ylabel('Historic')

# t = eixo x do gráfico principal
# p, r e pr = valores de pitch e roll
t, p, r, pr = [], [], [], []
# e para gráfico de histórico
p_hist, t_hist = [], []

# linhas (plot) para pitch/roll e sma
pLine, = axes[0].plot(t,p,color='c',LineWidth=1.5,label='Pitch',)
smaLine, = axes[0].plot([],[],color='#ff0000',LineWidth=0.5)
pLine_hist, = axes[1].plot(t,p,color='#808080',LineWidth=1.5,label='Pitch',)

# linhas horizontais para representar os limites
lineStopped_max, = axes[0].plot( [], [],color='#ff9933',LineWidth=0.2)
lineOperating_max, = axes[0].plot( [], [],color='#ff0000',LineWidth=0.2)
#lineStopped_min, = axes[0].plot( [], [],color='#ff9933',LineWidth=0.2)
#lineOperating_min, = axes[0].plot( [], [],color='#ff0000',LineWidth=0.2)

# linha de símbolo para indicar acionamento de LED`s
symbol_operating, = axes[0].plot([],[],'go',alpha=0.4)
symbol_alert, = axes[0].plot([],[],'r*',alpha=0.4)
symbol_signal_operating, = axes[0].plot([],[],'kv',alpha=0.8)
symbol_signal_alert, = axes[0].plot([],[],'rv',alpha=0.8)

# inicializa variável para acionamento do LED - 1 for stopped; 2 for operating; 3 for alert
currentStatus = -1

# variável para controle das últimas informações plotadas
lastRec = ''

# variável para controle do número de alertas (em tempo de execução)
alertCount = 0


#--------------------------------------------------------------------------
# Função: Realiza a atualização dos dados no gráfico. Aciona a leitura dos
#         dados gravados no banco e realização dos cálculos de vibração
# Parâmetros: frame (enviado por FuncAnimation do matplotlib.animation)
#--------------------------------------------------------------------------
def update(frame):
    
    # variaveis para controle interno dos loops
    count = 0
    count_ope = 0
    count_ale = 0

    # arrays para armazenar posições de símbolos de alerta e plotar
    x_alerts = []
    y_alerts = []
    x_operating = []
    y_operating = []
    x_signal_alert = []
    y_signal_alert = []
    x_signal_operating = []
    y_signal_operating = []


    #-------------------------------
    # Realiza a leitura dos dados
    #-------------------------------   
    data = rd.getAllData()
    p = data[0] #Pitch
    r = data[1] #Roll
    pr = data[2] #tPitch Roll Sum
    dt = data[3]

    p = pr

    p_hist = rd.getAllData(limit=500)[2]

    if len(p) == 0:
        print('### Erro na leitura de dados')

    newStatus = 1 #set stopped

    n = p.size
    tx = rd.getSecondsDiff(n)
    t = np.linspace(0,tx,n)

    n2 = p_hist.size
    tx_hist = rd.getSecondsDiff(n2)
    t_hist = np.linspace(0,tx,n2)

    sma = cl.calcSMA(p)
    #ewma = cl.calcEWMA(p)


    # ---------- Realiza os cálculos de vibração ---------------------------------
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
    #-----------------------------------------------------------------------------

    # ---------- Acionamento dos LED`s -------------------------------------------
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
    #-----------------------------------------------------------------------------

    # ---------- Envio de dados para dashboard mobile ----------------------------
    global lastRec #forces to get the global variable
    index = -1
    if list(dt).count(lastRec) > 0:
        index = list(dt).index(lastRec)
    if index < len(sma):
        index += 1 #go to next record
        while index < len(sma):
            #if index < 2:
            #    print("opa")
            mqtt.vibration(round(sma[index][0],2))
            
            index += 1
    lastRec = dt[-1]
    #-----------------------------------------------------------------------------

    limits = cl.getSMARanges()
    range_stopped = limits[0]
    range_operating = limits[1]
    range_alert = limits[2]

    # Atualiza valores de cada linha plotada no gráfico
    pLine.set_data(t, p)
    smaLine.set_data(t,sma)
    lineStopped_max.set_data([t[0],tx], [range_stopped[1],range_stopped[1]])
    lineOperating_max.set_data([t[0],tx], [range_operating[1][1],range_operating[1][1]])
    #lineStopped_min.set_data([t[0],tx], [range_stopped[0],range_stopped[0]])
    #lineOperating_min.set_data([t[0],tx], [range_operating[0][0],range_operating[0][0]])
    pLine_hist.set_data(t_hist, p_hist)
    #pyplot.gca().collections.clear()
    #pyplot.fill_between(t, sma2 , color='#11ff00',alpha=0.1) # p or sma2 or ewma2

    # Plota símbolos de alerta/operação nos gráficos
    symbol_alert.set_data(x_alerts,y_alerts)
    symbol_operating.set_data(x_operating,y_operating)
    symbol_signal_alert.set_data(x_signal_alert,y_signal_alert)
    symbol_signal_operating.set_data(x_signal_operating,y_signal_operating)

    #Atualiza e redimensiona gráfico
    axes[0].relim()
    axes[1].relim()
    axes[0].autoscale_view()
    axes[1].autoscale_view()

    return pLine,




# Somente para realiza simulação
#t1 = threading.Thread(target=sim.run, args=[])
#t1.start()

# Loop para receber dados MQTT do dashboard mobile
t2 = threading.Thread(target=mqtt.loop, args=[])
t2.start()

# Limpa o alertCount
mqtt.alert(0)

# Limpa os LED`s
mqtt.led(0)

# Atualização do gráfico (online)
animation = FuncAnimation(figure, update, interval=5)
pyplot.show()

# Ao fechar tela, interrompe conexão mqtt
mqtt.stop()
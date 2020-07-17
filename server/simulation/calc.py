## https://www.youtube.com/watch?v=s2K1JfNR7Sc

import numpy as np
import matplotlib.pyplot as plt
import read_data as rd
import pandas as pd #https://pandas.pydata.org/pandas-docs/version/0.24/reference/api/pandas.Series.ewm.html

def getHighLow(arr,last=-1):
    max, min = 0, 0
    if last == -1: last = arr.size
    if arr.size > 0:
        max = arr[-(last):].max() #get the higher value of the nLast elements
        min = arr[-(last):].min()
    return [max, min]

def getSMARanges():
    stopped = np.array([-1.5,1.5]) #np.array([-0.8,0.8])
    operating = np.array([[-4.5,-1.5],[1.5,4.5]]) #np.array([[-1.5,-0.8],[0.8,1.5]])
    alert = np.array([-4.5,4.5]) #np.array([-1.5,1.5])
    return [stopped, operating, alert]


def calcSMA(arr):
    df = pd.DataFrame(arr)
    sma = df.ewm(span=10).mean()
    sma = sma.values
    return sma

def calcEWMA(arr):
    df = pd.DataFrame(arr)
    ewma = df.rolling(window=10).mean()
    ewma = ewma.values
    return ewma

def calcMSV(arr):
    mean = np.mean(arr)
    std = np.std(arr)
    var = std ** 2.0
    return [mean, std, var]

def checkSMARanges(i):
    limits = getSMARanges()
    range_stopped = limits[0]
    range_operating = limits[1]
    range_alert = limits[2]

    isOperating = ((i >= range_operating[1][0] and i <= range_operating[1][1]) or #chek superior limits
                       (i >= range_operating[0][0] and i <= range_operating[0][1])) #check inferior limits
    isAlert = ((i >= range_alert[1]) or #check superior limits
                ( i <= range_alert[0])) #check inferior limits

    return (isOperating, isAlert)


def main():
    p = rd.getPitchData()
    r = rd.getRollData()
    pr = rd.getPitchRollSum()

    hl = getHighLow(p)

    n = p.size
    tx = rd.getSecondsDiff()
    t = np.linspace(0,tx,n)

    freq = np.fft.fftfreq(n)
    mascara = freq > 0

    fft_calculo_r = np.fft.fft(r)
    fft_abs_r = (-2.0)*np.abs(fft_calculo_r / n)

    fft_calculo_p = np.fft.fft(p)
    fft_abs_p = (-2.0)*np.abs(fft_calculo_p / n)







## Cross checks for power spectrum
# Mean, Standard Deviation, and Variance of the original signal

#print (mean_y, std_y, var_y)







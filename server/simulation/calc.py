import numpy as np
import matplotlib.pyplot as plt
import read_data as rd
import pandas as pd #https://pandas.pydata.org/pandas-docs/version/0.24/reference/api/pandas.Series.ewm.html

#---------------------------------------------------------------
# Função: Busca os intervalos de repouso, operacao e alerta
# Retorno: array no formato (repouso, operacao, alerta), cada um
#          definido por dois valores (inferior, superior)
#---------------------------------------------------------------
def getSMARanges():
    stopped = np.array([-1.5,1.5]) #np.array([-0.8,0.8])
    operating = np.array([[-4.5,-1.5],[1.5,4.5]]) #np.array([[-1.5,-0.8],[0.8,1.5]])
    alert = np.array([-4.5,4.5]) #np.array([-1.5,1.5])
    return [stopped, operating, alert]


#-----------------------------------------------------------------------
# Função: Calcula a média móvel simples (SMA) para os valores do array
# Parâmetros: arr - array com valores da série a calcular
# Retorno: array com valores do SMA calculados para a série
#-----------------------------------------------------------------------
def calcSMA(arr):
    df = pd.DataFrame(arr)
    sma = df.ewm(span=10).mean()
    sma = sma.values
    return sma


#-----------------------------------------------------------------------
# Função: Calcula a média móvel exponencial (EWMA) para os valores do array
# Parâmetros: arr - array com valores da série a calcular
# Retorno: array com valores do EWMA calculados para a série
#-----------------------------------------------------------------------
def calcEWMA(arr):
    df = pd.DataFrame(arr)
    ewma = df.rolling(window=10).mean()
    ewma = ewma.values
    return ewma


#-----------------------------------------------------------------------------
# Função: Calcula média aritmética (mean), desvio padrão (std) e a variância
#         (densidade espectral da potência, quadrado do desvio padrão)
# Parâmetros: arr - array com valores da série a calcular
# Retorno: array de três posições com os valores calculados para a série
#-----------------------------------------------------------------------------
def calcMSV(arr):
    mean = np.mean(arr)
    std = np.std(arr)
    var = std ** 2.0
    return [mean, std, var]


#-----------------------------------------------------------------------
# Função: Verifica em qual faixa um valor se encontra
# Parâmetros: i - valor a ser verificado
# Retorno: array que define true/false para (operando, alerta)
#-----------------------------------------------------------------------
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






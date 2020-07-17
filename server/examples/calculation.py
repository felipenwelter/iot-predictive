## https://www.youtube.com/watch?v=s2K1JfNR7Sc

import numpy as np
import matplotlib.pyplot as plt
import read_data as rd
import pandas as pd #https://pandas.pydata.org/pandas-docs/version/0.24/reference/api/pandas.Series.ewm.html

plt.rcParams['figure.figsize'] = [14,6]
plt.rcParams.update({'font.size':18})

p = rd.getPitchData()
r = rd.getRollData()
pr = rd.getPitchRollSum()

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
mean_p = np.mean(p)
std_p = np.std(p)
var_p = std_p ** 2.0
#print (mean_y, std_y, var_y)

p_df = pd.DataFrame(p)
p_sma = p_df.ewm(span=10).mean()
p_sma = p_sma.values
p_ewma = p_df.rolling(window=10).mean()
p_ewma = p_ewma.values

r_df = pd.DataFrame(r)
r_sma = r_df.ewm(span=10).mean()
r_sma = r_sma.values
r_ewma = r_df.rolling(window=10).mean()
r_ewma = r_ewma.values

pr_df = pd.DataFrame(pr)
pr_sma = pr_df.ewm(span=10).mean()
pr_sma = pr_sma.values
pr_ewma = pr_df.rolling(window=10).mean()
pr_ewma = pr_ewma.values


mean_r = np.mean(r)
std_r = np.std(r)
var_r = std_r ** 2.0
#print (mean_r, std_r, var_r)


fig,axs = plt.subplots(3,1,sharex=True,sharey=True)

fig.text(0.0, 0.7, round(mean_p,2))
fig.text(0.0, 0.6, round(std_p,2))
fig.text(0.0, 0.5, round(var_p,2))

#idx = 1
#while idx < len(r):
#    r[idx] -= mean_r
#    idx += 1


plt.sca(axs[0])
#plt.figure(1)
#plt.title("Original Pitch")
plt.plot(t,p,color='c',LineWidth=1.5,label='Pitch')
#plt.fill_between(t, p, color='c')
plt.plot(t,p_sma,color='r',LineWidth=0.8,label='SMA')
plt.plot(t,p_ewma,color='b',LineWidth=0.8,label='EWMA')
#plt.legend()

#plt.sca(axs[1])
##plt.figure(2)
##plt.title("Sinal fft")
#plt.plot(freq[mascara],fft_abs_p[mascara],label='Pitch fft')
#plt.legend()

plt.sca(axs[1])
#plt.figure(2)
#plt.title("Original Roll")
plt.plot(t,r,color='c',LineWidth=1.5,label='Roll')
#plt.fill_between(t, r, color='c')
plt.plot(t,r_sma,color='r',LineWidth=0.8,label='SMA')
plt.plot(t,r_ewma,color='b',LineWidth=0.8,label='EWMA')
#plt.legend()

plt.sca(axs[2])
#plt.figure(2)
#plt.title("Sinal fft")
#plt.plot(freq[mascara],fft_abs_r[mascara],label='Roll fft')
plt.plot(t,pr,color='c',LineWidth=1.5,label='P+R')
plt.fill_between(t, pr, color='c')
plt.plot(t,pr_sma,color='r',LineWidth=0.8,label='SMA')
plt.plot(t,pr_ewma,color='b',LineWidth=0.8,label='EWMA')
#plt.legend()


plt.show()
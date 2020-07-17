## https://www.youtube.com/watch?v=s2K1JfNR7Sc

import numpy as np
import matplotlib.pyplot as plt
import read_data as rd
plt.rcParams['figure.figsize'] = [14,6]
plt.rcParams.update({'font.size':18})

p = rd.getPitchData()
r = rd.getRollData()

n = p.size
tx = rd.getSecondsDiff()
t = np.linspace(0,tx,n)

freq = np.fft.fftfreq(n)
mascara = freq > 0

fft_calculo_r = np.fft.fft(r)
fft_abs_r = (-2.0)*np.abs(fft_calculo_r / n)

fft_calculo_p = np.fft.fft(p)
fft_abs_p = (-2.0)*np.abs(fft_calculo_p / n)

fig,axs = plt.subplots(4,1)







## Cross checks for power spectrum
# Mean, Standard Deviation, and Variance of the original signal
mean_y = np.mean(p)
std_y = np.std(p)
var_y = std_y ** 2.0
print (mean_y, std_y, var_y)

mean_y = np.mean(r)
std_y = np.std(r)
var_y = std_y ** 2.0
print (mean_y, std_y, var_y)




plt.sca(axs[0])
#plt.figure(1)
#plt.title("Original Pitch")
plt.plot(t,p,color='c',LineWidth=1.5,label='Pitch')
plt.legend()

plt.sca(axs[1])
#plt.figure(2)
#plt.title("Sinal fft")
plt.plot(freq[mascara],fft_abs_p[mascara],label='Pitch fft')
plt.legend()

plt.sca(axs[2])
#plt.figure(2)
#plt.title("Original Roll")
plt.plot(t,r,color='c',LineWidth=1.5,label='Roll')
plt.legend()

plt.sca(axs[3])
#plt.figure(2)
#plt.title("Sinal fft")
plt.plot(freq[mascara],fft_abs_r[mascara],label='Roll fft')
plt.legend()



plt.show()
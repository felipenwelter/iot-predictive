## https://www.youtube.com/watch?v=s2K1JfNR7Sc

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [14,6]
plt.rcParams.update({'font.size':18})

# Create a simple signal with two frequencies
dt = 0.001
t = np.arange(0,1,dt)
f = np.sin(2 * np.pi *50 * t) + np.sin(2 * np.pi * 120 * t) # sum of two frequencies
f_clean = f
f = f + 2.5 * np.random.randn(len(t))

#plt.plot(t,f,color='c',LineWidth=1.5,label='Noisy')
#plt.plot(t,f_clean,color='k',LineWidth=2,label='Clean')
#plt.xlim(t[0],t[-1])
#plt.legend()
#plt.show()


## Compute the Fast Fourier Transform (FFT)
n = len(t)
fhat = np.fft.fft(f,n)                      # Compute the FFT
PSD = fhat * np.conj(fhat) / n              # Power Spectrum (power per frequency)
freq = (1 / (dt*n)) * np.arange(n)          # Create x-axis of frequencies
L = np.arange(1,np.floor(n/2),dtype='int')  # Only plot the first half of

#fig,axs = plt.subplots(2,1)

#plt.sca(axs[0])
#plt.plot(t,f,color='c',LineWidth=1.5,label='Noisy')
#plt.plot(t,f_clean,color='k',LineWidth=2,label='Clean')
#plt.xlim(t[0],t[-1])
#plt.legend()

#plt.sca(axs[1])
#plt.plot(freq[L],PSD[L],color='c',LineWidth=2,label='Noisy')
#plt.xlim(freq[L[0]],freq[L[-1]])
#plt.legend()
## axis x in Hz
## axis y is power
#plt.show()


## Use the PSD to filter out the noise
indices = PSD > 100             # Find all the frequencies with large power
PSDClean = PSD * indices        # Zero out all the others
fhat = indices * fhat           # Zero out samll Fourier coeffs. in Y
ffilt = np.fft.ifft(fhat)       # Inverse FFT for filtered time signal

fig,axs = plt.subplots(3,1)

plt.sca(axs[0])
plt.plot(t,f,color='c',LineWidth=1.5,label='Noisy')
plt.plot(t,f_clean,color='k',LineWidth=2,label='Clean')
plt.xlim(t[0],t[-1])
plt.legend()

plt.sca(axs[1])
plt.plot(t,ffilt,color='k',LineWidth=2,label='Filtered')
plt.xlim(t[0],t[-1])
plt.legend()
# axis x in Hz
# axis y is power

plt.sca(axs[2])
plt.plot(freq[L],PSD[L],color='c',LineWidth=2,label='Noisy')
plt.plot(freq[L],PSDClean[L],color='k',LineWidth=1.5,label='Filtered')
plt.xlim(freq[L[0]],freq[L[-1]])
plt.legend()
plt.show()
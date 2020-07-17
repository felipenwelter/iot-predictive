import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, fftfreq, ifft

#####################################################
#https://www.youtube.com/watch?v=P571FXS33wg

## Setup for domain
# number of points
n = 1000

# Distance (in meters) or time period (in seconds)
Lx = 100

# angular frequency
omg = 2.0 * np.pi/Lx

## Creating individual signals
x = np.linspace(0, Lx, n)
y1 = 1.0 * np.cos( 5.0 * omg * x)
y2 = 2.0 * np.sin(10.0 * omg * x)
y3 = 0.5 * np.sin(20.0 * omg * x)

## Full signal
y = y1 + y2 + y3

## Cross checks for power spectrum
# Mean, Standard Deviation, and Variance of the original signal
mean_y = np.mean(y)
std_y = np.std(y)
var_y = std_y ** 2.0

print (mean_y, std_y, var_y)

## Preparatory steps
# Creates all the necessary frequencies
freqs = fftfreq(n)

# mask array to be used for power spectra.
# ignoring half the values, as they are complex conjucates of the other
mask = freqs > 0

# wave numbers - number of waves of the signal needs to occupy the domain.
# no of waves (per domain length)
nwaves = freqs * n

# Create all the necessary time periods (or distance)
times = 1.0 / freqs
times[freqs == 0.0] = Lx

## FFT and power spectra calculations
# fft values
fft_vals = fft(y)

# true theoretical fft
fft_theo = 2.0 * np.abs(fft_vals / n)

# this is the power spectra
ps = 2.0 * (np.abs(fft_vals/n) ** 2.0)

# power by variance
pow_var = ps / var_y * 100.0

# freq. power spectra - for variance preserving form
fps = ps * freqs

# sum of power spectrum values
print(np.sum(ps[mask]))

plt.figure(1)
plt.title('Original signal')
plt.plot(x, y, color='xkcd:salmon', label='original')
plt.legend()

plt.figure(2)
#plt.plot(freqs, fft_vals, label="raw fft values")
#plt.title("Raw FFT values - need more processing")
plt.plot(freqs[mask], fft_theo[mask], label='true fft values')
plt.title('True FFT values')

plt.figure(3)
plt.plot(freqs[mask], ps[mask], label='frequency vs spectra')
plt.title('Power Spectrum Example - frequency vs spectra')

plt.figure(4)
plt.plot(nwaves[mask], ps[mask], label='wavenumber vs spectra')
plt.title('Power Spectrum Example - wavenumber vs spectra')

plt.figure(5)
plt.plot(times[mask], ps[mask], label='timeperiod vs spectra')
plt.title('Power Spectrum Example - timeperiod vs spectra')

plt.figure(6)
plt.plot(nwaves[mask], pow_var[mask], label='wavenumber vs power by variance')
plt.title('Power Spectrum Example - wavenumber vs power by variance')

plt.figure(7)
plt.semilogx(freqs[mask], fps[mask], label='frequency vs variance preserving spectra')
plt.title('Power Spectrum Example - frequency vs variance preserving spectra')

plt.show()


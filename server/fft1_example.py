import matplotlib.pyplot as plt
import numpy as np

#####################################################
#https://www.youtube.com/watch?v=hv5V2CikvIc
#matriz = np.array([[1,2,3],[4,5,6],[7,8,9]])
#print(np.fft.fft(matriz[1,:]))
#print(np.fft.fft2(matriz))


#####################################################
#https://www.youtube.com/watch?v=uDz-KirOmw8
n = 1000
tx = 200
w = 2.0 * np.pi/tx

t = np.linspace(0,tx,n)
print(t)
s1 = 2.0 * np.cos(2.0 * w * t)
s2 = 1.0 * np.cos(30.0 * w * t)
s = s1 + s2

freq = np.fft.fftfreq(n)
mascara = freq > 0

fft_calculo = np.fft.fft(s)
fft_abs = 2.0 * np.abs(fft_calculo / n)

plt.figure(1)
plt.title("Sinal original")
plt.plot(t,s)

plt.figure(2)
plt.title("Sinal fft")
plt.plot(freq[mascara],fft_abs[mascara])
plt.show()


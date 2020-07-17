from datetime import datetime
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from random import randrange

pyplot.rcParams['figure.figsize'] = [14,6]
pyplot.rcParams.update({'font.size':18})

x_data, y_data = [], []

figure = pyplot.figure()
line, = pyplot.plot_date(x_data, y_data, '-')

def update(frame):
    x_data.append(datetime.now())
    y_data.append(randrange(0, 100))

    if len(y_data) > 20:
        x_data.pop(0)
        y_data.pop(0)

    line.set_data(x_data, y_data)
    figure.gca().relim()
    figure.gca().autoscale_view()

    return line,

animation = FuncAnimation(figure, update, interval=100)

pyplot.show()
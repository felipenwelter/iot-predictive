import matplotlib.pyplot as plt

tPlot, axes = plt.subplots(
        nrows=2, ncols=1, sharex=True, sharey=False, 
        gridspec_kw={'height_ratios':[3,1]}
        )

tPlot.suptitle('node', fontsize=20)

axes[0].plot(range(10),'ro-') 
axes[1].plot(range(10),'bo-') 

plt.show()
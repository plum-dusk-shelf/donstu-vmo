from matplotlib import pyplot as plt
import numpy as np
from PIL import Image

x = range(-100, 101)
x2 = x
y = [i ** 2 for i in x]
y2 = y

fig,axs = plt.subplots(2,1,figsize=(10, 8))
axs[0].xlabel = 'pisya'
axs[0].ylabel = 'popa'
# plt.grid(which='major', linewidth=1)
# plt.tick_params(which ='major', length=10)
axs[0].plot(x, y)


axs[1].bar(x, y)
axs[1].plot()

plt.show()

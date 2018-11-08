import numpy as np
import matplotlib.pyplot as plt

N = 4
ind = np.arange(N)  # the x locations for the groups
width = 0.27       # the width of the bars

fig = plt.figure()
ax = fig.add_subplot(111)

yvals = [14, 17.4, 13.4, 6.2]
rects1 = ax.bar(ind, yvals, width, color='r')
zvals = [10.8,13.8,4.4, 1.6]
rects2 = ax.bar(ind+width, zvals, width, color='g')
kvals = [11.4,8.2,1.6, 0]
rects3 = ax.bar(ind+width*2, kvals, width, color='b')

ax.set_title('Final Fitness for each Population Size', y = 1.03)
ax.set_ylabel('Final Fitness')
ax.set_xlabel('Population Size')
ax.set_xticks(ind+width)
ax.set_xticklabels( ('10', '100', '1000', '10000') )
ax.legend( (rects1[0], rects2[0], rects3[0]), ('Grid 1', 'Grid 2', 'Grid 3') )

def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.show()
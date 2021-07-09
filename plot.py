import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

num_files   = 3

filename1   = ''
filename2   = ''
filename3   = ''


plot_title  = 'Footprint Comparison'
plot_label1 = '90prime'
plot_label2 = 'decam'
plot_label3 = ''

savefile    = 'sky_dist_comp.png'


filenames   = []
plot_labels = []

for i in range(1, num_files + 1):
    filenames.append(globals()['filename{}'.format(i)])


for i in range(0, num_files):
    ra     = []
    dec    = []

    with open(filenames[i], "r") as f:
        data = f.readlines()
        for line in data:
            ra.append(line.split()[0])
            dec.append(line.split()[1])

    ra  = np.asfarray(ra, float)
    dec = np.asfarray(dec, float)

    plt.scatter(ra, dec, alpha = 0.5)
    plt.xlabel("RA")
    plt.ylabel("DEC")

plt.legend(title = plot_title)
plt.savefig(savefile)

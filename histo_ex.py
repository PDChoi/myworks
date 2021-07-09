import matplotlib.pyplot as plt
import numpy as np

data = [] ## data list

data_range_min = min(data)
data_range_max = max(data)
number_of_bins = 40
bin_interval   = (data_range_min - data_range_max)/float(number_of_bins)

savefig_name   = 'put_name_here.png'



bins = np.arange(data_range_min, data_range_max, bin_interval)

######## Plot histogram: Use MATPLTLIB.PYPLOT ########
plt.hist(data, bins = bins, normed = True, stacked = True, histtype = 'step', lw = 2, color = 'teal', label = 'OOO Histogram')  ## Plot histogram. Erase 'lw' if you don't wnat to use 'histtype'.
plr.legend()  ## Turning on label
plt.savefig(savefig_name)


######## To check values of the histogram: Use NUMPY #########
histo, bins = np.histogram(data, bins, normed = True)

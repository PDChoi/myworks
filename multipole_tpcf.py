import numpy as np
import halotools
from halotools.mock_observables import tpcf
import time
import matplotlib as mpl
import matplotlib.pyplot as plt


mpl.use('Agg')


smin = 0.01
smax = 200.
boxsize = 3000.
s_binsize = 5
mu_binsize = 0.02


num_threads = 'max'

sum_xi = 0
sum_r2xi = 0
sum_xisq = 0

for i in range(0, filenum):
    filename = r''%(i+1)
    savefile = r''%(i+1)

    start = time.time()

    x = []
    y = []
    z = []

    with open(filename, "r") as f:
        data = f.readlines()
        for line in data:
            x.append(line.split()[0])
            y.append(line.split()[1])
            z.append(line.split()[2])

    x = np.asfarray(x, float)
    y = np.asfarray(y, float)
    z = np.asfarray(z, float)

    pos = np.vstack((x,y,z)).T
    sbins = np.arange(smin, smax, sbinsize)
    mubins = np.arange(mumin, mumax, mubinsize)
    period = boxsize


    s_mu = s_mu_tpcf(pos, sbins, mubins, period = period, num_threads = 'max')

    xi_monop = tpcf_multipole(s_mu, mubins, order=0)
    xi_quadrap = tpcf_multipole(s_mu, mubins, order=1)

    
    s = sbins[1:]-sbinsize/2
    r2xi1 = s**2 * xi_monop
    r2xi2 = s**2 * 

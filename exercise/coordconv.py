import numpy as np
import astropy
import math
import fitio
from astropy.cosmology import FlatLambdaCDM
from astropy.coordinates import SkyCoord
import astropy.units as u
import random


H0   = 68
Om   = 0.3
Tcmb = 2.725

filepath        = ''
outputpath      = ''

file_start      = 1
file_end        = 10
filename_prefix = 'zevoEZmock_QSO_v1.8_veto_ngc_'
filename_suffix = '.dat'
random_filename = 'randx100_QSO_v1.8_veto_ngc.dat'

output_prefix   = 'ezmock_cart-'

ra_col  = 1 
dec_col = 2
z_col   = 3
w_col   = 4

ran_ra_col  = 1
ran_dec_col = 2
ran_z_col   = 3
ran_w_col   = 4

#### O P T I O N S ####
datatype = 1   
# data type  1: ascii    2: fits
In_fixed_digits  = 1
Out_fixed_digits = 0
Do_combination   = 1



#############################################################################

cosmo = FlatLambdaCDM(H0 = H0 * u.km/u.s/u.Mpc, Om0 = Om, Tcmb0 = Tcmb * u.K)

ra       = []
dec      = []
redshift = []
weight   = []

r_ra       = []
r_dec      = []
r_redshift = []
r_weight   = []


def readascii(filename):
    with open(filename

def readfits(filename):
    data = fitsio.read(filename)
    d = cosmo.angular_diameter_distance(data['Z'])
    c = SkyCoord(ra = data['RA']*u.degree, dec = data['DEC']*u.degree, distance = d)

    x = c.cartesian.x
    y = c.cartesian.y
    z = c.cartesian.z
    w = data['WEIGHT_FKP']




if Do_combination:
    with open(random_filename, "r") as r:
        rdata = r.readlines()
        for rline in rdata:
            r_ra.append(line.split()[ran_ra_col-1])
            r_dec.append(line.split()[ran_dec_col-1])
            r_redshift.append(line.split()[ran_z_col-1])
            r_weight.append(line.split()[ran_w_col-1])

    r_ra       = np.asfarray(r_ra, float)
    r_dec      = np.asfarray(r_dec, float)
    r_redshift = np.asfarray(r_redshift, float)
    r_weight   = np.asfarray(r_weight, float)

    rdist = cosmo.luminosity_distance(r_redshift)
    rc = SkyCoord(ra = r_ra * u.degree, dec = r_dec * u.degree, distance = rdist, frame = 'icrs')
    rx = rc.cartesian.x
    ry = rc.cartesian.y
    rz = rc.cartesian.z

    rpos  = np.vstack((rx, ry, rz, r_weight)).T
    rsave = open(randomfilecart, 'w')
    np.savetxt(rsave, rpos, fmt=['%f', '%f', '%f', '%f'])



for filenum in range(file_start, file_end+1):
    if In_fixed digits:
        if abs(math.log10(filenum)) == 0:
            filename = filepath + filename_prefix + '000' + filenum + suffix
        if abs(math.log10(filenum)) == 1:
            filename = filepath + filename_prefix + '00' + filenum + suffix
        if abs(math.log10(filenum)) == 2:
            filename = filepath + filename_prefix + '0' + filenum + suffix
        if abs(math.log10(filenum)) == 3:
            filename = filepath + filename_prefix + filenum + suffix

    with open(filename, "r") as f:
        data = f.readlines()
        for line in data:
            ra.append(line.split()[ra_col-1])
            dec.append(line.split()[dec_col-1])
            redshift.append(line.split()[z_col-1])
            weight.append(line.split()[w_col-1])

    ra       = np.asfarray(ra, float)
    dec      = np.asfarray(dec, float)
    redshift = np.asfarray(redshift, float)

    dist = cosmo.luminosity_distance(redshift)
    c = SkyCoord(ra = ra * u.degree, dec = dec * u.degree, distance = dist, frame = 'icrs')
    x = c.cartesian.x
    y = c.cartesian.y
    z = c.cartesian.z

    pos = np.vstack((x, y, z, weight)).T


    if Do_combination:
        num_comb_file = int(len(rdata)/(len(data)*1.76))
        for comb_filenum in num_comb_file+1:
            for i in range(1.76*len(data)*(comb_filenum-1) + 1, 1.76*len(data)*comb_filenum):
                x.append(rx[i])
                y.append(ry[i])
                z.append(rz[i])
                weight.append(-r_weight[i])

            pos = np.vstack((x, y, z)).T

            out_filename = output_path + output_prefix + filenum + '_' + comb_filenum + '_comb.dat'
            save = open(out_filename, 'w')
            np.savetxt(save, pos, fmt=['%f', '%f', '%f', '%f'])

    else:
        if Out_fixed_digits:
            if abs(math.log10(filenum)) == 0:
                out_filename = output_prefix + '000' + filenum + suffix
            if abs(math.log10(filenum)) == 1:
                out_filename = output_prefix + '00' + filenum + suffix
            if abs(math.log10(filenum)) == 2:
                out_filename = output_prefix + '0' + filenum + suffix
            if abs(math.log10(filenum)) == 3:
                out_filename = output_prefix + filenum + suffix

        else:
            out_filename = output_prefix + filenum + suffix

        save = open(out_filename, 'w')
        np.savetxt(save, pos, fmt = ['%f', '%f', '%f', '%f'])

     

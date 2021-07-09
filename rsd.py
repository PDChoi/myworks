import numpy as np

filenum = 100
filepath = '/Volumes/Seagate/mock_challenge/hod1_par1/'
savepath = '/Volumes/Seagate/mock_challenge/hod1_par1_rsd/'
filename = 'mock_100_hod1_par1.txt'
redshift = 0.5
Om = 0.3 

for i in range(0, filenum):
    f_input = filepath + 'mock_%s_hod1_par1.txt'%(i+1)
    savefile = savepath + 'mock_%s_hod1_par1_rsd.txt'%(i+1)

    x  = []
    y  = []
    z  = []
    vx = []
    vy = []
    vz = []
    galtype = []
    cen_num = []
    sat_num = []
    dum1 = []
    dum2 = []
    dum3 = []
    dum4 = []

    with open(f_input, 'r') as f:
        data = f.readlines()
        for line in data:
            x.append(line.split()[0])        
            y.append(line.split()[1])        
            z.append(line.split()[2])        
            vx.append(line.split()[3])        
            vy.append(line.split()[4])        
            vz.append(line.split()[5])
            galtype.append(line.split()[6])
            cen_num.append(line.split()[7])
            sat_num.append(line.split()[8])
            dum1.append(line.split()[9])
            dum2.append(line.split()[10])
            dum3.append(line.split()[11])
            dum4.append(line.split()[12])

    x = np.asfarray(x, float)
    y = np.asfarray(y, float)
    z = np.asfarray(z, float)
    vx = np.asfarray(vx, float)
    vy = np.asfarray(vy, float)
    vz = np.asfarray(vz, float)

    r2 = x**2 + y**2 + z**2
    vr = x*vx + y*vy + z*vz
    scale_factor = 1./(1+redshift)
    E = (Om * scale_factor**(-3) +1. - Om)
    factor = 1./(100.*E)

    x += factor*x*vr/r2
    y += factor*y*vr/r2
    z += factor*z*vr/r2

    warray = np.array([x, y, z, vx, vy, vz, galtype, cen_num, sat_num, dum1, dum2, dum3, dum4]).T

    save = open(savefile, 'w')
    np.savetxt(save, warray, fmt=['%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'])

    del x, y, z, vx, vy, vz, galtype, cen_num, sat_num, dum1, dum2, dum3, dum4

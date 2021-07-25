import numpy
import scipy
from outerrim import read_outerrim
#from get_cosmo import Cosmo
from make_grid import make_grid


path = '/global/homes/g/grazi/cori_scratch_path/useful_simulations/OuterRim/HaloCatalog/'
step_num = 100
redshift = 0.695

for i in range(1, 110):
    halocat = path + 'STEP%s/'%(step_num)
    print('READ FILE #', i)
    read_outerrim(step_num, redshift, i, path = halocat)



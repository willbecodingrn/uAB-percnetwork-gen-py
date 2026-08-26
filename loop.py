import time
import numpy as np
t_s = time.time()
import pathfind as pf
import squaremaker as sm
L = 80 #amount of nodes in x and y directions
k = 2.5 #scale factor in mm
h = 2 #height of sample in mm
seed = 42
p = 1.00
pi= np.pi
angles = [0, pi/6, pi/ 4, pi/3, pi/2, 2*pi/3, 3*pi/4, 5*pi/6, pi]

for a in angles:
    print('='*4, end='')
    print(f'current angle: {a: .3f}', end='')
    print('='*4, end='\n\n')
    G, pos, pc = sm.makemesh(L, k, p, exportGraph=False, seed=seed, theta=a)

    cap, shear = pf.twoP_pressure(G)

    print(f'capillary contribution: {cap:.2f}')
    print(f'yield stress contribution: {shear: .2f}', end='\n\n\n')

t_e = time.time()
#pf.save_min_path(G, pos, path, p, pc, seed=seed) #takes p
print(f'program runtime: {((t_e - t_s) / 60):.3f} mins')
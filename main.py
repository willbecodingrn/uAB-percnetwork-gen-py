import time
t_s = time.time()
import pathfind as pf
import squaremaker as sm
import numpy as np
L = 8 #amount of nodes in x and y directions
k = 2.5 #scale factor in mm
h = 2 #height of sample in mm
seed = 42
p = 1.00

G, pos, pc = sm.makemesh(L, k, p, exportGraph=True, seed=seed) #takes p
sm.buildmesh(G, p, pos, h, L, k, seed=seed) #takes p
print(f"percolation threshold: {pc*100:.4f}%")
active = pf.active_net(G)

'''
for u, v, d in G.edges(data=True):
    print(f'from {u} to {v}:', end='')
    print(d['r'])'''

#path, cost = pf.dijkstra(active, 'tau')
cap, shear = pf.twoP_pressure(G)
cost = cap + shear
print(f'pressure threshold: {cost:.6f}')
print(f'capillary contribution: {cap:.2f}')
print(f'yield stress contribution: {shear: .2f}')

t_e = time.time()
#pf.save_min_path(G, pos, path, p, pc, seed=seed) #takes p
print(f'program runtime: {((t_e - t_s) / 60):.3f} mins')
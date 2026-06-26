import time
t_s = time.time()
import dijkstra as djk
import squaremaker as sm
L = 32 #amount of nodes in x and y directions
k = 7 #scale factor in mm
h = 3 #height of sample in mm
seed = 42
#p = 1.00

G, pos, pc = sm.makemesh(L, k, 'pc', exportGraph=True, seed=seed) #takes p
sm.buildmesh(G, pc, pos, h, L, k, seed=seed) #takes p
print(f"percolation threshold: {pc*100:.4f}%")
active = djk.active_net(G)

'''
for u, v, d in G.edges(data=True):
    print(f'from {u} to {v}:', end='')
    print(d['r'])'''

path, cost = djk.pathfind(active)
print(f'pressure threshold: {cost:.2f}')

t_e = time.time()
djk.save_min_path(G, pos, path, pc, pc, seed=seed) #takes p
print(f'program runtime: {((t_e - t_s) / 60):.3f} mins')
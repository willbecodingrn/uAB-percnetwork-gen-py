import time
t_gs = time.time()
import dijkstra as djk
import numpy as np, matplotlib.pyplot as plt
import squaremaker as sm

#region init vars
L = 32
k = 7 #scale factor in mm
h = 3 #height of sample in mm
#p = 0.65
#endregion

seeds = [42, 20, 30]

for s in seeds:
    _, _, pc = sm.makemesh(L, k, .8, s, exportGraph=False)
    pa = np.ceil(10*pc)/10

    ps = [('pc', pc), 
      (1.0,1.0),
      (pa, pa),
      (pa+0.1, pa+0.1)]
    
    for p in ps:
        print('\n\n', end='')
        print('='*4, f'seed: {s:^10}, |p: {100*float(p[1]):.2f}%', '='*4)
        t_s = time.time()
        G, pos, pc = sm.makemesh(L, k, p[0], exportGraph=True, seed=s) #takes p
        sm.buildmesh(G, p[1], pos, h, L, k, seed=s) #takes p
        print(f"percolation threshold: {pc*100:.4f}%")
        active = djk.active_net(G)

        path, cost = djk.pathfind(active)
        print(f'pressure threshold: {cost:.2f}')

        t_e = time.time()
        djk.save_min_path(G, pos, path, p[1], pc, seed=s) #takes p
        plt.close('all')
        print(f'cycle runtime: {((t_e - t_s) / 60):.3f} mins')

t_ge = time.time()
print(f'program runtime: {((t_ge - t_gs) / 60):.3f} mins')
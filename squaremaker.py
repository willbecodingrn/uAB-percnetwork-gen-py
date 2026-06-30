import networkx as nx, numpy as np, matplotlib.pyplot as plt
import cadquery as cq
import time
import newmanziff as nz

rt2 = np.sqrt(2)
t_c = 3.29

def makemesh(size, scale, p, seed=42, showGraph=False, exportGraph=True):
    #region init vars
    LX = size
    LY = size // 2
    link_length = scale/(1.64*rt2)
    r_min = 0.17*link_length
    r_max = 0.32*link_length
    global r_node
    r_node = np.ceil(10*r_max)/10
    print(f"l: {link_length:.2f}mm, r_min: {r_min:.2f}mm,\nr_max: {r_max:.2f}, r_node: {r_node}mm")
    print(f'max square len: {equivalent_square(r_max):.2f}, min square len: {equivalent_square(r_min):.2f}')
    np.random.seed(seed)
    #endregion

    #region init mesh
    G = nx.Graph()
    pos = {}
    #nodes
    for i in range(LX):
        for j in range(LY):
            x = 0.5*i*scale
            y = scale*(j-0.5) if i%2 else j*scale
            G.add_node((i, j))
            pos[(i,j)] = (x,y)
    #links
    for i in range(LX):
        for j in range(LY):
            if i%2:
                if j <= LY-1 and i < LX-1: 
                    if j >= 1: G.add_edge((i, j),(i+1,j-1), r=1,active=False)
                    G.add_edge((i,j),(i+1, j),r=1, active=False)
            else:
                if j <= LY-1 and i < LX-1: 
                    if j< LY-1: G.add_edge((i, j), (i+1, j+1),r=1,active=False)
                    G.add_edge((i,j), (i+1, j),r=1,active=False)
    #print(len(pos))
    #print(pos)
    print(f"# of Nodes: {G.number_of_nodes()}, # of Links: {G.number_of_edges()}")
    #endregion

    links = list(G.edges(data=True))
    radii = []

    #assigning radii and tau
    for n in links: 
        r = np.random.uniform(r_min,r_max)
        n[2]['r'] = r
        n[2]['tau'] = (2*t_c*link_length)/(r) #link_length and r in mm -> units cancel
        radii.append(r)
        #print(n[2])                    #for debugging
    
    pc, links_sorted = nz.percolate(G, size)

    global threshold
    threshold = pc
    if p == 'pc': p = pc
    links_sorted.reverse()
    r_gate = links_sorted[int((1-p)*len(links))][2]['r']

    for n in links:
        if n[2]['r'] <= r_gate: n[2]['active'] = True

    #region graph mesh
    t_s = time.time()
    on_links = [(u,v) for u,v, d in G.edges(data=True) if d.get('active', True)]
    off_links = [(u,v) for u, v, d in G.edges(data=True) if not d.get('active', True)]
    plt.figure(figsize=(10, 10), dpi=400)
    nx.draw_networkx_edges(G, pos, edgelist=off_links, alpha=0.1)
    nx.draw_networkx_edges(G, pos, edgelist=on_links, width=20*radii)
    nx.draw_networkx_nodes(G, pos, node_size=r_node)

    plt.axis('equal')
    if exportGraph: plt.savefig(f"outputs/figures/SD{seed}-p{round(p, 3) if p!=pc else 'c'}-{size}n.png", dpi=300, bbox_inches="tight")
    t_e = time.time()
    
    print(f'\rfigure exported, took {(t_e - t_s)/60:.2f} mins')
    if showGraph: plt.show()
    if not showGraph: plt.close('all')
    #endregion

    return G, pos, pc

def buildmesh(mesh: nx.Graph, p, pos, height, size, scale, seed=42):
    on_nodes = set()
    mainPlane = cq.Plane(origin=(0, 0, height), normal=(0, 0, 1))


    #region form links
    links = []

    t_s = time.time()
    print('forming links', end='')
    zdir = cq.Vector(0,0,1)
    for u, v, d in mesh.edges(data=True):
        if not d.get('active', True): continue
        on_nodes.add(u)
        on_nodes.add(v)

        x1, y1 = pos[u]
        x2, y2 = pos[v]
        a = equivalent_square(d['r'])

        p1 = cq.Vector(x1, y1, height)
        p2 = cq.Vector(x2, y2, height) 
        direction = p2.sub(p1).normalized()

        ydir = zdir.cross(direction).normalized()
        plane = cq.Plane(origin=(x1, y1, height - a/2), xDir=ydir, normal=direction)
        path = (cq.Workplane(mainPlane).moveTo(x1,y1).lineTo(x2, y2))
        profile = (cq.Workplane(plane).rect(a, a))
        link = profile.sweep(path)
        links.append(link.val())

    links = cq.Compound.makeCompound(links)
    
    t_e = time.time()
    print(f'\rformed links, took: {((t_e-t_s) / 60):.2f} mins')
    #endregion

    #region form nodes
    t_s = time.time()
    print('forming nodes', end='')
    points = [pos[n] for n in mesh.nodes() if n in on_nodes]
    nodes = (
        cq.Workplane(mainPlane)
        .pushPoints(points)
        .circle(r_node)
        .extrude(-height)
    )

    nodes = cq.Compound.makeCompound(nodes)
    t_e = time.time()
    print(f'\rformed nodes, took: {((t_e-t_s)/60):.2f} mins')
    #endregion

    #region exporting STEP
    #making a block
    t_s = time.time()
    print('rendering object', end='')
    block = (cq.Workplane("XY").box(size*scale, size*scale, height,
                                    centered=(True, True, False)))
    porous = block.cut(nodes)
    porous = porous.cut(links)
    t_e = time.time()
    print(f'\rrendered object, took: {((t_e-t_s)/60):.2f} mins')

    label = 'c' if p == threshold else f'{p:.2f}'
    cq.exporters.export(porous, f"outputs/step/SD{seed}-p{label}-{size}n-{scale}x{height}.step")
    print('STEP file exported')
    #endregion

def equivalent_square(r):
    pi = np.pi
    j = 0.4217315309944166
    return 2*((3*pi)/(32*j))**(1/4)*r

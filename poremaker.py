import matplotlib.pyplot as plt
import numpy as np
import networkx as nx, cadquery as cq
from cadquery.vis import show
import newmanziff as nz
import time, tqdm


rt2 = np.sqrt(2)
#update these as needed
tension = 0.0579
t_c = 4.4167582

def makemesh(size, scale, p, seed=42, showGraph=False, exportGraph=True, theta=0):
    #region init vars
    LX = size
    LY = size // 2
    link_length = scale/rt2/1.64
    r_min = 0.17*link_length
    r_max = 0.32*link_length
    global r_node
    r_node = np.ceil(10*r_max)/10
    print(f"l: {link_length:.2f}mm, r_min: {r_min:.2f}mm,\nr_max: {r_max:.2f}, r_node: {r_node}mm")
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
                    if j >= 1: G.add_edge((i, j),(i+1,j-1), r=1, active=False)
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

    #assigning radii and weights
    #link_length = 2.6 #average actual link length
    for n in links: 
        r = np.random.uniform(r_min,r_max)
        n[2]['r'] = r
        n[2]['tau'] = (2*t_c*link_length)/(r) #link_length and r in mm -> units cancel
        n[2]['P_cap'] = 2*np.cos(theta)*tension / r
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
    if exportGraph or showGraph:
        t_s = time.time()
        print('rendering figure', end='')
        on_links = [(u,v) for u,v, d in G.edges(data=True) if d.get('active', True)]
        off_links = [(u,v) for u, v, d in G.edges(data=True) if not d.get('active', True)]
        plt.figure(figsize=(size+1,size+1))
        nx.draw_networkx_edges(G, pos, edgelist=off_links, alpha=0.1)
        nx.draw_networkx_edges(G, pos, edgelist=on_links, width=20*radii)
        nx.draw_networkx_nodes(G, pos, node_size=r_node*100)

        plt.axis('equal')
    if exportGraph: plt.savefig(f"outputs/figures/SD{seed}-p{round(p, 3) if p!=pc else 'c'}-{size}n.png", dpi=300, bbox_inches="tight")
    if exportGraph or showGraph: 
        t_e = time.time()
        print(f'\rfigure exported, took {(t_e - t_s)/60:.2f} mins')
    if showGraph: plt.show()
    if not (showGraph or exportGraph): plt.close('all')
    #endregion

    return G, pos, pc

def cry():
    print(f'---\t\t\t---')
    for n in range(4):
        print(f' i \t\t\t i ')

def buildmesh(mesh: nx.Graph, p, pos, height, size, scale, seed=42):
    #network = cq.Workplane("XY")
    length = scale/rt2
    tol = 1e-5
    #region form links

    v_se = cq.Vector(1, -1, 0).normalized()
    v_ne = cq.Vector(1, 1, 0).normalized()
    linked_se = []
    linked_ne = []
    on_nodes = set()

    t_s = time.time()
    print('forming links', end='')
    for u, v, d in mesh.edges(data=True):
        if not d.get('active', True): continue

        on_nodes.add(u)
        on_nodes.add(v)

        x1, y1 = pos[u]
        x2, y2 = pos[v]
        r = d['r']
        p1 = cq.Vector(x1, y1, 0)
        p2 = cq.Vector(x2, y2, 0) 
        direction = p2.sub(p1).normalized()

        if abs(direction.dot(v_se) - 1) < tol:
            linked_se.append(cq.Solid.makeCylinder(
                r, length, p1, v_se))
        elif abs(direction.dot(v_ne) - 1) < tol:
            linked_ne.append(cq.Solid.makeCylinder(
                r, length, p1, v_ne))

    all_solids = linked_se + linked_ne
    compound = cq.Compound.makeCompound(all_solids)
    network = cq.Workplane(obj=compound)
    t_e = time.time()
    print(f'\rformed links, took: {((t_e-t_s) / 60):.2f} mins')
    #endregion

    #region form nodes
    t_s = time.time()
    print('forming nodes', end='')
    points = [pos[n] for n in mesh.nodes() if n in on_nodes]
    nodes = (
        cq.Workplane("XY")
        .workplane(offset=(-height/2))
        .pushPoints(points)
        .circle(r_node)
        .extrude(height)
    )
    network = network.union(nodes)
    t_e = time.time()
    print(f'\rformed nodes, took: {((t_e-t_s)/60):.2f} mins')
    #endregion

    t_s = time.time()
    print('rendering object', end='')
    network = network.combine()
    block = (cq.Workplane("XY").box(size*scale, size*scale, height))
    porous = block.cut(network)
    t_e = time.time()
    print(f'\rrendered object, took: {((t_e-t_s)/60):.2f} mins')
    label = 'c' if p == threshold else f'{p:.2f}'
    cq.exporters.export(porous, f"outputs/step/SD{seed}-p{label}-{size}n-{scale}x{height}.step")
    print('STEP file exported')

def make_uniform(size, scale, p, seed=42, showGraph=False, exportGraph=False, theta=0):
    #region init vars
    LX = size
    LY = size // 2
    link_length = scale/rt2/1.64
    r = 0.245*link_length
    r_max = 0.32*link_length
    global r_node
    r_node = np.ceil(10*r_max)/10
    print(f"l: {link_length:.2f}mm, r: {r:.2f}mm, r_node: {r_node}mm")
    if p: np.random.seed(seed)
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
                    if j >= 1: G.add_edge((i, j),(i+1,j-1), r=r,active=False)
                    G.add_edge((i,j),(i+1, j),r=1, active=False)
            else:
                if j <= LY-1 and i < LX-1: 
                    if j< LY-1: G.add_edge((i, j), (i+1, j+1),r=r,active=False)
                    G.add_edge((i,j), (i+1, j),r=1,active=False)

    links = list(G.edges(data=True))
    radii = []
    key = []

    for n in links:
        n[2]['r'] = r
        n[2]['tau'] = (2*t_c*link_length)/(r)
        n[2]['P_cap'] = 2*np.cos(theta)*tension / r
        n[2]['key'] = np.random.uniform(0, 1)
        radii.append(r)

    pc,_ = nz.percolate(G, size)
    global threshold
    threshold = pc
    if p:
        links_sorted = sorted(links, key=lambda e: e[2]['key'])
        gate = links_sorted[int((1-p)*len(links))][2]['key'] #smallest to largest
        for n in links:
            if n[2]['key'] >= gate: n[2]['active'] = True
    else:
        for n in links: n[2]['active'] = True
    #endregion

    #region graph mesh
    if exportGraph or showGraph:
        t_s = time.time()
        print('rendering figure', end='')
        on_links = [(u,v) for u,v, d in G.edges(data=True) if d.get('active', True)]
        off_links = [(u,v) for u, v, d in G.edges(data=True) if not d.get('active', True)]
        plt.figure(figsize=(size+1,size+1))
        nx.draw_networkx_edges(G, pos, edgelist=off_links, alpha=0.1)
        nx.draw_networkx_edges(G, pos, edgelist=on_links, width=20*radii)
        nx.draw_networkx_nodes(G, pos, node_size=r_node)

        plt.axis('equal')
    if exportGraph: plt.savefig(f"outputs/figures/SD{seed}-p{round(p, 3) if p!=pc else 'c'}-{size}n.png", dpi=300, bbox_inches="tight")
    if exportGraph or showGraph: 
        t_e = time.time()
        print(f'\rfigure exported, took {(t_e - t_s)/60:.2f} mins')
    if showGraph: plt.show()
    if not (showGraph or exportGraph): plt.close('all')
    #endregion

    return G, pos, pc
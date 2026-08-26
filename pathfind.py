import networkx as nx
import matplotlib.pyplot as plt

def dijkstra(mesh: nx.Graph, param: str):
    size = max(n[0] for n in mesh.nodes) + 1

    inlet_nodes = [n for n in mesh.nodes if n[0] == 0]
    outlet_nodes = [n for n in mesh.nodes if n[0] == size -1]

    best_path = None
    best_cost = float('inf')

    for s in inlet_nodes:
        for t in outlet_nodes:
            try:
                cost = nx.dijkstra_path_length(mesh, s, t, weight=param)
                if cost < best_cost:
                    path = nx.dijkstra_path(mesh, s, t, weight=param)
                    best_cost = cost
                    best_path = path

            except nx.NetworkXNoPath:
                continue
    return best_path, best_cost

def show_min_path(mesh: nx.Graph, pos, path):

    size = max(n[0] for n in mesh.nodes) + 1
    inlet = [n for n in mesh.nodes if n[0] == 0]
    outlet = [n for n in mesh.nodes if n[0] == size-1]

    plt.figure(figsize=(size+1, size+1))
    nx.draw_networkx_edges(mesh, pos, edge_color='lightgray', width=1)
    nx.draw_networkx_nodes(mesh, pos, node_size=10, node_color='black')

    path_edges = list(zip(path[:-1], path[1:]))
    
    nx.draw_networkx_nodes(mesh, pos, nodelist=inlet, node_size=100, node_color='red')
    nx.draw_networkx_nodes(mesh, pos, nodelist=outlet, node_size=100, node_color='blue')
    nx.draw_networkx_edges(mesh, pos, edgelist=path_edges, width=5, edge_color='green')
    nx.draw_networkx_nodes(mesh, pos, nodelist=path, node_color='blue', node_size=20)

    plt.axis('equal')
    plt.show()


def save_min_path(mesh: nx.Graph, pos, path, p, pc, seed=42):
    
    size = max(n[0] for n in mesh.nodes) + 1
    inlet = [n for n in mesh.nodes if n[0] == 0]
    outlet = [n for n in mesh.nodes if n[0] == size-1]
    
    on_links = [(u,v) for u, v, d in mesh.edges(data=True) if d.get('active', True)]
    off_links = [(u,v) for u, v, d in mesh.edges(data=True) if d.get('active', False)]
    radii = [d['r'] for _, _, d in mesh.edges(data=True)]
    plt.figure(figsize=(size+1, size+1))
    nx.draw_networkx_edges(mesh, pos, edgelist=on_links, width=20*radii)
    nx.draw_networkx_edges(mesh, pos, edgelist=off_links, alpha=0.1)
    nx.draw_networkx_nodes(mesh, pos, node_size=10, node_color='black')

    path_edges = list(zip(path[:-1], path[1:]))
    
    nx.draw_networkx_nodes(mesh, pos, nodelist=inlet, node_size=100, node_color='red')
    nx.draw_networkx_nodes(mesh, pos, nodelist=outlet, node_size=100, node_color='blue')
    nx.draw_networkx_edges(mesh, pos, edgelist=path_edges, width=5, edge_color='green')
    nx.draw_networkx_nodes(mesh, pos, nodelist=path, node_color='blue', node_size=20)

    plt.axis('equal')
    plt.savefig(f"outputs/figures/SD{seed}-p{round(p,3) if p!=pc else 'c'}-{size}n-path.png", dpi=300, bbox_inches="tight")

def active_net(mesh):
    N = nx.Graph()
    N.add_nodes_from(mesh.nodes(data=True))

    for u, v, d in mesh.edges(data=True):
        if d['active']: N.add_edge(u,v, **d)
    return N

def twoP_pressure(mesh: nx.Graph): #mesh should be the active network
    p_cap = p_shear = 0

    size = max(n[0] for n in mesh.nodes) + 1
    inlet_nodes = [n for n in mesh.nodes if n[0] == 0]
    outlet_nodes = [n for n in mesh.nodes if n[0] == size -1]

    best = 10**10
    #region Dijkstra
    for s in inlet_nodes:
        for t in outlet_nodes:
            try:
                cost = nx.dijkstra_path_length(mesh, s, t, weight='tau')
                if cost < best: best = cost

            except nx.NetworkXNoPath:
                continue
    
    p_shear = best
    #endregion

    #region Kruskal
    G = mesh.copy()

    INLET = '__INLET__'
    OUTLET = '__OUTLET__'

    G.add_node(INLET)
    G.add_node(OUTLET)

    for n in inlet_nodes: G.add_edge(INLET, n, P_cap=0)
    for n in outlet_nodes: G.add_edge(OUTLET, n, p_cap=0)
    
    #MST
    mst = nx.minimum_spanning_tree(G, weight='P_cap', algorithm='kruskal')
    path = nx.shortest_path(mst, INLET, OUTLET)
    path = path[1:-1]
    #print(path)
    #for u, v in zip(path[:-1], path[1:]): print(G[u][v]['P_cap'])

    p_cap = max([G[u][v]['P_cap'] for u, v in zip(path[:-1], path[1:])])
    #endregion

    return p_cap, p_shear
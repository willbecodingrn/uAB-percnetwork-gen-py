import networkx as nx

def percolate(mesh: nx.Graph, meshSize):

    #region init objs
    parent = {}
    rank = {}
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    parent[LEFT] = LEFT
    parent[RIGHT] = RIGHT
    rank[LEFT] = 0
    rank[RIGHT] = 0
    #endregion
        
    #region init tools
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra = find(a)
        rb = find(b)

        if ra == rb: return
        elif rank[ra] > rank[rb]: parent[ra] = rb
        else: 
            parent[rb] = ra
            rank[ra] += 1
        #endregion
    
    LX = meshSize
    links = list(mesh.edges(data=True))
    sorted_links = sorted(links, key=lambda e: e[2]['r'])

    for n in mesh.nodes(): #init nodes
        parent[n] = n
        rank[n] = 0
    for n in mesh.nodes():
        i, j = n
        if i == 0: union(n, LEFT)
        if i == LX - 1: union(n, RIGHT)
    
    opened = 0
    pc = None

    for u, v, d in sorted_links:
        d['active'] = True
        opened += 1
        union(u,v)

        if u[0] == 0: union(u, LEFT)
        if v[0] == 0: union(u, RIGHT)
        if u[0] == LX - 1: union(u, RIGHT)
        if v[0] == LX - 1: union(v, RIGHT)

        if find(LEFT) == find(RIGHT):
            pc = opened / mesh.number_of_edges()
            break

    for _, _, d in mesh.edges(data=True):
        d['active'] = False
    
    return pc, sorted_links



import math

import networkx as nx


def rumor_centrality(tree: nx.Graph, root: int):
    t = {}
    p = {}
    r = {}
    visited = {}

    n = tree.size()

    def dfs_up(parent, v):
        children = [c for c in tree.neighbors(v) if c != parent]
        visited[v] = True

        if len(children) == 0:
            t[v] = 1
            p[v] = 1

        current_t = 1
        current_p = 1
        for child in children:
            if not visited.get(child, False):
                dfs_up(v, child)

            current_t += t[child]
            current_p *= p[child]

        t[v] = current_t
        p[v] = current_t * current_p

    def dfs_down(parent, v):
        children = [c for c in tree.neighbors(v) if c != parent]
        visited[v] = True

        for child in children:
            if not visited.get(child, False):
                r[child] = r[v] * t[child] / (n - t[child])
                dfs_down(v, child)

    dfs_up(None, root)

    r[root] = math.factorial(n - 1) / (p[root] / t[root])
    for vis in visited:
        visited[vis] = False

    dfs_down(None, root)

    # current_max_e = root
    # for v in adjs:
    #     if r[v] > r[current_max_e]:
    #         current_max_e = v
    #
    # return current_max_e, r[current_max_e]

    return r[root]


def find_rumor_center(g: nx.Graph) -> int:
    max_i = 0
    max_r = 0
    for v in g.nodes:
        T = nx.bfs_tree(g, v)
        r = rumor_centrality(T, v)

        if r > max_r:
            max_r = r
            max_i = v

    return max_i



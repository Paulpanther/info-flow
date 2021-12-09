import math
from typing import List

import networkx as nx

import graph_generator
import graph_simulations
from graph_visualization import plot_nx_graph


def rumor_centrality(tree: nx.Graph, root: int):
    t = {}
    p = {}
    r = {}
    visited = {}

    n = len(tree.nodes)

    if n <= 1:
        return 0

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


def rumor_values(g: nx.Graph) -> List[float]:
    return [rumor_centrality(nx.bfs_tree(g, v), v) for v in g.nodes]


if __name__ == '__main__':
    graph, init_nodes = graph_simulations.si(graph_generator.synthetic_internet(100), 10, 0.5, 1)
    print(graph.nodes)
    print(nx.is_tree(graph))
    print(init_nodes)
    rumor_v = rumor_values(graph)
    print(rumor_v)
    sizes = [50 if v in init_nodes else 20 for v in graph.nodes]
    plot_nx_graph(graph, rumor_v, rumor_v, sizes)

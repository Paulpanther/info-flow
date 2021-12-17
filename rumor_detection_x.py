import math
import time
from typing import List

import networkx as nx
import numpy as np
from tqdm import tqdm

import graph_generator
import graph_simulations
from graph_visualization import plot_nx_graph


def rumor_centrality(tree: nx.Graph, root: int, use_fact=False):
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

    if use_fact:
        r[root] = math.factorial(n - 1) / (p[root] / t[root])
    else:
        r[root] = t[root] / p[root]
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
    # for v in tqdm(g.nodes, desc="Rumor Centrality"):
    for v in g.nodes:
        T = nx.bfs_tree(g, v)
        r = rumor_centrality(T, v)

        if r > max_r:
            max_r = r
            max_i = v

    return max_i


def rumor_values(g: nx.Graph, use_fact=False) -> List[float]:
    return [rumor_centrality(nx.bfs_tree(g, v), v, use_fact) for v in tqdm(g.nodes, desc="Rumor Centrality per Node")]


def run(n, generator):
    durations = {}
    successes = {}
    for i in range(0, n):
        graph, init_nodes = graph_simulations.si(generator(i), 100, 0.5, 1)
        time_start = time.time()

        rumor_v = find_rumor_center(graph)

        duration = time.time() - time_start
        success = rumor_v == init_nodes[0]
        nodes = len(graph.nodes)

        if nodes not in durations:
            durations[nodes] = []
        durations[nodes].append(duration)

        if nodes not in successes:
            successes[nodes] = []
        successes[nodes].append(success)
    return durations, successes


if __name__ == '__main__':
    g = nx.Graph()
    g.add_node(0)  # A
    g.add_node(1)  # B
    g.add_node(2)  # F
    g.add_node(3)  # G
    g.add_node(4)  # H
    g.add_node(5)  # J
    g.add_edge(0, 1)
    g.add_edge(0, 3)
    g.add_edge(0, 4)
    g.add_edge(0, 2)
    g.add_edge(1, 4)
    g.add_edge(1, 4)
    # print("Scale free")
    # n = 10
    # durations, successes = run(n, lambda i: graph_generator.scale_free(i))
    # import plotly.express as px
    # fig = px.scatter(x=list(range(0, n)), y=lambda i: sum(durations[i]))
    # fig.show()



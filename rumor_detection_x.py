"""Rumor Centrality Score - Implemented with networkx"""

import math
import time
from typing import List
import networkx as nx
from tqdm import tqdm
import matplotlib.pyplot as plt

import graph_generator
import graph_simulations


def rumor_centrality(graph: nx.Graph, root: int, use_fact=False):
    """Calculates the rumor centrality for root on the graph given by adj_list"""
    t = {}
    p = {}
    r = {}
    visited = {}

    tree = nx.bfs_tree(graph, root)
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

    return r[root]


def find_rumor_center(g: nx.Graph) -> int:
    """Finds the node with the max. rumor centrality"""
    max_i = 0
    max_r = 0
    for v in tqdm(g.nodes, desc="Rumor Centrality"):
        r = rumor_centrality(g, v)

        if r > max_r:
            max_r = r
            max_i = v

    return max_i


def rumor_values(g: nx.Graph, use_fact=False) -> List[float]:
    """Finds the rumor centrality for all nodes"""
    return [rumor_centrality(nx.bfs_tree(g, v), v, use_fact) for v in tqdm(g.nodes, desc="Rumor Centrality per Node")]


def test_against_si(n, generator):
    """Runs n tests of rumor centrality against the si model and measures runtime and success"""
    durations = {}
    successes = {}
    for node_count in range(0, n):
        graph, init_nodes = graph_simulations.si(generator(node_count), 100, 0.5, 1)
        time_start = time.time()

        rumor_v = find_rumor_center(graph)

        duration = time.time() - time_start
        success = rumor_v == init_nodes[0]

        durations[node_count] = duration
        successes[node_count] = success

    return durations, successes


def main():
    print("Scale free")
    n = 10
    durations, successes = test_against_si(n, lambda i: graph_generator.scale_free(i))
    print(len(list(range(0, n))))
    print(len(durations))
    plt.scatter(x=list(range(0, n)), y=durations.keys())
    plt.savefig("temp.png")


if __name__ == '__main__':
    main()

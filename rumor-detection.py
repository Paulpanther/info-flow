"""Rumor Centrality Score - Implemented from scratch"""
from typing import Dict, List

import networkx
import math
from collections import deque

from graph_visualization import plot_nx_graph, compute_node_degrees
from graph_generator import scale_free


def networkx_graph_to_adj_list(g: networkx.Graph) -> Dict[int, List[int]]:
    """Transforms a networkx graph to an adj list dict node -> node list"""
    adj_list = {}
    for line in networkx.generate_adjlist(g):
        node, *edges = line.split(" ")
        adj_list[node] = edges
    return adj_list


def get_bfs_tree(adj_list, root) -> Dict[int, List[int]]:
    """Build a bfs tree from root"""
    queue = deque([root])
    visited = {root: True}
    T = {}

    while len(queue) > 0:
        v = queue.pop()
        children = adj_list[v]
        T[v] = []

        for child in children:
            if not visited.get(child, False):
                T[v].append(child)
                queue.appendleft(child)
                visited[child] = True
    return T


def rumor_centrality(adj_list, root):
    """Calculates the rumor centrality for root on the graph given by adj_list"""
    t = {}
    p = {}
    r = {}
    visited = {}

    bfs_tree_adj_list = get_bfs_tree(adj_list, root)

    n = len(bfs_tree_adj_list)

    def dfs_up(v):
        children = bfs_tree_adj_list[v]
        visited[v] = True

        if len(children) == 0:
            t[v] = 1
            p[v] = 1

        current_t = 1
        current_p = 1
        for child in children:
            if not visited.get(child, False):
                dfs_up(child)

            current_t += t[child]
            current_p *= p[child]

        t[v] = current_t
        p[v] = current_t * current_p

    def dfs_down(v):
        children = bfs_tree_adj_list[v]
        visited[v] = True

        for child in children:
            if not visited.get(child, False):
                r[child] = r[v] * t[child] / (n - t[child])
                dfs_down(child)

    dfs_up(root)

    r[root] = math.factorial(n - 1) / (p[root] / t[root])
    for vis in visited:
        visited[vis] = False

    dfs_down(root)

    return r[root]


def main():

    nx_g = scale_free(100)

    n_markers, n_text = compute_node_degrees(nx_g)
    plot_nx_graph(nx_g, n_markers, n_text)

    adj_list = networkx_graph_to_adj_list(nx_g)

    # We could save a lot of lines here by using a map and a max
    # at the additional cost of O(n)
    rs = []
    labels = []

    max_i = 0
    max_r = 0
    for v in adj_list:
        r = rumor_centrality(adj_list, v)

        rs.append(r)
        labels.append(f"rumor centrality score for {v}: {r}")

        if r > max_r:
            max_r = r
            max_i = v

    print(max_i, max_r)
    plot_nx_graph(nx_g, rs, labels)


if __name__ == '__main__':
    main()

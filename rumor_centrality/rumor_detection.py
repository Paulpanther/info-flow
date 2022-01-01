"""Rumor Centrality Score - Implemented from scratch"""
from typing import Dict, List, Tuple

import networkx
import math
from collections import deque


def networkx_graph_to_adj_list(g: networkx.Graph) -> Dict[int, List[int]]:
    """Transforms a networkx graph to an adj list dict node -> node list"""
    adj_list = {}
    for line in networkx.generate_adjlist(g):
        node, *edges = line.split(" ")
        adj_list[int(node)] = list(map(int, edges))
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


def rumor_centrality(adj_list, root, use_fact=False):
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

    if use_fact:
        r[root] = math.factorial(n - 1) / (p[root] / t[root])
    else:
        r[root] = t[root] / p[root]
    for vis in visited:
        visited[vis] = False

    dfs_down(root)

    return r[root]


def get_rumor_centrality_lookup(adj_list, use_fact=False) -> Dict[int, float]:
    """Returns each node of the adj list with its respective rumor centrality in a dict"""
    return dict(map(lambda v: (v, rumor_centrality(adj_list, v, use_fact)), list(adj_list.keys())))


def get_center_prediction(adj_list, use_fact=False):
    """Returns the node with the maximum rumor centrality of all nodes"""
    return max(
        get_rumor_centrality_lookup(adj_list, use_fact).items(),
        key=lambda x: x[1],
    )[0]

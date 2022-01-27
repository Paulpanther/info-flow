"""Rumor Centrality Score - Implemented from scratch"""
from typing import Dict, List, Tuple

import networkx
import math
from collections import deque
from multiprocessing import Pool, Manager
from decimal import Decimal


def networkx_graph_to_adj_list(g: networkx.Graph) -> Dict[int, List[int]]:
    """Transforms a networkx graph to an adj list dict node -> node list"""

    # generate_adjlist does not include previous mentioned edges, so a graph 0-1 is noted as
    # 0 1
    # 1
    # The back-edge 1->0 is missing. Therefore we need to add those manually
    adj_list = {}
    for source, neighbors in g.adjacency():
        adj_list[source] = adj_list.get(source, set()).union(set(neighbors))
        for target in neighbors:
            adj_list[target] = adj_list.get(target, set()).union({source})

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
        r[root] = Decimal(math.factorial(n - 1)) / (Decimal(p[root]) / Decimal(t[root]))
    else:
        r[root] = t[root] / p[root]
    for vis in visited:
        visited[vis] = False

    # We do not use the results of this calculation
    # It is described in the paper, but I dont see its use?
    dfs_down(root)

    return r[root]


def parallel_multiprocessing_wrapper(adj_list, root, use_fact):
    return root, rumor_centrality(adj_list, root, use_fact)


def get_rumor_centrality_lookup(adj_list, use_fact=False, threads=1) -> Dict[int, float]:
    """Returns each node of the adj list with its respective rumor centrality in a dict"""
    if threads < 1:
        raise ValueError("At least one thread is needed to run!")

    if threads > 1:
        m = Manager()
        adj_proxy = m.dict(adj_list)
        args = [(adj_proxy, v, use_fact) for v in adj_list.keys()]
        with Pool(threads) as p:
            rumor_centrality_lookup = p.starmap(parallel_multiprocessing_wrapper, args)

        return dict(rumor_centrality_lookup)

    return dict(map(lambda v: (v, rumor_centrality(adj_list, v, use_fact)), list(adj_list.keys())))


def get_center_prediction(adj_list, use_fact=False, threads=1):
    """Returns the nodes with the maximum rumor centrality of all nodes"""
    lookup = get_rumor_centrality_lookup(adj_list, use_fact, threads)
    max_rumor_centrality = max(lookup.values())
    return [node for node, score in lookup.items() if score == max_rumor_centrality]


def test():
    # Build graph from talk example
    g = networkx.Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("F")
    g.add_node("G")
    g.add_node("H")
    g.add_node("J")

    g.add_edge("A", "B")
    g.add_edge("A", "F")
    g.add_edge("A", "G")
    g.add_edge("A", "H")

    g.add_edge("B", "H")
    g.add_edge("B", "J")

    g.add_edge("G", "H")

    # All nodes are numbers again
    mapping = {"A": 1, "B": 2, "F": 3, "G": 4, "H": 5, "J": 6}
    reversed_mapping = dict([(number, letter) for letter, number in mapping.items()])

    g = networkx.relabel_nodes(g, mapping)

    adj_list = networkx_graph_to_adj_list(g)
    get_rumor_centrality_lookup(adj_list)
    get_rumor_centrality_lookup(adj_list, True)


if __name__ == "__main__":
    test()

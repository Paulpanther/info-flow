import math
import random
from collections import deque

from graph_visualization import convert_to_nx_graph, plot_nx_graph, compute_node_degrees


def make_graph(n):
    return {i: random.sample(list(range(n)), random.randint(0, n)) for i in range(n)}


def bfs(adjs, root):
    queue = deque([root])
    visited = {root: True}
    T = {}

    while len(queue) > 0:
        v = queue.pop()
        children = adjs[v]
        T[v] = []

        for child in children:
            if not visited.get(child, False):
                T[v].append(child)
                queue.appendleft(child)
                visited[child] = True
    return T


def rumor_centrality(adjs, root):
    t = {}
    p = {}
    r = {}
    visited = {}

    n = len(adjs)

    def dfs_up(v):
        children = adjs[v]
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
        children = adjs[v]
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

    # current_max_e = root
    # for v in adjs:
    #     if r[v] > r[current_max_e]:
    #         current_max_e = v
    #
    # return current_max_e, r[current_max_e]

    return r[root]


if __name__ == '__main__':
    g = make_graph(100)

    nx_g = convert_to_nx_graph(g)
    n_markers, n_text = compute_node_degrees(nx_g)
    plot_nx_graph(nx_g, n_markers, n_text)

    rs = []
    labels = []

    max_i = 0
    max_r = 0
    for v in g:
        T = bfs(g, v)
        r = rumor_centrality(T, v)

        rs.append(r)
        labels.append(f"rumor centrality score for {v}: {r}")

        if r > max_r:
            max_r = r
            max_i = v

    print(max_i, max_r)
    plot_nx_graph(nx_g, rs, labels)




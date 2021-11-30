import math


def make_graph(n):
    pass


if __name__ == '__main__':

    t = {}
    p = {}
    r = {}
    adjs = {
        0: [1],
        1: [2],
        2: [],
    }
    visited = {}

    root = 0
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

    current_max_e = root
    for v in adjs:
        if r[v] > r[current_max_e]:
            current_max_e = v

    print(current_max_e, r[current_max_e])

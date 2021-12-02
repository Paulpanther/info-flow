import networkx
from networkx.generators.random_graphs import dense_gnm_random_graph
from networkx.algorithms.distance_measures import center
from networkx.algorithms.centrality import betweenness_centrality, closeness_centrality

from graph_visualization import plot_nx_graph


def random_graph(n, m, seed=None) -> networkx.Graph:
    return dense_gnm_random_graph(n, m, seed)


def centers_by_jordan_center(g):
    return center(g)


def centers_by_betweenness_centrality(g):
    b_c_dict = betweenness_centrality(g)
    top = sorted(b_c_dict.items(), key=lambda x: x[1], reverse=True)[0]
    return top


def centers_by_distance_centrality(g):
    d_c_dict = closeness_centrality(g)
    top = sorted(d_c_dict.items(), key=lambda x: x[1], reverse=True)[0]
    return top


def main():
    nodes = 200
    edges = 300
    g = random_graph(nodes, edges)

    plot_nx_graph(g)

    print("centers_by_jordan_center")
    print(centers_by_jordan_center(g))
    print("centers_by_betweenness_centrality")
    print(centers_by_betweenness_centrality(g))
    print("centers_by_distance_centrality")
    print(centers_by_distance_centrality(g))


if __name__ == "__main__":
    main()

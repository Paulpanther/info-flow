import random
from collections import defaultdict
from typing import List, Dict, Tuple, Iterator

import networkx as nx
from networkx.algorithms import single_source_shortest_path_length
from networkx.algorithms.distance_measures import diameter
from networkx.algorithms.distance_measures import periphery

from rumor_centrality.graph_visualization import plot_nx_graph
from rumor_centrality.rumor_detection import get_center_prediction
from rumor_centrality.rumor_detection import networkx_graph_to_adj_list


def get_cluster_reprs(g: nx.Graph, number_clusters: int) -> List[int]:
    # select nodes that are the farthest away from each other (and are infected)
    peripheral_nodes = periphery(g)
    cluster_reprs = random.sample(peripheral_nodes, k=2)

    dist_x = single_source_shortest_path_length(g, cluster_reprs[0])
    dist_y = single_source_shortest_path_length(g, cluster_reprs[1])
    summed_dists = {k: dist_x.get(k, 0) + dist_y.get(k, 0) for k in (set(dist_x) & set(dist_y) - set(cluster_reprs))}
    for k in range(2, number_clusters):
        # select node which is farthest away from currently selected nodes
        # sum distances from each node from set?
        max_node = sorted(summed_dists.items(), key=lambda x: x[1], reverse=True)[0]
        print(f"got node {max_node[0]} with dist {max_node[1]} to cluster centers")
        cluster_reprs.append(max_node[0])
        dist_new = single_source_shortest_path_length(g, cluster_reprs[1])
        summed_dists = {k: dist_x.get(k, 0) + dist_y.get(k, 0) for k in
                        (set(summed_dists) & set(dist_new) - set(cluster_reprs))}

    return cluster_reprs


# TODO: make all clusters grow equally from each seed

def assign_all_nodes_cluster(g: nx.Graph, cluster_reprs: List[int]) -> Dict[int, int]:
    dists = [single_source_shortest_path_length(g, cluster_repr) for cluster_repr in cluster_reprs]
    cluster_assign = {}

    for node in g:
        min_dist_cluster = 0
        nodes = list(range(len(cluster_reprs)))
        random.shuffle(nodes)
        for idx in nodes:
            if dists[idx][node] < dists[min_dist_cluster][node]:
                min_dist_cluster = idx

        cluster_assign[node] = min_dist_cluster

    return cluster_assign


def cluster_graph(g: nx.Graph, number_clusters: int) -> List[int]:
    reprs = get_cluster_reprs(g, number_clusters)
    assignm = assign_all_nodes_cluster(g, reprs)
    return list(assignm.values())


def get_induced_subgraph(adj_list: Dict[int, List[int]], subgraph_assignments: List[int]) -> List[Dict[int, List[int]]]:
    return [
        {
            cur_node: [next_node for next_node in adj_list[cur_node] if subgraph_assignments[next_node] == i]
            for cur_node in adj_list if subgraph_assignments[cur_node] == i
        } for i in set(subgraph_assignments)
    ]


def get_node_indices_by_value(subgraph_assignments: List[int]) -> List[List[int]]:
    clusters = defaultdict(list)
    for i, cluster_num in enumerate(subgraph_assignments):
        clusters[cluster_num].append(i)

    return clusters


def get_max_infection_radius(gs: Iterator[nx.Graph]) -> int:
    # for g in gs:
    #     print(f"g : {diameter(g)}")
    # print(list(map(diameter, gs)))
    return max(map(lambda x: diameter(nx.Graph(x)), gs))


def build_cluster(g: nx.Graph, number_clusters: int) -> Tuple[int, List[List[int]], List[int]]:
    assignm = cluster_graph(g, number_clusters)
    adj_list = networkx_graph_to_adj_list(g)
    subgraphs = get_induced_subgraph(adj_list, assignm)
    # subgraph_nodes = get_node_indices_by_value(assignm)
    # print(subgraph_nodes)
    # subgraphs = map(g.subgraph, list(subgraph_nodes.values()))
    # print(list(subgraphs))
    max_infection_radius = get_max_infection_radius(list(subgraphs))

    return max_infection_radius, subgraphs, assignm


def multiple_rumor_source_prediction(g: nx.Graph, max_num_clusters: int = 20,
                                     estimate_num_cluster: bool = False) -> Tuple[List[int], List[int]]:
    if estimate_num_cluster:
        # argmax wk - wk+1 - (wk+1 - wk+2)
        clusters_dists = [build_cluster(g, k) for k in range(max_num_clusters)]
        computed_diffs = [
            (clusters_dists[k][0] - clusters_dists[k + 1][0] - (clusters_dists[k + 1][0] - clusters_dists[k + 2][0]), k)
            for
            k in range(len(clusters_dists) - 3)]
        best_cluster = max(computed_diffs, key=lambda x: x[0])
        subgraphs = clusters_dists[best_cluster[1]][1]
        # print(list(clusters_dists[best_cluster[1]][1]))
        subgraphs_rumor_centers = list(map(lambda x: get_center_prediction(x), subgraphs))

        return subgraphs_rumor_centers, clusters_dists[best_cluster[1]][2]
    else:
        max_infection_radius, subgraphs, assignm = build_cluster(g, max_num_clusters)
        subgraphs_rumor_centers = list(map(lambda x: get_center_prediction(x), subgraphs))

        return subgraphs_rumor_centers, assignm


def visualise_cluster_graph(g: nx.Graph, rumor_centers: List[List[int]], assignment: List[int],
                            layout=nx.spring_layout) -> None:
    max_assignment = max(assignment) + 1
    labels: List[int] = assignment.copy()
    for i, r_cs in enumerate(rumor_centers):
        for r_c in r_cs:
            labels[r_c] = f"{labels[r_c]} (rumour center)"
            assignment[r_c] = i + max_assignment

    plot_nx_graph(g, assignment, labels, layout=layout)

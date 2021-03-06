import random
from collections import defaultdict
from typing import List, Dict, Tuple, Iterator, Any

import networkx as nx
from networkx.algorithms import single_source_shortest_path_length
from networkx.algorithms.distance_measures import periphery, diameter

from rumor_centrality.graph_visualization import plot_nx_graph
from rumor_centrality.rumor_detection import get_center_prediction
from rumor_centrality.rumor_detection import get_edge_list_from_adj_list
from rumor_centrality.rumor_detection import networkx_graph_to_adj_list


def get_induced_subgraph(adj_list: Dict[int, List[int]], subgraph_assignments: Dict[int, int]) -> List[
    Dict[int, List[int]]]:
    subgraphs = []

    for i in set(subgraph_assignments.values()):
        current_subgraph = {}
        for cur_node in adj_list:
            current_subgraph[cur_node] = []
            if subgraph_assignments[cur_node] != i:
                continue

            for next_node in adj_list[cur_node]:
                if subgraph_assignments[next_node] != i:
                    continue
                current_subgraph[cur_node].append(next_node)

        subgraphs.append(current_subgraph)

    return subgraphs


def get_node_indices_by_value(subgraph_assignments: Dict[int, int]) -> defaultdict[Any, list]:
    clusters = defaultdict(list)
    for node, cluster_num in subgraph_assignments.items():
        clusters[cluster_num].append(node)

    return clusters


def get_biggest_connected_component_subgraph_from_adj_list(adj_list: dict[int, list[int]]) -> nx.Graph:
    G = nx.Graph(get_edge_list_from_adj_list(adj_list))
    for node in adj_list:
        G.add_node(node)
    return G.subgraph(max(nx.connected_components(G), key=len))


def get_max_infection_radius(gs: Iterator[Dict[int, List[int]]]) -> int:
    try:
        connected_nx_graphs = list(map(get_biggest_connected_component_subgraph_from_adj_list, gs))
        return max(map(lambda x: diameter(x), connected_nx_graphs))
    except Exception:
        print("A Problem occured when finding max, returning 5")
        return 5


def get_cluster_reprs(g: nx.Graph, number_clusters: int) -> List[int]:
    # select nodes that are the farthest away from each other (and are infected)
    peripheral_nodes = periphery(g)
    cluster_reprs = random.sample(peripheral_nodes, k=2)

    dist_x = single_source_shortest_path_length(g, cluster_reprs[0])
    dist_y = single_source_shortest_path_length(g, cluster_reprs[1])
    summed_dists = {k: dist_x.get(k, 0) + dist_y.get(k, 0) for k in (set(dist_x) & set(dist_y) - set(cluster_reprs))}
    for k in range(2, number_clusters):
        # select node which is farthest away from currently selected nodes
        # sum distances from each node from set
        max_node = sorted(summed_dists.items(), key=lambda x: x[1], reverse=True)[0]
        cluster_reprs.append(max_node[0])
        dist_new = single_source_shortest_path_length(g, cluster_reprs[1])
        summed_dists = {k: dist_x.get(k, 0) + dist_y.get(k, 0) for k in
                        (set(summed_dists) & set(dist_new) - set(cluster_reprs))}

    return cluster_reprs


def assign_all_nodes_cluster(g: nx.Graph, cluster_reprs: List[int]) -> Dict[int, int]:
    """Given a graph g and a list of vertices that are the cluster representatives,
    assigns all nodes in g to a cluster and returns those assignments as a dict"""

    dists = {cluster_repr: single_source_shortest_path_length(g, cluster_repr) for cluster_repr in cluster_reprs}
    packed_cluster_labels = {cluster_label: i for i, cluster_label in enumerate(set(cluster_reprs))}
    cluster_assign = {}

    for node in g:
        min_dist_cluster = None
        nodes = cluster_reprs.copy()
        random.shuffle(nodes)
        for idx in nodes:
            if min_dist_cluster is None or dists[idx][node] < dists[min_dist_cluster][node]:
                min_dist_cluster = idx

        cluster_assign[node] = packed_cluster_labels[min_dist_cluster]

    return cluster_assign


def cluster_graph(g: nx.Graph, number_clusters: int) -> Dict[int, int]:
    reprs = get_cluster_reprs(g, number_clusters)
    assignm = assign_all_nodes_cluster(g, reprs)
    return assignm


def build_cluster(g: nx.Graph, number_clusters: int) -> tuple[int, list[dict[int, list[int]]], dict[int, int]]:
    assignm = cluster_graph(g, number_clusters)
    adj_list = networkx_graph_to_adj_list(g)
    subgraphs = get_induced_subgraph(adj_list, assignm)
    max_infection_radius = get_max_infection_radius(list(subgraphs))

    return max_infection_radius, subgraphs, assignm


def multiple_rumor_source_prediction(g: nx.Graph, max_num_clusters: int = 20,
                                     estimate_num_cluster: bool = False) -> Tuple[List[List[int]], Dict[int, int]]:
    """Main method for multiple center prediction, uses always rumor centrality"""
    if estimate_num_cluster:
        # argmax wk - wk+1 - (wk+1 - wk+2)
        clusters_dists = [build_cluster(g, k) for k in range(max_num_clusters)]
        computed_diffs = [
            (clusters_dists[k][0] - clusters_dists[k + 1][0] - (clusters_dists[k + 1][0] - clusters_dists[k + 2][0]), k)
            for
            k in range(len(clusters_dists) - 3)]
        best_cluster = max(computed_diffs, key=lambda x: x[0])
        subgraphs = clusters_dists[best_cluster[1]][1]
        subgraphs_rumor_centers = list(map(lambda x: get_center_prediction(x), subgraphs))

        return subgraphs_rumor_centers, clusters_dists[best_cluster[1]][2]
    else:
        max_infection_radius, subgraphs, assignm = build_cluster(g, max_num_clusters)
        subgraphs_rumor_centers = list(map(lambda x: get_center_prediction(x), subgraphs))

        return subgraphs_rumor_centers, assignm


def multiple_rumor_source_prediction_metric(
        g: nx.Graph,
        max_num_clusters: int = 20,
        center_prediction_callback=get_center_prediction,
        callback_runs_on_nxgraph=False,
) -> Tuple[List[List[int]], Dict[int, int]]:
    """Main method for multiple center prediction,
    takes a cluster center prediction method as `center_prediction_callback`"""

    if max_num_clusters == 1:
        subgraphs, assignm = [networkx_graph_to_adj_list(g)], None
    else:
        max_infection_radius, subgraphs, assignm = build_cluster(g, max_num_clusters)

    if callback_runs_on_nxgraph:
        subgraphs_rumor_centers = list(map(lambda x: center_prediction_callback(
            get_biggest_connected_component_subgraph_from_adj_list(x)
        ), subgraphs))
    else:
        subgraphs_rumor_centers = list(map(lambda x: center_prediction_callback(x), subgraphs))

    return subgraphs_rumor_centers, assignm


def visualise_cluster_graph(g: nx.Graph, rumor_centers: List[List[int]], assignment: Dict[int, int],
                            layout=nx.spring_layout) -> None:
    max_assignment = max(assignment.values()) + 1
    labels: Dict = assignment.copy()
    for i, r_cs in enumerate(rumor_centers):
        for r_c in r_cs:
            labels[r_c] = f"{labels[r_c]} (rumour center)"
            assignment[r_c] = i + max_assignment

    plot_nx_graph(g, list(assignment.values()), list(labels.values()), layout=layout)

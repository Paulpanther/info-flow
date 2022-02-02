from typing import List

from networkx import diameter, is_connected

from rumor_centrality.evaluation import hop_distances
from rumor_centrality.graph_clustering import multiple_rumor_source_prediction
from rumor_centrality.graph_simulations import si


def flatten_list(l: List[List[int]]) -> List[int]:
    return [sl[0] for sl in l]


def multiple_sources_experiment(num_infection_centers, infection_prob, node_count, max_infected_nodes, graph_callback):
    while True:
        exp_graph = graph_callback(node_count)
        exp_graph_simulated, infection_sources = si(exp_graph.copy(), iterations=-1,
                                                    infections_centers=num_infection_centers,
                                                    max_infected_nodes=max_infected_nodes,
                                                    infection_prob=infection_prob)
        if is_connected(exp_graph_simulated):
            break

    exp_diameter = diameter(exp_graph_simulated)
    subgraphs_rumor_centers, assignm = multiple_rumor_source_prediction(exp_graph_simulated, num_infection_centers)

    hops = hop_distances(exp_graph, flatten_list(subgraphs_rumor_centers), infection_sources)

    return {
        "hops": hops,
        "graph_normalized_hops": list(map(lambda x: x / exp_diameter, hops)),
        "diameter": exp_diameter,
        "num_infection_centers": num_infection_centers,
        "infection_prob": infection_prob,
        "node_count": node_count,
        "max_infected_nodes": max_infected_nodes,
    }

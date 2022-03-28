import pickle
import sys
from functools import partial
from itertools import product
from multiprocessing import Pool, TimeoutError
from os import makedirs
from os.path import join
from pathlib import Path

from tqdm import tqdm

import rumor_centrality.jordan_center_alternative as jo
from rumor_centrality.experiment import multiple_sources_experiment_metric
from rumor_centrality.graph_generator import synthetic_internet, scale_free, us_power_grid, internet
from rumor_centrality.rumor_detection import get_center_prediction

experiment_params = {
    "max_infected_nodes": [500, 1000],
    # "node_count": 3000,
    "infection_prob": 0.3,
    "num_infection_centers": [2, 3, 5, 7, 10],
    "exp_iterations": 100,
}

# Available Graphs
# Making graphs bigger, so that infections make sense on it
graph_types = {
    # "synthetic_internet_100": lambda: synthetic_internet(1000),
    "synthetic_internet_10000": partial(synthetic_internet, 10000),
    # "scale_free_100": lambda: nx.Graph(scale_free(1000)),
    "scale_free_10000": partial(scale_free, 10000),
    "us_power_grid": us_power_grid,
    "internet": internet,
}

metrics = {
    "rumor_centrality": get_center_prediction,
    "jordan_centrality": jo.centers_by_jordan_center,
    "betweenness_centrality": jo.centers_by_betweenness_centrality,
    "distance_centrality": jo.centers_by_distance_centrality,
}


def unpack_result(result):
    try:
        return_value = result.get(timeout=250)
    except TimeoutError:
        return_value = None

    return return_value


if __name__ == "__main__":
    _, cluster_numbers, output_dir = sys.argv

    try:
        cluster_numbers = sorted(list(map(int, cluster_numbers.split(","))))
    except ValueError:
        exit("INVALID CLUSTER NUMBERS")

    output_dir = join(output_dir, "centers")
    makedirs(output_dir, exist_ok=True)

    result_mult_metrics = []

    num_infection_centers = cluster_numbers or experiment_params["num_infection_centers"]
    max_infected_nodes = experiment_params["max_infected_nodes"]
    infection_prob = experiment_params["infection_prob"]
    exp_iterations = experiment_params["exp_iterations"]

    for num_infection_center, max_inf_nodes, graph_name, metric_name in tqdm(
            list(product(num_infection_centers, max_infected_nodes, graph_types, metrics))):
        graph = graph_types[graph_name]
        metric = metrics[metric_name]

        with Pool(processes=10) as pool:
            multiple_results = [pool.apply_async(multiple_sources_experiment_metric, (
                num_infection_center,
                infection_prob,
                max_inf_nodes,
                graph,
                graph_name,
                metric,
                metric_name,
                metric_name != "rumor_centrality",
            )) for i in range(exp_iterations)]
            result_mult_metrics.extend([unpack_result(res) for res in multiple_results])

    with Path(join(output_dir, f"multiple_centers_all_graphs_centers_{cluster_numbers}.pickle")).open("wb") as f:
        pickle.dump(result_mult_metrics, f)

#!/usr/bin/env python
# coding: utf-8

# # Missing on real World
# This notebooks tests the relevance of nodes for the two real world datasets Powergrid and Internet. We randomly remove a certain percent of nodes.
# 
# Then we predict the infection center again (without simulation at first) and measure the removals impact.

# In[1]:


import networkx as nx
import rumor_centrality.rumor_detection as raw
import rumor_centrality.jordan_center_alternative as jo
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from rumor_centrality.graph_generator import internet, us_power_grid, scale_free, synthetic_internet
from time import time
from multiprocessing import Pool
from typing import List, Tuple, Dict
from rumor_centrality import graph_simulations
from rumor_centrality.graph_visualization import plot_nx_graph
import random
import pickle
from os.path import join
from multiprocessing import Pool
import sys
from os import makedirs

# Available Graphs
graph_types = {
    "synthetic_internet_100": lambda: synthetic_internet(100),
    "synthetic_internet_1000": lambda: synthetic_internet(1000),
    "scale_free_100": lambda: nx.Graph(scale_free(100)),
    "scale_free_1000": lambda: nx.Graph(scale_free(1000)),
    "us_power_grid": us_power_grid,
    "internet": internet,
}


infected_nodes_percent = 0.3
sim_si = lambda g: graph_simulations.si(g, -1, 0.3, 1, int(len(g.nodes) * infected_nodes_percent), 10, True)
sim_sis = lambda g: graph_simulations.sis(g, -1, 0.3, 0.1, 1, int(len(g.nodes) * infected_nodes_percent), 10, True)
sim_sir = lambda g: graph_simulations.sir(g, -1, 0.3, 0.1, 1, int(len(g.nodes) * infected_nodes_percent), 10, True)

simulations = {
    "si": sim_si,
    "sis": sim_sis,
    "sir": sim_sir,
}

# Choose Graph
_, graph_name, output_dir, simulation = sys.argv
if graph_name not in graph_types.keys():
    exit("INVALID GRAPH NAME!")

if simulation not in simulations.keys():
    exit("INVALID SIMULATION NAME")

output_dir = join(output_dir, simulation, graph_name)
makedirs(output_dir, exist_ok=True)

# Available Metrics
metrics = {
    "rumor_centrality" : lambda g: raw.get_center_prediction(
        raw.networkx_graph_to_adj_list(g), use_fact=False
    ),
    "jordan_centrality": jo.centers_by_jordan_center,
    "betweenness_centrality": jo.centers_by_betweenness_centrality,
    "distance_centrality": jo.centers_by_distance_centrality,
}

# Setup Experiment Parameters
graph_callback = graph_types[graph_name]
sample_size = 100

percent_radius = [0.0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]  # Percent of nodes to remove


graph_size = len(graph_callback().nodes)

def name_builder(name, pickle=True):
    postfix = ""
    if pickle:
        postfix = ".pickle"
    return f"{name}__config_graph_{graph_name}_nodes_{graph_size}_samples_{sample_size}_{postfix}"

main_ref_graph = graph_callback().copy(as_view=True)


# In[7]:


if output_dir is not None:
    with open(join(output_dir, name_builder("main_ref_graph")), "wb") as f:
        pickle.dump(main_ref_graph, f)


# In[8]:


def get_hop_distance(g, center, predicted_center):
    return nx.shortest_path_length(g, center, predicted_center)


# In[9]:


def remove_node_and_reconnect(g, node):
    neighbors = list(g.neighbors(node))
    for i in neighbors:
        for j in neighbors:
            if i != j:
                # Duplicated edges naturally not possible on a graph
                g.add_edge(i, j)
    g.remove_node(node)


# In[10]:


import_graph = None
def get_experiment_graph(g, percent_missing):
    g = g.copy(as_view=True)
    nodes_to_remove = int(len(g.nodes) * percent_missing)

    _g = g.copy()
    removed_nodes = []
    for _ in range(nodes_to_remove):
        node_to_remove = random.choice(list(_g.nodes))
        remove_node_and_reconnect(_g, node_to_remove)
        removed_nodes.append(node_to_remove)
    return _g, removed_nodes


def simulate_remove_predict(p_r):
    infected_graph, centers = simulations[simulation](main_ref_graph)

    if nx.is_empty(infected_graph):
        return None
    ex_graph, removed_nodes = get_experiment_graph(infected_graph, p_r)

    if nx.is_empty(ex_graph):
        return None

    if not nx.is_connected(ex_graph):
        return None

    predicted_centers = {}
    for metric_name, metric_callback in metrics.items():
        predicted_centers[metric_name] = metric_callback(ex_graph)

    r = {
        "real_centers": centers,
        "predicted_centers": predicted_centers,
        "ex_graph": ex_graph,
        "removed_nodes": removed_nodes,
    }
    return r


results = {}
for p_r in tqdm(percent_radius):
    with Pool(3) as threads:
        results[p_r] = threads.map(simulate_remove_predict, [p_r] * sample_size)


if output_dir is not None:
    with open(join(output_dir, name_builder("results")), "wb") as f:
        pickle.dump(results, f)


# In[13]:


shortest_paths = nx.shortest_path(main_ref_graph)


# In[14]:


def get_best_hop_distance(g, original_centers, predicted_centers):
    best_pair = None
    best_distance = len(g.nodes)
    for o_c in original_centers:
        for p_c in predicted_centers:
            d = len(shortest_paths[o_c][p_c])
            if d < best_distance:
                best_distance = d
                best_pair = (o_c, p_c)
    return best_pair, best_distance

# In[15]:


def get_all_hop_distances(g, original_centers, predicted_centers):
    distances = []
    for o_c in original_centers:
        for p_c in predicted_centers:
            distances.append(len(shortest_paths[o_c][p_c]))
    return distances

from statistics import median

def get_median_hop_distance(g, original_centers, predicted_centers):
    return median(get_all_hop_distances(g, original_centers, predicted_centers))


center_results = {}
for k, v in results.items():
    predicted_centers = []
    for _r in v:
        if _r is None:
            predicted_centers.append((None, None))
        else:
            predicted_centers.append((_r["predicted_centers"], _r["real_centers"]))
    center_results[k] = predicted_centers


# In[18]:


reference_map = []

# Map results to hop distances
hop_distance_freq_by_p_r_by_metric = {}

for metric_name in metrics.keys():
    hop_distance_freq_by_p_r = {}
    for p_r, values in tqdm(center_results.items()):
        hop_distance_freq = {}
        for i, centers in tqdm(enumerate(values)):
            predicted_centers = centers[0]
            real_centers = centers[1]
            if predicted_centers is None or real_centers is None:
                hop_distance_freq[-1] = hop_distance_freq.get(-1, 0) + 1
                reference_map.append((p_r, i, -1))
            else:
                predicted_centers = predicted_centers[metric_name]
                # best_pair, best_distance = get_best_hop_distance(main_ref_graph, real_centers, predicted_centers)
                median_distance = get_median_hop_distance(main_ref_graph, real_centers, predicted_centers)
                hop_distance_freq[median_distance] = hop_distance_freq.get(median_distance, 0) + 1

                reference_map.append((p_r, i, median_distance))

        hop_distance_freq_by_p_r[p_r] = hop_distance_freq
    hop_distance_freq_by_p_r_by_metric[metric_name] = hop_distance_freq_by_p_r

if output_dir is not None:
    with open(join(output_dir, name_builder("hop_distance_freq_by_p_r_by_metric")), "wb") as f:
        pickle.dump(hop_distance_freq_by_p_r_by_metric, f)


def rgba(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 200*(1 - ratio)))
    r = int(max(0, 255*(ratio - 1)))
    g = 255 - b - r
    return r, g, b, 200

min_v_percent = min(percent_radius)
max_v_percent = max(percent_radius)

from pandas import DataFrame

def plot_metric(metric_name, ax):
    hop_distance_freq_by_p_r = hop_distance_freq_by_p_r_by_metric[metric_name]
    colors = ['#%02x%02x%02x%02x' % rgba(min_v_percent, max_v_percent, p) for p in hop_distance_freq_by_p_r.keys()]

    df = DataFrame(hop_distance_freq_by_p_r)
    df = df.reindex(index=sorted(df.index))
    df.plot.bar(color=colors, ax=ax, width=1)
    ax.set_title(f"{metric_name}")
    ax.set_ylabel("Freq")
    ax.set_xlabel("Hop Distance")
    return ax

from pandas import DataFrame

min_v_distance = None
max_v_distance = None

for metric_name in metrics:
    for v in hop_distance_freq_by_p_r_by_metric[metric_name].values():
        for hop_distance in v.keys():
            if min_v_distance is None or hop_distance < min_v_distance:
                min_v_distance = hop_distance

            if max_v_distance is None or hop_distance > max_v_distance:
                max_v_distance = hop_distance

def plot_metric_stacked(metric_name, ax):

    hop_distance_freq_by_p_r = hop_distance_freq_by_p_r_by_metric[metric_name]

    df = DataFrame(hop_distance_freq_by_p_r)
    df = df.reindex(index=sorted(df.index))
    df = df.transpose()

    colors = ['#%02x%02x%02x%02x' % rgba(min_v_distance, max_v_distance, hop) for hop in list(df.columns)]

    df.plot.bar(color=colors, stacked=True, ax=ax)
    ax.set_title(f"{metric_name}")
    ax.set_ylabel("Freq")
    ax.set_xlabel("Hop Distance")
    return ax


fig, axes = plt.subplots(1, len(metrics), figsize=(15,5), sharey=True)

for i, metric in enumerate(metrics):
    plot_metric(metric, axes[i])
fig.suptitle(f"Hop Distance Freq with various percent of nodes missing\n{graph_name} - {graph_size} nodes, {sample_size} samples")
fig.tight_layout()
fig.savefig(
    join(output_dir, name_builder("bar", pickle=False)),
    dpi=1024,
)


fig, axes = plt.subplots(1, len(metrics), figsize=(15,5), sharey=True)

for i, metric in enumerate(metrics):
    plot_metric_stacked(metric, axes[i])
fig.suptitle(f"Hop Distance Freq with various percent of nodes missing\n{graph_name} - {graph_size} nodes, {sample_size} samples")
fig.tight_layout()
fig.savefig(
    join(output_dir, name_builder("stacked_bar", pickle=False)),
    dpi=1024,
)

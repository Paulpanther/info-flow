"""Utility to generate graphs and to load graphs from datasets"""

import networkx as nx


small_world = nx.watts_strogatz_graph

scale_free = nx.scale_free_graph

synthetic_internet = nx.generators.random_internet_as_graph


def internet():
    return nx.read_edgelist("../data/as20000102.txt", create_using=nx.Graph(), nodetype=int)


def us_power_grid():
    return nx.read_edgelist("../data/uspowergrid.txt", create_using=nx.Graph(), nodetype=int, data=(("weight", float),))

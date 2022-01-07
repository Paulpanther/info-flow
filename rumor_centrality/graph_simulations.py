"""Utility to simulate different infection spread dynamics on a graph"""

from typing import List

import networkx as nx
from ndlib.models import ModelConfig
from ndlib.models.epidemics import SIModel, SISModel, SIRModel, SEIRModel, SEIRctModel, SEISModel, SEISctModel


def si(graph: nx.Graph, iterations: int, infection_prob: float, infections_centers: int, max_infected_nodes: int=-1) -> (nx.Graph, List[int]):
    return _run_model(SIModel, graph, iterations, [1], max_infected_nodes,
                      ("beta", infection_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def sis(graph: nx.Graph, iterations: int, infection_prob: float, recovery_prob: float, infections_centers: int, max_infected_nodes: int=-1) -> (nx.Graph, List[int]):
    return _run_model(SISModel, graph, iterations, [1], max_infected_nodes,
                      ("beta", infection_prob),
                      ("lambda", recovery_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def sir(graph: nx.Graph, iterations: int, infection_prob: float, removal_prob: float, infections_centers: int, max_infected_nodes: int=-1) -> (nx.Graph, List[int]):
    return _run_model(SIRModel, graph, iterations, [1, 2], max_infected_nodes,
                      ("beta", infection_prob),
                      ("gamma", removal_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def discrete_seir(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, removal_prob: float, infections_centers: int, max_infected_nodes: int=-1) -> (nx.Graph, List[int]):
    return _run_model(SEIRModel, graph, iterations, [1, 3], max_infected_nodes,
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("gamma", removal_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def continuous_seir(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, removal_prob: float, infections_centers: int, max_infected_nodes: int=-1) -> (nx.Graph, List[int]):
    return _run_model(SEIRctModel, graph, iterations, [1, 3], max_infected_nodes,
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("gamma", removal_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def discrete_seis(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, recovery_prob: float, infections_centers: int, max_infected_nodes: int=-1) -> (nx.Graph, List[int]):
    return _run_model(SEISModel, graph, iterations, [1], max_infected_nodes,
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("lambda", recovery_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def continous_seis(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, recovery_prob: float, infections_centers: int, max_infected_nodes: int=-1) -> (nx.Graph, List[int]):
    return _run_model(SEISctModel, graph, iterations, [1], max_infected_nodes,
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("lambda", recovery_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def _run_model(Model, graph: nx.Graph, iterations: int, allowed_states: List[int], max_infected_nodes: int, *config: (str, any)) -> (nx.Graph, List[int]):
    """
        Gets a graph, performs simulation of infections spread with given model.
        Returns infection tree and initial infected nodes.
        Graph is modified in-place
    """
    if (iterations < 0 and max_infected_nodes < 0) or (iterations > 0 and max_infected_nodes > 0):
        raise AttributeError("Either limited iterations or limited infections need to be specified")

    cfg = ModelConfig.Configuration()
    for key, value in config:
        cfg.add_model_parameter(key, value)

    model = Model(graph)
    model.set_initial_status(cfg)

    initial_infected = [node for (node, status) in model.status.items() if status == 1]

    if max_infected_nodes < 0:
        model.iteration_bunch(iterations, progress_bar=False)
    else:
        # Model simulation with abort if max infected node count is reached
        total_infected = 0
        while total_infected < max_infected_nodes:
            it_dict = model.iteration()
            node_status_dict = it_dict["status"]
            infected_nodes = [1 for v in node_status_dict.values() if v in allowed_states]
            total_infected += sum(infected_nodes)

    for node, status in model.status.items():
        if status not in allowed_states:
            graph.remove_node(node)

    return graph, initial_infected
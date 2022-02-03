"""Utility to simulate different infection spread dynamics on a graph"""
import random
from typing import List

import networkx as nx
from ndlib.models import ModelConfig
from ndlib.models.epidemics import SIModel, SISModel, SIRModel, SEIRModel, SEIRctModel, SEISModel, SEISctModel


def si(
        graph: nx.Graph,
        iterations: int,
        infection_prob: float,
        infections_centers: int,
        max_infected_nodes: int = -1,
        max_no_change: int = -1,
        fill_infection_count: bool = False
) -> (nx.Graph, List[int]):
    return _run_model(
        SIModel,
        graph,
        iterations,
        [1],
        max_infected_nodes,
        max_no_change,
        fill_infection_count,
        ("beta", infection_prob),
        ("fraction_infected", infections_centers / graph.number_of_nodes()))


def sis(
        graph: nx.Graph,
        iterations: int,
        infection_prob: float,
        recovery_prob: float,
        infections_centers: int,
        max_infected_nodes: int = -1,
        max_no_change: int = -1,
        fill_infection_count: bool = False
) -> (nx.Graph, List[int]):
    return _run_model(
        SISModel,
        graph,
        iterations,
        [1],
        max_infected_nodes,
        max_no_change,
        fill_infection_count,
        ("beta", infection_prob),
        ("lambda", recovery_prob),
        ("fraction_infected", infections_centers / graph.number_of_nodes()))


def sir(
        graph: nx.Graph,
        iterations: int,
        infection_prob: float,
        removal_prob: float,
        infections_centers: int,
        max_infected_nodes: int = -1,
        recovered_are_infected=True,
        max_no_change: int = -1,
        fill_infection_count: bool = False
) -> (nx.Graph, List[int]):
    return _run_model(
        SIRModel,
        graph,
        iterations,
        [1, 2] if recovered_are_infected else [1],
        max_infected_nodes,
        max_no_change,
        fill_infection_count,
        ("beta", infection_prob),
        ("gamma", removal_prob),
        ("fraction_infected", infections_centers / graph.number_of_nodes()))


def discrete_seir(
        graph: nx.Graph,
        iterations: int,
        infection_prob: float,
        latent_period: float,
        removal_prob: float,
        infections_centers: int,
        max_infected_nodes: int = -1,
        max_no_change: int = -1
) -> (nx.Graph, List[int]):
    return _run_model(
        SEIRModel,
        graph,
        iterations,
        [1, 3],
        max_infected_nodes,
        max_no_change,
        ("alpha", latent_period),
        ("beta", infection_prob),
        ("gamma", removal_prob),
        ("fraction_infected", infections_centers / graph.number_of_nodes()))


def continuous_seir(
        graph: nx.Graph,
        iterations: int,
        infection_prob: float,
        latent_period: float,
        removal_prob: float,
        infections_centers: int,
        max_infected_nodes: int = -1,
        max_no_change: int = -1
) -> (nx.Graph, List[int]):
    return _run_model(
        SEIRctModel,
        graph,
        iterations,
        [1, 3],
        max_infected_nodes,
        max_no_change,
        ("alpha", latent_period),
        ("beta", infection_prob),
        ("gamma", removal_prob),
        ("fraction_infected", infections_centers / graph.number_of_nodes()))


def discrete_seis(
        graph: nx.Graph,
        iterations: int,
        infection_prob: float,
        latent_period: float,
        recovery_prob: float,
        infections_centers: int,
        max_infected_nodes: int = -1,
        max_no_change: int = -1
) -> (nx.Graph, List[int]):
    return _run_model(
        SEISModel,
        graph,
        iterations,
        [1],
        max_infected_nodes,
        max_no_change,
        ("alpha", latent_period),
        ("beta", infection_prob),
        ("lambda", recovery_prob),
        ("fraction_infected", infections_centers / graph.number_of_nodes()))


def continous_seis(
        graph: nx.Graph,
        iterations: int,
        infection_prob: float,
        latent_period: float,
        recovery_prob: float,
        infections_centers: int,
        max_infected_nodes: int = -1,
        max_no_change: int = -1
) -> (nx.Graph, List[int]):
    return _run_model(
        SEISctModel,
        graph,
        iterations,
        [1],
        max_infected_nodes,
        max_no_change,
        ("alpha", latent_period),
        ("beta", infection_prob),
        ("lambda", recovery_prob),
        ("fraction_infected", infections_centers / graph.number_of_nodes()))


def _run_model(
        Model,
        raw_graph: nx.Graph,
        iterations: int,
        allowed_states: List[int],
        max_infected_nodes: int,
        max_no_change: int,
        fill_infection_count: bool,
        *config: (str, any)
) -> (nx.Graph, List[int]):
    """
        Gets a graph, performs simulation of infections spread with given model.
        Returns infection tree and initial infected nodes.
        Graph is modified in-place
    """

    graph = raw_graph.copy()

    if (iterations < 0 and max_infected_nodes < 0) or (iterations > 0 and max_infected_nodes > 0):
        raise AttributeError("Either limited iterations or limited infections need to be specified")

    if max_infected_nodes > 0 and max_infected_nodes > len(graph.nodes):
        raise AttributeError("More max_infected_nodes than nodes in Graph")

    cfg = ModelConfig.Configuration()
    for key, value in config:
        cfg.add_model_parameter(key, value)

    model = Model(graph)
    model.set_initial_status(cfg)

    initial_infected = [node for (node, status) in model.status.items() if status == 1]

    if max_infected_nodes < 0:
        model.iteration_bunch(iterations, progress_bar=True)
        status_dict = model.status.items()
        node_status = [(node, state in allowed_states) for (node, state) in status_dict]

    else:
        # Model simulation will abort if max infected node count is reached
        total_infected = 0
        times_of_no_change = 0
        status_dict = model.status.items()

        while total_infected < max_infected_nodes:
            it_dict = model.iteration()
            node_status_dict = it_dict["status"]
            infected_nodes = [1 for v in node_status_dict.values() if v in allowed_states]
            change = sum(infected_nodes)

            # Count how often there is no change
            # Abort if too often (this eliminates infinite loops for SIR/SIS)
            if change == 0:
                times_of_no_change += 1
                if max_no_change != -1 and times_of_no_change > max_no_change:
                    break

            total_infected += change

            if total_infected < max_infected_nodes:
                # Only update status if requirement is met
                status_dict = model.status.items()

        node_status = [(node, state in allowed_states) for (node, state) in status_dict]

        if fill_infection_count:
            node_status = _fill_missing_infections(graph, node_status, max_infected_nodes)

    for node, status in node_status:
        if not status:
            graph.remove_node(node)

    return graph, initial_infected


def _fill_missing_infections(g: nx.Graph, node_status, infection_goal: int):
    infected_nodes = [node for node, status in node_status if status]
    missing_infections = int(infection_goal - len(infected_nodes))

    if missing_infections <= 0:
        return node_status

    # All neighbors of infected nodes that are not infected
    infection_neighbors = list(set(very_ugly_flatten([list(g.neighbors(node)) for node in infected_nodes])) - set(infected_nodes))
    random.shuffle(infection_neighbors)
    newly_infected = infection_neighbors[0:min(missing_infections, len(infection_neighbors))]

    return [(node, True if node in newly_infected else status) for (node, status) in node_status]


def very_ugly_flatten(l: List[List[any]]) -> List[any]:
    return [item for sublist in l for item in sublist]

from typing import List

import networkx as nx
from ndlib.models import ModelConfig
from ndlib.models.epidemics import SIModel, SISModel, SIRModel, SEIRModel, SEIRctModel, SEISModel, SEISctModel

import graph_generator


def si(graph: nx.Graph, iterations: int, infection_prob: float, infections_centers: int) -> nx.Graph:
    return _run_model(SIModel, graph, iterations, [1],
                      ("beta", infection_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def sis(graph: nx.Graph, iterations: int, infection_prob: float, recovery_prob: float, infections_centers: int) -> nx.Graph:
    return _run_model(SISModel, graph, iterations, [1],
                      ("beta", infection_prob),
                      ("lambda", recovery_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def sir(graph: nx.Graph, iterations: int, infection_prob: float, removal_prob: float, infections_centers: int) -> nx.Graph:
    return _run_model(SIRModel, graph, iterations, [1, 2],
                      ("beta", infection_prob),
                      ("gamma", removal_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def discrete_seir(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, removal_prob: float, infections_centers: int) -> nx.Graph:
    return _run_model(SEIRModel, graph, iterations, [1, 3],
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("gamma", removal_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def continuous_seir(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, removal_prob: float, infections_centers: int) -> nx.Graph:
    return _run_model(SEIRctModel, graph, iterations, [1, 3],
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("gamma", removal_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def discrete_seis(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, recovery_prob: float, infections_centers: int) -> nx.Graph:
    return _run_model(SEISModel, graph, iterations, [1],
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("lambda", recovery_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def continous_seis(graph: nx.Graph, iterations: int, infection_prob: float, latent_period: float, recovery_prob: float, infections_centers: int) -> nx.Graph:
    return _run_model(SEISctModel, graph, iterations, [1],
                      ("alpha", latent_period),
                      ("beta", infection_prob),
                      ("lambda", recovery_prob),
                      ("fraction_infected", infections_centers / graph.number_of_nodes()))


def _run_model(Model, graph: nx.Graph, iterations: int, allowed_states: List[int], *config: (str, any)) -> nx.Graph:
    """
        Gets a graph, performs simulation of infections spread with given model and returns infection tree.
        Graph is modified in-place
    """
    cfg = ModelConfig.Configuration()
    for key, value in config:
        cfg.add_model_parameter(key, value)

    model = Model(graph)
    model.set_initial_status(cfg)
    model.iteration_bunch(iterations, progress_bar=True)

    for node, status in model.status.items():
        if status not in allowed_states:
            graph.remove_node(node)

    return graph


if __name__ == '__main__':
    print(continous_seis(graph_generator.complete(1000), 300, 0.2, 0.1, 0.1, 1).nodes)

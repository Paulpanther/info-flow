import networkx as nx


def star(size: int):
    return nx.star_graph(size)


def complete(size: int):
    return nx.complete_graph(size)

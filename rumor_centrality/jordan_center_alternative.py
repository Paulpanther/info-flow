"""Calculation of infection centers based on centrality scores"""

import networkx
from networkx.algorithms.distance_measures import center
from networkx.algorithms.centrality import betweenness_centrality, closeness_centrality
from typing import List


def centers_by_jordan_center(g: networkx.Graph) -> List[int]:
    """Infection centers by jordan centrality measurement"""
    return center(g)


def centers_by_betweenness_centrality(g: networkx.Graph) -> List[int]:
    """Infection centers by betweenness centrality measurement"""
    b_c_dict = betweenness_centrality(g)
    top_betweenness_centrality = sorted(b_c_dict.items(), key=lambda x: x[1], reverse=True)[0][1]
    return [node for node, score in b_c_dict.items() if score == top_betweenness_centrality]


def centers_by_distance_centrality(g: networkx.Graph) -> List[int]:
    """Infection centers by distance centrality measurement"""
    d_c_dict = closeness_centrality(g)
    top_distance_centrality = sorted(d_c_dict.items(), key=lambda x: x[1], reverse=True)[0][1]
    return [node for node, score in d_c_dict.items() if score == top_distance_centrality]


def test():
    g = networkx.karate_club_graph()

    print("centers_by_jordan_center")
    print(centers_by_jordan_center(g))
    print("centers_by_betweenness_centrality")
    print(centers_by_betweenness_centrality(g))
    print("centers_by_distance_centrality")
    print(centers_by_distance_centrality(g))


if __name__ == "__main__":
    test()

from collections import defaultdict
from typing import List

import networkx as nx
from networkx import single_source_shortest_path_length


def hop_distances(g: nx.Graph, predictions: List[int], groundtruths: List[int]) -> List[int]:
    assert len(predictions) == len(groundtruths), "number of predictions has to be the same as groundtruth"

    distance_matrix = defaultdict(dict)
    for groundtruth in groundtruths:
        distances_from_groundtruth = single_source_shortest_path_length(g, groundtruth)
        for predicted_source in predictions:
            distance_matrix[groundtruth][predicted_source] = distances_from_groundtruth[groundtruth][predicted_source]

    # iteratively find min distance and remove selected groundtruth (we don't want to be greedy, and also not clever)
    hop_distance = []
    for i in range(len(groundtruths)):
        cur_min = (0,0)
        for groundtruth in groundtruths:
            for predicted_source in predictions:
                if distance_matrix[groundtruth][predicted_source] < distance_matrix[cur_min[0]][cur_min[1]]:
                    cur_min = (groundtruth, predicted_source)

        hop_distance.append(distance_matrix[cur_min[0]][cur_min[1]])
        del distance_matrix[cur_min[0]]

    return hop_distance

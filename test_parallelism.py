import networkx as nx
import time
import sys

from rumor_centrality.rumor_detection import get_rumor_centrality_lookup, networkx_graph_to_adj_list


USE_FACT = False


def main():
    node_count = int(sys.argv[1])
    thread_count = int(sys.argv[2])

    g = nx.complete_graph(node_count)
    adj_list = networkx_graph_to_adj_list(g)
    start = time.time()
    seq_r = get_rumor_centrality_lookup(adj_list, USE_FACT, threads=1)
    seq_time = time.time() - start

    start = time.time()
    par_r = get_rumor_centrality_lookup(adj_list, USE_FACT, threads=thread_count)
    par_time = time.time() - start

    if all(map(lambda e: e[0] == e[1], zip(seq_r.items(), par_r.items()))):
        print("Results are the same!")
    else:
        print("Results differ!")
    print(f"Sequential Runtime: {seq_time} seconds")
    print(f"Parallel Runtime ({thread_count} threads): {par_time} seconds")


if __name__ == "__main__":
    main()

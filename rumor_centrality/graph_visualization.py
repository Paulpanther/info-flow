from typing import List

import networkx as nx
import plotly.graph_objects as go


def generate_nx_graph():
    G = nx.random_geometric_graph(200, 0.125)
    return G


def compute_node_degrees(G):
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: ' + str(len(adjacencies[1])))

    return node_adjacencies, node_text


def plot_nx_graph(G, node_marker=None, node_text=None, node_size=None, layout=nx.spring_layout):

    edge_x = []
    edge_y = []

    positions = nx.get_node_attributes(G, 'pos')

    if len(positions) == 0:
        positions = layout(G)
    for edge in G.edges():
        # x0, y0 = G.nodes[edge[0]]['pos']
        x0, y0 = positions[edge[0]]
        # x1, y1 = G.nodes[edge[1]]['pos']
        x1, y1 = positions[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        # x, y = G.nodes[node]['pos']
        x,y = positions[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=node_size,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    if node_marker is not None and node_text is not None:
        node_trace.marker.color = node_marker
        node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Network graph',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()


def multiple_histograms(values_each: List[List[float]], names: List[str], x_label: str, y_label: str, sup_title: str, mod=10):
    from matplotlib import pyplot as plt

    n = len(values_each)

    frequencies = []
    for i in range(n):
        values = values_each[i]
        values = [-1 if v is None else v for v in values]
        uniq_values = list(set(values))
        f = dict([(u, values.count(u)) for u in uniq_values])
        frequencies.append(f)

    fig, axes = plt.subplots(1, n, sharey=True, figsize=(10, 10))

    for i, sim_name in enumerate(names):
        ax = axes[i] if n > 1 else axes
        ax.bar(
            frequencies[i].keys(),
            frequencies[i].values(),
            label=sim_name,
            width=1,
        )

        ax.set_title(sim_name)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.set_xticks([x for x in list(frequencies[i].keys()) if x % mod == 0])

    ax_root = axes[0] if n > 1 else axes
    ax_root.legend()
    fig.suptitle(sup_title)


if __name__ == '__main__':
    G = generate_nx_graph()
    n_markers, n_text = compute_node_degrees(G)
    plot_nx_graph(G, n_markers, n_text)

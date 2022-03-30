# Robust Source Detection

Part of the Information Flow Seminar in the Winter Term 2021/2022 at HPI.

In this repository, you can find:

1. An open-source python implementation of [Rumor Centrality](https://dspace.mit.edu/handle/1721.1/63150)
   in `rumor_centrality.rumor_detection.py`
2. Easy graph generation using networkx in `rumor_centrality.graph_generator.py`
3. Easy infection simulation using ndlib in `rumor_centrality.graph_simulations.py`
4. Notebooks and code to run experiments with different combination of graphs, spreading behavior, and source detection
   algorithms (mainly `TopologyMatrix.ipynb`)
5. Notebooks and code to experiment with missing values in source detection (`missing_experiment.py`
   and `EDA of Missing Data Experiments.ipynb`)
6. Notebooks and code to experiment with multiple sources (`multiple_centers_experiment.py` and
   the `Multiple Rumor Centers` notebooks)


## Setup

To run the code here, you need at least Python 3.6 and then install the requirements in `requirements.txt`.
Usage of a virtual environment is encouraged.

```
pip install -r requirements.txt
```


## Comparison of Centrality Metrics in Different Scenarios

The Notebook `TopologyMatrix.ipynb` visualizes a comparison between `Rumor Centrality`, `Distance Centrality`, `Betweenness Centrality`, and `Jordan Centrality` on Small World, Scale Free, Synthetic Internet and US Power Grid graphs infected with SI, SIS and SIR to the infection sizes of 10, 100, 200, 300, 400, 500, 600, 700, 800 and 900 nodes. The predictions are evaluated using Mean Diameter Normalize Hop Distance.

The second cell of the Notebook contains the parameters for the Dynamics, Predictiors, Infections Counts, Graphs and Amount of Repetitions. All parameters can be changed there and new dynamics, graphs and predictors can be added.

The following cells describe the process of generating, simulating and predicting. Because the process take a long time, it can be manually subdivided into smaller steps and the partial results can be stored and loaded using the `save` and `load` functions. 

The last cell renders the matrix. Here some visualization parameters can be changed, like which data to show, the tick size and data range.

## Missing Node Experiments

While collecting the status of nodes of an information spread, false negatives can occur. This leads to actually
infected people, actually congested traffic junctions or similar not being represented as a node in the infection
graph (there obviously can be false positives as well, but we did not experiment with that).

The experiments of testing the impact of missing nodes for the informaction source detection follow the following
process:

1. Simulate an infection using the `SI Model` in the chosen network until 30% of all nodes are infected
2. Use all four metrics (`Rumor Centrality`, `Jordan Centrality`, `Distance Centrality`, `Betweenness Centrality`) to
   predict the source of the simulated infection
3. Remove a certain percent of infected nodes, reconnect the neighbors of the removed node to a clique and repeat the
   source prediction step on the resulting reduced and reconnected infection graph
4. Measure the distance of all predicted sources to the original source of the simulation

Each step of the process creates some data usefull for our research:

1. Creates a baseline infection graph
2. Creates a baseline prediction (i.e. 0% of infected nodes removed)
3. Creates a reduced infection graph and source predictions for that graph
4. Creates distances form predicted sources to original source, thus making all source predictions compareable

The described process and the data created can be reproduced with the `missing_experiment.py` script:

```
python3 missing_experiment.py graph output_dir diffusion_dynamic 
```

The options for `graph` are: `synthetic_internet_100`, `synthetic_internet_1000`, `scale_free_100`, `scale_free_1000`
, `us_power_grid`, and `internet` (Note that we only use `synthetic_internet_1000`, `scale_free_1000`
and `us_power_grid`).

You can freely choose the output directory, if it does not exist, the script will create it.

The options for `diffusion_dynamic` are: `si`, `sis`, and `sir` (Note that we only use `si`).

The script will create a folder for the dynamic you chose and a sub-folder for the chosen graph (
eg. `output_dir/si/scale_free_100`). In this folder you will find the results of the computation. To better separate the
files of different experiments, the results are named after the following schema:
`{data_name}__config_graph_{graph}_nodes_{graph_size}_samples_{sample_size}_`
There are 5 files per run, all identified by the `{data_name}` attribute:

1. `bar__[...]`: A hist plot for each of the four metrics. Each hist visualizes the frequencies of hop distances from
   predicted source to original source, dependent on how many nodes were removed. Hop Distance on x, missing percent as
   data.
2. `stacked_bar__[...]`: Contains the same data as `bar__[...]` but visualizes as stacked bar plot, with missing percent
   on x and the hop distance distribution as plotted data.
3. `main_ref_graph__[...]`: This is a [pickle](https://docs.python.org/3/library/pickle.html) file containing the
   networkx graph object of the base graph, the infection simulations were run on. This is important, as synthetic
   graphs are not fixed to a seed, and change for each run of the script.
4. `results__[...]`: The main experiment data. A pickle file, containing a dictionary, mapping percent missing to a list
   of all sample results. Each sample result contains the original sources (`real_centers`), the reduced infected
   graph (`ex_graph`), the nodes that were removed to create `ex_graph` (`removed_nodes`) and
   finally `predicted_centers`, which contains a dictionary with a key for each metric. In this dictionary each metric
   maps to a list of all the nodes, that were detected as potential information flow sources.

You can use the `EDA of Missing Data Experiments.ipynb` notebook to read in the results of the script, without parsing
manually. This notebook also contains logic to normalize and visualize our results, exactly the same way we used for
creating our report.

## Multiple Rumor Centers

An infection can have more than one source. We want to try to infer those. For that, we first partition the graph in `k`
subgraphs, and then apply the metrics on those. Specifically, we follow those steps:

1. Simulate an infection using the `SI Model` in the chosen network until the desired number of nodes are infected on
   from `k` many sources (making sure the resulting graph is connected)
2. Partition the graph into `k`
3. Use all four metrics (`Rumor Centrality`, `Jordan Centrality`, `Distance Centrality`, `Betweenness Centrality`) to
   predict the source of the simulated infection in each partition
4. Measure the distances from the predictions to the original sources

The approach is outlined in `Multiple Rumor Centers - Overview.ipynb`. Most of the code for this can be found
in `rumor_centrality.graph_clustering.py`

The first 3 steps can be carried out by using the `multiple_centers_experiment.py` script:

```
python multiple_centers_experiment.py <cluster_numbers> <output_dir>
```

where `cluster_numbers` is a comma seperated list of clusters, for which the experiment should be run. Example usage:

```
python multiple_centers_experiment.py 2,3,5,7 results
```

This runs the experiment on the graphs `synthetic_internet_10000`, `scale_free_10000`, and `us_power_grid` repeating
each experiment 100 times.

The output will be written to the `<output_dir>` folder in form of
a [pickle](https://docs.python.org/3/library/pickle.html) file containing a Dictionary for each run containing:

- the `hops` (list of hops)
- `graph_normalized_hops`
- `diameter`
- `num_infection_centers`
- `max_infected_nodes`
- `predictions` (i.e. the predicted source nodes, also a list)
- `ground_truths` (i.e. the original sources, also a list)
- the actual networkx `graph`
- as well as `metric`

Instead of the script, you can also use the notebook `Multiple Rumor Centers - Experiment.ipynb` to carry out the
experiment. The main method for this can also be found in `rumor_centrality.experiment.py`

Using the pickled results file, you can use the `Multiple Rumor Centers Analysis.ipynb` notebook to analyze your
results. This performs the necessary data cleaning and preparation as well as visualization to get the same results as
seen in our report.

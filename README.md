# info-flow - Source Detection

We will fill you out later :)

## Missing Node Experiments
While collecting the status of nodes of an information spread, false negatives can occur. This leads to actually infected people, actually congested traffic junctions or similar not being represented as a node in the infection graph (there obviously can be false positives as well, but we did not experiment with that).

The experiments of testing the impact of missing nodes for the informaction source detection follow the following process:
1. Simulate an infection using the `SI Model` in the choosen network until 30% of all nodes are infected
2. Use all four metrics (`Rumor Centrality`, `Jordan Centrality`, `Distance Centrality`, `Betweenness Centrality`) to predict the source of the simulated infection
3. Remove a certain percent of infected nodes, reconnect the neighbors of the removed node to a clique and repeat the source prediction step on the resulting reduced and reconnected infection graph 
4. Measure the distance of all predicted sources to the original source of the simulation

Each step of the process creates some data usefull for our research:
1. Creates a baseline infection graph
2. Creates a baseline prediction (eg. 0% of infected nodes removed)
3. Creates a reduced infection graph and source predictions for that graph
4. Creates distances form predicted sources to original source, thus making all source predictions compareable

The described process and the data created can be reproduced with the `missing_experiment.py` script:
```
python3 missing_experiment.py graph output_dir diffusion_dynamic 
```

The options for `graph` are: `synthetic_internet_100`, `synthetic_internet_1000`, `scale_free_100`, `scale_free_1000`, `us_power_grid`, and `internet` (Note that we only use `synthetic_internet_1000`, `scale_free_1000` and `us_power_grid`).

You can freely choose the output directory, if it does not exist, the script will create it.

The options for `diffusion_dynamic` are: `si`, `sis`, and `sir` (Note that we only use `si`).

The script will create a folder for the dynamic you chose and a sub-folder for the chosen graph (eg. `output_dir/si/scale_free_100`). In this folder you will find the results of the computation. To better separate the files of different experiments, the results are named after the following schema:
`{data_name}__config_graph_{graph}_nodes_{graph_size}_samples_{sample_size}_`
There are 5 files per run, all identified by the `{data_name}` attribute:
1. `bar__[...]`: A hist plot for each of the four metrics. Each hist visualizes the frequencies of hop distances from predicted source to original source, dependent on how many nodes were removed. Hop Distance on x, missing percent as data.
2. `stacked_bar__[...]`: Contains the same data as `bar__[...]` but visualizes as stacked bar plot, with missing percent on x and the hop distance distribution as plotted data.
3. `main_ref_graph__[...]`: This is a ![pickle](https://docs.python.org/3/library/pickle.html) file containing the networkx graph object of the base graph, the infection simulations were run on. This is important, as synthetic graphs are not fixed to a seed, and change for each run of the script.
4. `results__[...]`: The main experiment data. A pickle file, containing a dictionary, mapping percent missing to a list of all sample results. Each sample result contains the original sources (`real_centers`), the reduced infected graph (`ex_graph`), the nodes that were removed to create `ex_graph` (`removed_nodes`) and finally `predicted_centers`, which contains a dictionary with a key for each metric. In this dictionary each metric maps to a list of all the nodes, that were detected as potential information flow sources.

You can use the `EDA of Missing Data Experiments.ipynb` notebook to read in the results of the script, without parsing manually. This notebook also contains logic to normalize and visualize our results, exactly the same way we used for creating our report.




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

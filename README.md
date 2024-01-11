# gfa_subgraphs
This small tool has 3 functionalities:
* Separating a neighborhood around 1 or more nodes chosen by the user from a GFA graph into a subgraph
* Separates different components in the graph based on their sequence size or number of nodes size.
* Given alignments to the graph, it can separate only these alignments and a neighborhood around them to make visualizing very big graph easier. It also produces Bandage-compatible colors for these alignments.

If you're interested in seeing more functionalitie, please open an issue with the intended input and outputs wanted and I will try my best to implement these improvements asap.
## Installation:
To install for user only
```
python setup.py install --user
```

Or if you have root access then without `--user`

## Usage:
```
usage: GFASubgraph [-h] [-g GRAPH_PATH] [--log_file LOG_FILE]
                   [--log LOG_LEVEL]
                   {output_comps,bfs,alignment_subgraph,low_cov_edges} ...

Output neighborhood in Graph

Subcommands:
  {output_comps,bfs,alignment_subgraph,low_cov_edges}
                        Available subcommands
    output_comps        Command for outputting each connected component in a
                        separate GFA file
    bfs                 Command for separating neighborhood
    alignment_subgraph  Command for outputting each connected component in a
                        separate GFA file
    low_cov_edges       Command for outputting each connected component in a
                        separate GFA file

Global Arguments:
  -h, --help            show this help message and exit
  -g GRAPH_PATH, --in_graph GRAPH_PATH
                        graph file path (GFA or VG)
  --log_file LOG_FILE   The name/path of the log file. Default: log.log
  --log LOG_LEVEL       The logging level [DEBUG, INFO, WARNING, ERROR,
                        CRITICAL]
```

The tool has one required argument `-g` which is the GFA file path, and two optional arguments, log file name `--log_file`, and 
logging level `--log`.

Then there are 3 subcommands
### BFS subcommand
This takes a node id or several node ids space-separated, and a neighborhood size as integer and an output file name:
```
$ GFASubgraph bfs -h
usage: GFASubgraph bfs [-h] [--start START_NODES [START_NODES ...]] [--neighborhood_size SIZE] [--output_neighborhood OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --start START_NODES [START_NODES ...]
                        Give the starting node(s) for neighborhood extraction
  --cores CORES         number of threads
  --neighborhood_size SIZE
                        With -s --start option, size of neighborhood to extract
  --output_neighborhood OUTPUT
                        Output neighborhood file

```

### Connected Components subcommand
This subcommand outputs the connected components as separate files, user can choose the `n` largest components in terms of node size.
If the `-n, --n-components` was left empty, then all components are outputted to the chosen directory, they are named in this fashion `component{1,2,3...}.gfa`

The argument `--seq-size` is a true or false argument, when given, then the components are sorted based on their seq size and not number of nodes.

```
$ GFASubgraph output_comps -h
usage: GFASubgraph output_comps [-h] [--output_dir OUTPUT_DIR] [-n N_COMPS]

optional arguments:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR
                        Output neighborhood file
  -n N_COMPS, --n-components N_COMPS
                        If you want to output the n largest components in node size. Default: all
  --seq-size            If this argument given, then the components are sorted based on the seq size

```

### Alignments subgraph subcommand
This subcommand takes an input alignment file to the graph in GAF format `--input_gaf`, and an optional list 
of alignment names `--alignment_list` as a text file with each name in one line, also takes a neighborhood size as integer `--neighborhood_size`. 

The idea here is that it goes through each path for each alignment given, takes each node in that path as a starting node to perform BFS search with a neighborhood size as given by the user, and extract the subgraph corresponding to this. So if the neighborhood size is 1, GFASubgraph will only extract the path the alignment took in the graph as a subgraph.

It also produces a CSV file with node IDs of the alignment and each alignment gets a color randomly, so the user can color the graph loaded with `Bandage` by given it the CSV file and coloring according to that CSV file.

```
# GFASubgraph alignment_subgraph -h

usage: GFASubgraph alignment_subgraph [-h] [--input_gaf INPUT_GAF] [--alignment_list ALIGNMENT_LIST]
                                      [--neighborhood_size SIZE] [--prefix PREFIX]

optional arguments:
  -h, --help            show this help message and exit
  --input_gaf INPUT_GAF
                        The input alignment gaf file
  --alignment_list ALIGNMENT_LIST
                        List of sequence names from the GAF file to separate, if not given all
                        alignments in GAF will be considered
  --neighborhood_size SIZE
                        the neighborhood size around each node in the alignment path, default: 3
  --prefix PREFIX       prefix for the output files

```
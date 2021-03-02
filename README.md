# gfa_subgraphs
A tool that can separate a neighborhood with user defined size around a node or nodes in the graph, and output it into a new GFA file for better debugging, visualization and analysis.
This tool can also separate connected components to separate GFA files.

##Installation:
To install for user only
```
python setup.py install --user
```

Or if you have root access then without `--user`

##Usage:
```
$ GFASubgraph -h

usage: GFASubgraph [-h] [-e] [-g GRAPH_PATH] [--log LOG_LEVEL] {output_comps,bfs} ...

Output neighborhood in Graph

Subcommands:
  {output_comps,bfs}    Available subcommands
    output_comps        Command for outputiing each connected component in a separate GFA file
    bfs                 Command for separating neighborhood

Global Arguments:
  -h, --help            show this help message and exit
  -e, --examples        prints out example commands to use the tool
  -g GRAPH_PATH, --in_graph GRAPH_PATH
                        graph file path (GFA or VG)
  --log LOG_LEVEL       The logging level [DEBUG, INFO, WARNING, ERROR, CRITICAL]

```

The tool has one required argument `-g` which is the GFA file path, then there are two subcommands

### BFS subcommand
This takes a node id or several node ids space-separated, and a neighborhood size as integer and an output file name:
```
$ GFASubgraph bfs -h
usage: GFASubgraph bfs [-h] [--start START_NODES [START_NODES ...]] [--neighborhood_size SIZE] [--output_neighborhood OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --start START_NODES [START_NODES ...]
                        Give the starting node(s) for neighborhood extraction
  --neighborhood_size SIZE
                        With -s --start option, size of neighborhood to extract
  --output_neighborhood OUTPUT
                        Output neighborhood file

```

### Connected Components subcommand
Takes an output directory path and it will output separate GFA files named as `component{1,2,3...}.gfa`

```
$ GFASubgraph output_comps -h
usage: GFASubgraph output_comps [-h] [--output_dir OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR
                        Output neighborhood file

```

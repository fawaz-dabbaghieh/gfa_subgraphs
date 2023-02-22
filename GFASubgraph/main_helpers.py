import logging
import sys
import os
from GFASubgraph.bfs import bfs
from collections import defaultdict


def bfs_queue(graph, n, length, queue):

    set_of_nodes = bfs(graph, n, length)
    if set_of_nodes:
        queue.put(set_of_nodes)
    queue.put(None)


def seq_size(graph, nodes):
    counter = 0
    for n in nodes:
        counter += graph.nodes[n].seq_len
    return counter


def error(msg, logfile):
    print(f"There has been an error, check the log file {logfile}")
    logging.error(msg)
    sys.exit(1)


def warning(msg, logfile):
    print("there were warnings, please check the log")
    logging.warning("WARNING " + msg)


def read_gaf(in_gaf, log_file):
    if not os.path.exists(in_gaf):
        error(f"The file {in_gaf} does not exist", log_file)
        return None

    else:
        alignments = dict()
        with open(in_gaf, "r") as infile:
            for l in infile:
                l = l.strip().split("\t")
                name = l[0]
                where_id = [idx for idx in range(len(l)) if "id:f" in l[idx]][0]
                l_length = int(l[3]) - int(l[2])  # alignment length
                l_id = l[where_id].split(":")[-1]
                coordinates = f"{l[2]}_{l[3]}"
                name = name + "_" + coordinates
                path = l[5]
                if path[0] in {"<", ">"}:  # making sure it is where the path is
                    path = path[1:].replace(">", ",")  # removing the first > or <
                    path = path.replace("<", ",")
                    alignments[name] = [path.split(","), l_length, l_id]

        return alignments


def extract_alignments(alignment_nodes, graph, n_size, final_nodes):
    for n in alignment_nodes:  # each one is a start node for bfs
        if n not in graph:
            logging.warning(f"The node {n} was not present in the graph, skipping")
            continue

        if n_size == 1:  # only the node of the path
            set_of_nodes = {n}
        else:
            set_of_nodes = bfs(graph, n, n_size)
        for n_id in set_of_nodes:
            final_nodes.add(n_id)  # if the node already exists won't be added twice


def check_candidate_edges(graph, edge, n_size):
    # as I'm doing BFS, doesn't matter from which edge I start
    # both nodes will be included

    # edge is (n1, side1, n2, side2, overlap)
    start_node = edge[0]
    neighborhood = bfs(graph, start_node, n_size)
    chrom_set = defaultdict(list)
    for n in neighborhood:
        if graph[n].chromosome:
            chrom_set[graph[n].chromosome].append(n)
    if len(chrom_set.keys()) == 1:
        return None
    else:
        return chrom_set

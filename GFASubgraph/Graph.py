from GFASubgraph.graph_io import read_gfa, write_gfa
from GFASubgraph.connected_components import all_components
from GFASubgraph.bfs import bfs
from GFASubgraph.Node import Node
import sys
import logging
import os
import pdb


class Graph:
    """
    Graph object containing the important information about the graph
    """

    __slots__ = ['nodes', 'edge_counts']

    def __init__(self, graph_file=None, edge_count=False, low_mem=False):
        if graph_file is not None:
            if not os.path.exists(graph_file):
                print("Error! Check log file.")
                logging.error("graph file {} does not exist".format(graph_file))
                sys.exit()
            # loading nodes from file
            self.nodes = read_gfa(gfa_file_path=graph_file, low_mem=low_mem)
            if edge_count:
                self.edge_counts = self.get_edges_counts(graph_file)
        else:
            self.nodes = dict()
            self.edge_counts = dict()

    def __len__(self):
        """
        overloading the length function
        """
        return len(self.nodes)

    def __str__(self):
        """
        overloading the string function for printing
        """
        return "The graph has {} Nodes".format(len(self.nodes))

    def __contains__(self, key):
        """
        overloading the in operator to check if node exists in graph
        """
        return key in self.nodes

    def __getitem__(self, key):
        """
        overloading the bracket operator
        """
        try:
            return self.nodes[key]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        """
        overloading setting an item in nodes
        """
        if isinstance(value, Node):
            self.nodes[key] = value
        else:
            raise ValueError("the object given to set should be a Node object")

    def __delitem__(self, key):
        """
        overloading deleting item
        """
        del self.nodes[key]

    def reset_visited(self):
        """
        resets all nodes.visited to false
        """
        for n in self.nodes.values():
            n.visited = False

# todo make remove start and remove end separate so I can use the same functions
#   for removing one edge
    def remove_node(self, n_id):
        """
        remove a node and its corresponding edges
        """
        starts = [x for x in self.nodes[n_id].start]
        for n_start in starts:
            overlap = n_start[2]
            if n_start[1] == 1:
                self.nodes[n_start[0]].end.remove((n_id, 0, overlap))
            else:
                self.nodes[n_start[0]].start.remove((n_id, 0, overlap))

        ends = [x for x in self.nodes[n_id].end]
        for n_end in ends:
            overlap = n_end[2]
            if n_end[1] == 1:
                self.nodes[n_end[0]].end.remove((n_id, 1, overlap))
            else:
                self.nodes[n_end[0]].start.remove((n_id, 1, overlap))

        del self.nodes[n_id]

    def remove_lonely_nodes(self):
        """
        remove singular nodes with no neighbors
        """
        nodes_to_remove = [n.id for n in self.nodes.values() if len(n.neighbors()) == 0]
        for i in nodes_to_remove:
            self.remove_node(i)

    def write_graph(self, set_of_nodes=None,
                    output_file="output_graph.gfa",
                    append=False):
        """writes a graph file as GFA

        list_of_nodes can be a list of node ids to write
        ignore_nodes is a list of node ids to not write out
        if append is set to true then output file should be an existing
        graph file to append to
        modified to output a modified graph file
        """
        if not output_file.endswith(".gfa"):
            output_file += ".gfa"
        # print("I am here")
        write_gfa(self, set_of_nodes=set_of_nodes, output_file=output_file,
                  append=append)

    def bfs(self, start, size):
        """
        Returns a neighborhood of size given around start node

        :param start: starting node for the BFS search
        :param size: size of the neighborhood to return
        """

        neighborhood = bfs(self, start, size)
        return neighborhood

    def output_components(self, output_dir):
        """
        writes each connected component in a separate GFA file
        """
        connected_comps = all_components(self)
        counter = 1
        for cc in connected_comps:
            if len(cc) > 1:
                output_file = output_dir + os.path.sep + "component{}.gfa".format(counter)
                counter += 1
                logging.info("Writing Component {}...".format(output_file))

                self.write_graph(set_of_nodes=cc, output_file=output_file, append=False)

    def remove_edge(self, edge):
        n1, side1, n2, side2, overlap = edge
        if side1 == 0:
            self.nodes[n1].remove_from_start(n2, side2, overlap)
        else:
            self.nodes[n1].remove_from_end(n2, side2, overlap)

        if side2 == 0:
            self.nodes[n2].remove_from_start(n1, side1, overlap)
        else:
            self.nodes[n2].remove_from_end(n1, side1, overlap)

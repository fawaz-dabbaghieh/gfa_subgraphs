from .graph_io import read_gfa, write_gfa
from .connected_components import all_components
from .bfs import bfs
import sys
import logging
import os


class Graph:
    """
    Graph object containing the important information about the graph
    """

    __slots__ = ['nodes', 'b_chains', 'child_parent']

    def __init__(self, graph_file=None):
        if graph_file is not None:
            if not os.path.exists(graph_file):
                print("graph file {} does not exist".format(graph_file))
                sys.exit()
            # loading nodes from file
            self.nodes = read_gfa(gfa_file_path=graph_file)
        else:
            self.nodes = dict()
        # elif graph_file.endswith(".vg"):
        #     self.nodes = read_vg(vg_file_path=graph_file, k=k, modified=modified, coverage=coverage)

        self.b_chains = set()  # list of BubbleChain objects
        # self.bubbles = set()
        # self.k = 1
        self.child_parent = dict()

    def __len__(self):
        """
        overloading the length function
        """

        return len(self.nodes)

    def __str__(self):
        """
        overloading the string function for printing
        """

        return "The graph has {} Nodes and {} chains".format(
            len(self.nodes), len(self.b_chains))

    def reset_visited(self):
        """
        resets all nodes.visited to false
        """

        for n in self.nodes.values():
            n.visited = False

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

import os
import sys
from GFASubgraph.Node import Node
import logging


def write_gfa(graph, set_of_nodes=None,
              output_file="output_file.gfa", append=False):
    """
    Write a gfa out

    :param nodes: Dictionary of nodes object.
    :param set_of_nodes: A list of node ids of the path or nodes we want to generate a GFA file for.
    :param output_file: path to output file
    :param append: if I want to append to a file instead of rewriting it
    """
    nodes = graph.nodes

    if set_of_nodes is None:
        set_of_nodes = graph.nodes.keys()

    if append is False:
        f = open(output_file, "w+")
    else:
        if os.path.exists(output_file):
            f = open(output_file, "a")
        else:
            logging.warning("Trying to append to a non-existent file\n"
                            "creating an output file")
            f = open(output_file, "w+")
    for n1 in set_of_nodes:
        if n1 not in nodes:
            logging.warning("Node {} does not exist in the graph, skipped in output".format(n1))
            continue

        # else:
        if nodes[n1].optional:  # if there are extra tags, write them as is
            line = str("\t".join(["S", str(n1), nodes[n1].seq, nodes[n1].optional]))
            # line = str("\t".join(("S", str(n1), nodes[n1].seq, nodes[n1].optional)))
        else:
            line = str("\t".join(["S", str(n1), nodes[n1].seq]))

        f.write(line)

        # writing edges
        edges = []
        # overlap = str(graph.k - 1) + "M\n"

        for n in nodes[n1].start:
            overlap = str(n[2]) + "M\n"

            if n[0] in set_of_nodes:
                if n[1] == 0:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "+", overlap)))
                    edges.append(edge)
                else:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "-", overlap)))
                    edges.append(edge)

        for n in nodes[n1].end:
            overlap = str(n[2]) + "M\n"

            if n[0] in set_of_nodes:
                if n[1] == 0:
                    edge = str("\t".join(("L", str(n1), "+", str(n[0]), "+", overlap)))
                    edges.append(edge)
                else:
                    edge = str("\t".join(("L", str(n1), "+", str(n[0]), "-", overlap)))
                    edges.append(edge)

        for e in edges:
            f.write(e)

    f.close()


def read_gfa(gfa_file_path):
    """
    Read a gfa file

    :param gfa_file_path: gfa graph file.
    """
    if not os.path.exists(gfa_file_path):
        logging.error("the gfa file path you gave does not exists, please try again!")
        sys.exit()

    nodes = dict()
    edges = []

    with open(gfa_file_path, "r") as lines:
        for line in lines:
            if line.startswith("S"):
                line = line.split("\t")
                n_id = str(line[1])
                n_len = len(line[2])
                nodes[n_id] = Node(n_id)

                nodes[n_id].seq_len = n_len
                nodes[n_id].seq = str(line[2]).strip()
                # adding the extra tags if any to the node object
                if len(line) > 3:
                    nodes[n_id].optional = "\t".join(line[3:])

            elif line.startswith("L"):
                edges.append(line)

    for e in edges:
        line = e.split()

        # I take the overlap in 5 and see if there are any more tags and make a dict out of them
        k = line[1]
        if k not in nodes:  # if the edge is there but not the node
            continue

        overlap = int(line[5][:-1])

        neighbor = line[3]
        if neighbor not in nodes:
            continue

        if line[2] == "-":
            from_start = True
        else:
            from_start = False

        if line[4] == "-":
            to_end = True
        else:
            to_end = False

        if from_start and to_end:  # from start to end L x - y -
            if (neighbor, 1, overlap) not in nodes[k].start:
                nodes[k].start.add((neighbor, 1, overlap))
            if (k, 0, overlap) not in nodes[neighbor].end:
                nodes[neighbor].end.add((k, 0, overlap))

        elif from_start and not to_end:  # from start to start L x - y +

            if (neighbor, 0, overlap) not in nodes[k].start:
                nodes[k].start.add((neighbor, 0, overlap))

            if (k, 0, overlap) not in nodes[neighbor].start:
                nodes[neighbor].start.add((k, 0, overlap))

        elif not from_start and not to_end:  # from end to start L x + y +
            if (neighbor, 0, overlap) not in nodes[k].end:
                nodes[k].end.add((neighbor, 0, overlap))

            if (k, 1, overlap) not in nodes[neighbor].start:
                nodes[neighbor].start.add((k, 1, overlap))

        elif not from_start and to_end:  # from end to end L x + y -
            if (neighbor, 1, overlap) not in nodes[k].end:
                nodes[k].end.add((neighbor, 1, overlap))

            if (k, 1, overlap) not in nodes[neighbor].end:
                nodes[neighbor].end.add((k, 1, overlap))

    return nodes


def get_edges_counts(graph_file):
    edge_counts = dict()
    with open(graph_file, "r") as infile:
        for l in infile:
            count = -1
            if l.startswith("L"):

                line = l.split()
                if len(line) < 7:
                    logging.warning(f"the edge {'   '.join(line)} does not have counts")
                    count = 0
                else:
                    if not line[6].startswith("ec"):
                        logging.warning(f'the edge {"   ".join(line)} does not have the ec tag')
                        count = 0

                # I take the overlap in 5 and see if there are any more tags and make a dict out of them
                k = str(line[1])
                overlap = int(line[5][:-1])
                if count == -1:
                    count = int(line[6].split(":")[-1])

                neighbor = str(line[3])
                if line[2] == "-":
                    from_start = True
                else:
                    from_start = False

                if line[4] == "-":
                    to_end = True
                else:
                    to_end = False

                if from_start and to_end:  # from start to end L x - y -
                    edge_counts[(k, 0, neighbor, 1, overlap)] = count
                    # if (neighbor, 1, overlap) not in nodes[k].start:
                    #     nodes[k].start.add((neighbor, 1, overlap))
                    # if (k, 0, overlap) not in nodes[neighbor].end:
                    #     nodes[neighbor].end.add((k, 0, overlap))

                elif from_start and not to_end:  # from start to start L x - y +
                    edge_counts[(k, 0, neighbor, 0, overlap)] = count
                    # if (neighbor, 0, overlap) not in nodes[k].start:
                    #     nodes[k].start.add((neighbor, 0, overlap))
                    #
                    # if (k, 0, overlap) not in nodes[neighbor].start:
                    #     nodes[neighbor].start.add((k, 0, overlap))

                elif not from_start and not to_end:  # from end to start L x + y +
                    edge_counts[(k, 1, neighbor, 0, overlap)] = count
                    # if (neighbor, 0, overlap) not in nodes[k].end:
                    #     nodes[k].end.add((neighbor, 0, overlap))
                    #
                    # if (k, 1, overlap) not in nodes[neighbor].start:
                    #     nodes[neighbor].start.add((k, 1, overlap))

                elif not from_start and to_end:  # from end to end L x + y -
                    edge_counts[(k, 1, neighbor, 1, overlap)] = count
                    # if (neighbor, 1, overlap) not in nodes[k].end:
                    #     nodes[k].end.add((neighbor, 1, overlap))
                    #
                    # if (k, 1, overlap) not in nodes[neighbor].end:
                    #     nodes[neighbor].end.add((k, 1, overlap))
    return edge_counts

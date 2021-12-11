#!/usr/bin/env python3
import sys
import os
import argparse
import logging
import multiprocessing as mp
from GFASubgraph.graph_io import write_gfa
from GFASubgraph.bfs import bfs
from GFASubgraph.Graph import Graph
from GFASubgraph.connected_components import all_components


def bfs_queue(graph, n, length, output_neighborhood):

    set_of_nodes = bfs(graph, n, length)
    graph.write_graph(set_of_nodes=set_of_nodes,
                      output_file=output_neighborhood, append=True)

def seq_size(graph, nodes):
    counter = 0
    for n in nodes:
        counter += graph.nodes[n].seq_len
    return counter


parser = argparse.ArgumentParser(description='Output neighborhood in Graph', add_help=True)
subparsers = parser.add_subparsers(help='Available subcommands', dest="subcommands")

parser._positionals.title = 'Subcommands'
parser._optionals.title = 'Global Arguments'

########################## general commands ###############################
parser.add_argument("-g", "--in_graph", metavar="GRAPH_PATH", dest="in_graph",
                    default=None, type=str, help="graph file path (GFA or VG)")

parser.add_argument("--log", dest="log_level", type=str, default="DEBUG",
                    help="The logging level [DEBUG, INFO, WARNING, ERROR, CRITICAL]")

########################## Output components ###############################
comp_parser = subparsers.add_parser('output_comps',
                                    help='Command for outputting each connected component in a separate GFA file')

comp_parser.add_argument("--output_dir", dest="output_dir", metavar="OUTPUT_DIR",
                        type=str, default=".", help="Output neighborhood file")

comp_parser.add_argument("-n", "--n-components", dest="n_comps", type=int, default=0,
                         help="If you want to output the n largest components in node size. Default: all")

comp_parser.add_argument("--seq-size", dest="seq_size", action="store_true", default=False,
                         help="If this argument given, then the components are sorted based on the seq size")

########################## BFS commands ###############################
bfs_parser = subparsers.add_parser('bfs', help='Command for separating neighborhood')

bfs_parser.add_argument("--start", dest="starting_nodes", metavar="START_NODES", type=str, nargs="+",
                        default=None, help="Give the starting node(s) for neighborhood extraction")

bfs_parser.add_argument("--cores", dest="cores", default=1, type=int,
                    help="number of threads")

bfs_parser.add_argument("--neighborhood_size", dest="bfs_len", metavar="SIZE", default=100,
                        type=int, help="With -s --start option, size of neighborhood to extract. Default: 100")

bfs_parser.add_argument("--output_neighborhood", dest="output_neighborhood", metavar="OUTPUT",
                        type=str, default=None, help="Output neighborhood file")

args = parser.parse_args()
# log_file = "log_" + str(time.clock_gettime(1)).split(".")[0] + ".log"
log_file = "log.log"

def main():
    if len(sys.argv) == 1:
        print("You did not provide any arguments\n"
              "Try to use -h or --help for help")
        sys.exit()


    if args.subcommands is None:
        print("Please provide a subcommand after the global commands")
        sys.exit(1)

    if args.in_graph is None:
        print("Please provide an input graph with -g, --in_graph")
        sys.exit(1)

    logging.basicConfig(filename=log_file, filemode='w',
                        format='[%(asctime)s] %(message)s',
                        level=getattr(logging, args.log_level.upper()))

    logging.info(" ".join(["argument given:"] + sys.argv))

    ####################### biggest component
    if args.subcommands == "output_comps":
        if not os.path.isdir(args.output_dir):
            os.mkdir(args.output_dir)
        else:
            logging.warning("Directory {} already exists, will add files to it anyway".format(args.output_dir))
        logging.info("Reading Graph...")

        graph = Graph(graph_file=args.in_graph)

        logging.info("Finding Biggest Component...")
        connected_comps = all_components(graph)
        if not connected_comps:
            logging.error("Something went wrong, there are no components returned")
            sys.exit()
        counter = 1
        logging.info("There are {} components in this graph".format(len(connected_comps)))
        logging.info("Writing Components...")
        if args.n_comps != 0:
            if args.seq_size:
                connected_comps.sort(key=lambda x: seq_size(graph, x), reverse=True)
            else:
                connected_comps.sort(key=lambda x: len(x), reverse=True)
        else:  # all comps
            args.n_comps = len(connected_comps)
        for cc in connected_comps[:args.n_comps]:
            output_file = args.output_dir + os.path.sep + "component{}.gfa".format(counter)
            # logging.info("Writing Component {}...".format(output_file))
            # print("I am here")
            write_gfa(graph, cc, output_file, False)
            counter += 1

        logging.info("Done...")

    ####################### BFS
    if args.subcommands == "bfs":
        if args.cores > os.cpu_count():
            print("Your system only have {} available cores at the moment".format(os.cpu_count()))
            sys.exit()

        if args.starting_nodes is not None:
            if args.bfs_len is not None:
                if args.output_neighborhood is not None:

                    logging.info("Reading Graph...")
                    graph = Graph(args.in_graph)

                    processes = []
                    for n in args.starting_nodes:

                        logging.info("extracting neighborhood around node {} and size of {}".format(n, args.bfs_len))
                        process = mp.Process(target=bfs_queue, args=(graph, n, args.bfs_len, args.output_neighborhood, ))
                        processes.append(process)

                        if len(processes) == args.cores:
                            for p in processes:
                                p.start()
                            for p in processes:
                                p.join()

                            processes = []

                    # leftovers
                    for p in processes:
                        p.start()
                    for p in processes:
                        p.join()

                    logging.info("Done...")
                else:
                    print("Error: Check log file")
                    logging.error("You need to give an output file name --output_neighborhood")
                    sys.exit()
            else:
                print("Error: Check log file")
                logging.error("You did not give the neighborhood size")
                sys.exit(1)
        else:
            print("Error: Check log file")
            logging.error("You did not give the starting node(s)")


if __name__ == "__main__":
    main()

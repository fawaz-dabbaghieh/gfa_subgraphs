#!/usr/bin/env python3
import sys
import os
import argparse
import logging
from GFASubgraph.bfs import bfs
from GFASubgraph.Graph import Graph

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
comp_parser = subparsers.add_parser('output_comps', help='Command for outputiing each connected component in a separate GFA file')

comp_parser.add_argument("--output_dir", dest="output_dir", metavar="OUTPUT_DIR",
                        type=str, default=".", help="Output neighborhood file")

########################## BFS commands ###############################
bfs_parser = subparsers.add_parser('bfs', help='Command for separating neighborhood')

bfs_parser.add_argument("--start", dest="starting_nodes", metavar="START_NODES", type=str, nargs="+",
                        default=None, help="Give the starting node(s) for neighborhood extraction")

bfs_parser.add_argument("--neighborhood_size", dest="bfs_len", metavar="SIZE", default=None,
                        type=int, help="With -s --start option, size of neighborhood to extract")

bfs_parser.add_argument("--output_neighborhood", dest="output_neighborhood", metavar="OUTPUT",
                        type=str, default=None, help="Output neighborhood file")


args = parser.parse_args()


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


    # log_file = "log_" + str(time.clock_gettime(1)).split(".")[0] + ".log"
    log_file = "log.log"

    logging.basicConfig(filename=log_file, filemode='w',
                        format='[%(asctime)s] %(message)s',
                        level=getattr(logging, args.log_level.upper()))

    logging.info(" ".join(["argument given:"] + sys.argv))

    ####################### biggest component
    if args.subcommands == "output_comps":
        if os.path.isdir(args.output_dir):
            logging.info("Reading Graph...")

            graph = Graph(graph_file=args.in_graph)

            logging.info("Finding Biggest Component...")
            all_comps = graph.output_components(args.output_dir)
            logging.info("Writing Components...")
            logging.info("Done...")

        else:
            print("Error: Check log file")
            logging.error("The directory {} does not exist".format(args.output_dir))


    ####################### BFS
    if args.subcommands == "bfs":
        if args.starting_nodes is not None:
            if args.bfs_len is not None:
                if args.output_neighborhood is not None:

                    logging.info("Reading Graph...")
                    graph = Graph(args.in_graph)


                    for n in args.starting_nodes:
                        logging.info("extracting neighborhood around node {}".format(n))
                        set_of_nodes = bfs(graph, n, args.bfs_len)
                        graph.write_graph(set_of_nodes=set_of_nodes,
                                          output_file=args.output_neighborhood, append=True)
                        logging.info("finished successfully...")
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

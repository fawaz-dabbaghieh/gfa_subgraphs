import argparse
import random
import logging
import pdb
import multiprocessing as mp
from GFASubgraph.main_helpers import *
from GFASubgraph.graph_io import write_gfa
from GFASubgraph.Graph import Graph
from GFASubgraph.connected_components import all_components
from GFASubgraph.x11_colors import color_list


parser = argparse.ArgumentParser(description='Output neighborhood in Graph', add_help=True)
subparsers = parser.add_subparsers(help='Available subcommands', dest="subcommands")

parser._positionals.title = 'Subcommands'
parser._optionals.title = 'Global Arguments'

########################## general commands ###############################
parser.add_argument("-g", "--in_graph", metavar="GRAPH_PATH", dest="in_graph",
                    default=None, type=str, help="graph file path (GFA or VG)")

parser.add_argument("--log_file", dest="log_file", type=str, default="log.log",
                    help="The name/path of the log file. Default: log.log")

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
                         help="If this argument given, then the components are sorted based on the seq size, "
                              "otherwise the number of nodes is used")

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


########################## Alignment subgraph ###############################
alignment_subgraph = subparsers.add_parser('alignment_subgraph',
                                    help='Command for outputting each connected component in a separate GFA file')

alignment_subgraph.add_argument("--input_gaf", dest="input_gaf", metavar="INPUT_GAF",
                                type=str, default=None, help="The input alignment gaf file")

alignment_subgraph.add_argument("--alignment_list", dest="alignment_list", type=str, default=None,
                                help="List of sequence names from the GAF file to separate, if not given "
                                     "all alignments in GAF will be considered")

alignment_subgraph.add_argument("--neighborhood_size", dest="bfs_len", metavar="SIZE", default=10,
                                type=int, help="the neighborhood size around each node in the alignment path, "
                                               "default: 10")

alignment_subgraph.add_argument("--prefix", dest="prefix", type=str, default="alignment_subgraph",
                                help="prefix for the output files")

args = parser.parse_args()

log_file = args.log_file

logging.basicConfig(filename=log_file, filemode='w',
                    format='[%(asctime)s] %(message)s',
                    level=getattr(logging, args.log_level.upper()))

logging.info(" ".join(["arguments given:"] + sys.argv))


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
    else:
        logging.info(f"Loading graph {args.in_graph}")
        graph = Graph(args.in_graph)

    ############################################## biggest component
    if args.subcommands == "output_comps":
        if not os.path.isdir(args.output_dir):
            os.mkdir(args.output_dir)
        else:
            logging.warning("Directory {} already exists, will add files to it anyway".format(args.output_dir))
        # logging.info("Reading Graph...")

        # graph = Graph(graph_file=args.in_graph)

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

    ############################################## BFS
    if args.subcommands == "bfs":
        if args.cores > os.cpu_count():
            print("Your system only have {} available cores at the moment".format(os.cpu_count()))
            sys.exit()

        if args.starting_nodes is not None:
            if args.bfs_len is not None:
                if args.output_neighborhood is not None:

                    # logging.info("Reading Graph...")
                    # graph = Graph(args.in_graph)

                    processes = []
                    queue = mp.Queue()
                    logging.info("Extracting neighborhoods...")
                    for n in args.starting_nodes:

                        process = mp.Process(target=bfs_queue, args=(graph, n, args.bfs_len, queue, ))
                        processes.append(process)

                        if len(processes) == args.cores:
                            for p in processes:
                                p.start()
                            n_sentinals = 0
                            while n_sentinals != len(processes):
                                nodes = queue.get()
                                if not nodes:
                                    n_sentinals += 1
                                else:
                                    # write to file
                                    graph.write_graph(set_of_nodes=nodes,  output_file=args.output_neighborhood,
                                                      append=True)
                            for p in processes:
                                p.join()

                            processes = []
                            queue = mp.Queue()
                            n_sentinals = 0

                    # leftovers
                    for p in processes:
                        p.start()
                    n_sentinals = 0
                    while n_sentinals != len(processes):
                        nodes = queue.get()
                        if not nodes:
                            n_sentinals += 1
                        else:
                            # write to file
                            graph.write_graph(set_of_nodes=nodes, output_file=args.output_neighborhood,
                                              append=True)
                    for p in processes:
                        p.join()

                    logging.info("Done...")
                else:
                    error("You need to give an output file name --output_neighborhood", args.log_file)
            else:
                error("You did not give the neighborhood size", args.log_file)
        else:
            error("You did not give the starting node(s)", args.log_file)

############################################## Alignment subgraph

    if args.subcommands == "alignment_subgraph":
        if not args.input_gaf:
            error("You need to provide an input GAF file", args.log_file)
        alignments = read_gaf(args.input_gaf, args.log_file)

        if not args.alignment_list:  # take all alignments
            to_extract = list(alignments.keys())
        else:
            to_extract = []
            with open(args.alignment_list, "r") as infile:
                for l in infile:
                    l = l.strip()
                    if l not in alignments:
                        logging.warning(f"The alignment {l} in {args.alignment_list} is not present in {args.input_gaf}")
                    else:
                        to_extract.append(l.strip())
        final_nodes = set()

        # finished preparing and now need to go through each alignment
        # and for each alignment go through each node and consider that as a start node
        # look at the neighbrohood around it
        # also outputting a CSV file with node names and coloring based on each alignment
        logging.info("Extracting the alignments...")
        with open(args.prefix + "colors.csv", "w") as out_csv:
            out_csv.write("Name,Colour,Alignment Name\n")

            for align_name in to_extract:
                color = random.choice(color_list)
                logging.info(f"Extracting the alignment {align_name} and will be coloured {color}")

                align_path = alignments[align_name]
                extract_alignments(align_path, graph, args.bfs_len, final_nodes)  # adds to final_nodes
                for n in align_path:  # I am only coloring the path
                    out_csv.write(f"{n},{color},{align_name}\n")

        out_graph = args.prefix + 'subgraph.gfa'
        logging.info(f"Writing the output graph {out_graph}")
        graph.write_graph(set_of_nodes=final_nodes, output_file=out_graph)


if __name__ == "__main__":
    main()

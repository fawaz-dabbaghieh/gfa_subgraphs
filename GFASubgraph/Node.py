import sys
import logging


class Node:
    __slots__ = ['id', 'seq', 'seq_len', 'start', 'end', 'visited', 'optional', 'chromosome']

    def __init__(self, identifier):
        self.id = identifier
        self.seq = ""
        self.seq_len = 0
        self.start = set()
        self.end = set()
        self.visited = False
        self.optional = ""
        self.chromosome = None

    def __sizeof__(self):
        size = self.id.__sizeof__() + self.seq_len.__sizeof__() + self.visited.__sizeof__()

        if len(self.start) == 0:
            size += self.start.__sizeof__()
        else:
            for i in self.start:
                size += sys.getsizeof(i)

        if len(self.end) == 0:
            size += self.end.__sizeof__()
        else:
            for i in self.end:
                size += sys.getsizeof(i)

        return size

    def neighbors(self):
        """
        Returns all adjacent nodes to self
        """

        neighbors = [x[0] for x in self.start] + [x[0] for x in self.end]
        return sorted(neighbors)

    def in_direction(self, node, direction):
        """
        returns true if node is a neighbor in that direction
        """
        # todo if I make start and end into dicts
        #   I can then easily check if the node in that direction by check if (node, 0) or (node, 1) in self.start
        #   same goes for self.end
        if direction == 0:
            if node in [x[0] for x in self.start]:
                return True
            return False
        else:
            if node in [x[0] for x in self.end]:
                return True
            return False

    def children(self, direction):
        """
        returns the children of a node in given direction
        """

        if direction == 0:
            return [x[0] for x in self.start]
        elif direction == 1:
            return [x[0] for x in self.end]
        else:
            raise Exception("Trying to access a wrong direction in node {}".format(self.id))

    # todo add functions to add edges to start and end that graph_io can then use
    #   should maybe have an option whether the edge is (neighbor, direction, overlap) or
    #   (neighbor, direction, overlap, count)
    def remove_from_start(self, neighbor, side, overlap):
        """
        remove the neighbor edge from the start going to side in neighbor
        """
        try:
            self.start.remove((neighbor, side, overlap))
        except KeyError:
            logging.warning(f"Could not remove edge {(neighbor, side, overlap)} from {self.id}'s start as it does not exist")

    def remove_from_end(self, neighbor, side, overlap):
        """
        remove the neighbor edge from the end going to side in neighbor
        """
        try:
            self.end.remove((neighbor, side, overlap))
        except KeyError:
            logging.warning(f"Could not remove edge {(neighbor, side, overlap)} from {self.id}'s end as it does not exist")

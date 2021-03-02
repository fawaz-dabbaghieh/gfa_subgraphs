import sys


class Node:
    __slots__ = ['id', 'seq', 'seq_len', 'start', 'end', 'visited', 'optional']

    def __init__(self, identifier, kc=0, km=0):
        self.id = identifier
        self.seq = ""
        self.seq_len = 0 
        self.start = []
        self.end = []
        self.visited = False
        self.optional = ""

    def __sizeof__(self):
        size = self.id.__sizeof__() + self.seq_len.__sizeof__() + self.visited.__sizeof__()

        if len(self.start) == 0:
            size += self.start.__sizeof__()
        else:
            for i in range(len(self.start)):
                size += sys.getsizeof(self.start[i])

        if len(self.end) == 0:
            size += self.end.__sizeof__()
        else:
            for i in range(len(self.end)):
                size += sys.getsizeof(self.end[i])

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

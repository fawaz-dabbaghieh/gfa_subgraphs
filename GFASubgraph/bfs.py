from collections import deque


def main_while_loop(graph, start_node, queue, visited, size):
    neighborhood = {start_node}
    if len(queue) == 0:
        queue.append(start_node)

    while len(neighborhood) <= size and len(queue) > 0:
        start = queue.popleft()

        if start not in neighborhood:
            neighborhood.add(start)

        visited.add(start)

        neighbors = graph[start].neighbors()

        for n in neighbors:
            if n not in visited and n not in queue:
                queue.append(n)

    return neighborhood


def bfs(graph, start_node, size):
    """
    Runs bfs and returns the neighborhood smaller than size
    Using only bfs was resulting in a one-sided neighborhood.
    So the neighborhood I was getting was mainly going from the start node
    into one direction because we have FIFO and it basically keeps going
    in that direction. So I decided to split check if have two possible directions
    From start, too look in both directions separately and add that to the whole neighborhood
    :param graph: A graph object from class Graph
    :param start_node: starting node for the BFS search
    :param size: size of the neighborhood to return
    """
    queue = deque()
    visited = set()
    if size > len(graph):
        size = len(graph) - 1

    queue.append(start_node)
    visited.add(start_node)
    neighbors = graph[start_node].neighbors()

    if len(neighbors) == 0:  # no neighbors
        return {start_node}

    neighborhood = main_while_loop(graph, start_node, queue, visited, size)

    return neighborhood

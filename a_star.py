import queue
import copy
import numpy as np
import container as cont

class balance():
    def __init__(self, init_state: cont.ship) -> None:
        self.init_state = copy.deepcopy(init_state)
        self.end_state = None

    def set_end_state(self,end_state: cont.ship) -> None:
        self.end_state = copy.deepcopy(end_state)
    
    def goal_test(self) -> bool:
        return self.init_state.is_balanced()

class node:
    def __init__(self, state: cont.ship, depth: int, distance: int) -> None:
        self.state = copy.deepcopy(state)
        self.depth = depth
        self.distance = distance

    def __lt__(self, other):
        if (self.distance + self.depth == other.distance + other.depth):
            return self.depth < other.depth
        else:
            return (self.distance + self.depth) < (other.distance + other.depth)

    def __gt__(self,other):
        return (self.distance + self.depth) > (other.distance + other.depth)

#Initializes a que with a single node
def make_que(node: node) -> queue.Queue:
    Que = queue.PriorityQueue()
    Que.put(node)
    return Que

#Creates a que node for the given state
def make_node(state, depth: int, distance: int) -> node:
    return node(state,depth,distance)

def heuristic(state: cont.ship) -> int:
    dist = 0
    return dist

def expand(node: node):
    ship = copy.deepcopy(node.state)
    containers = ship.containers
    dim = len(containers)
    dim2 = len(containers[0])
    children = []
    for column in range(dim2):
        (top_container,top_index) = ship.get_top(column)
        if (top_index != -1):
            for column2 in range(dim2):
                ship_temp = copy.deepcopy(ship)
                if (column2 != column):
                    if ship_temp.put_top(column2,top_index,column):
                        children.append(ship_temp)
    return children




    """ for i in range(dim2):
        for j in range(dim):
            if (containers[j][i] != -1):
                for k in range(dim2):
                    for l in range(dim):
                        if (k != i and l == 0 and containers[l][k] == -1):
                            ship_temp = copy.deepcopy(ship)
                            ship_temp.swap(j,i,l,k)
                            children.append(ship_temp)
                            break
                        elif (k != i and l != 0 and containers[l][k] != -1):
                            if (containers[l-1][k] == -1):
                                ship_temp = copy.deepcopy(ship)
                                ship_temp.swap(j,i,l-1,k)
                                children.append(ship_temp)
                                break
                break """
    return children

#Que's the children passed in to the que
def queing_function(nodes: queue.PriorityQueue,children,depth: int,visited_nodes: set, trace) -> queue.PriorityQueue:
    for child in children:
        tuple_state = tuple(map(tuple,child))
        if not visited_nodes.__contains__(tuple_state):
            new_node = node(child,depth+1,0)
            nodes.put(new_node)
            visited_nodes.add(tuple_state)
    if trace:
        print(f"The best state to expand with g(n) = {nodes.queue[0].depth} and h(n) = {nodes.queue[0].distance} is \n {np.matrix(nodes.queue[0].state)}\n")
    return nodes

#Our main search; que's based on the passed in queing function
def search(problem,queing_function,trace):
    nodes = make_que(make_node(problem.init_state,0,0))
    i = 0
    max_que = 0
    visited_nodes = {tuple(map(tuple,problem.init_state))}
    while not nodes.empty():
        i = i + 1
        max_que = max(max_que,nodes.qsize())
        node = nodes.get()
        if problem.goal_test(node.state):
            return (node,node.depth,max_que,i)
        nodes = queing_function(nodes,expand(node),node.depth,visited_nodes,trace)
    raise Exception("Search terminated in failure")
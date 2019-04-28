from mapa import Map 
from utils import calc_distance
from enums import DistanceMethod, Direction, ALL_DIRECTIONS
from queue import PriorityQueue
# The cost for actions is defined by the following:
GHOST_COST = 50
# TODO: Change cost of boosts to depend on number of ghosts maybe?
BOOST_COST = 10
ENERGY_COST = 10
# TODO: Maybe change this metric?
ZOMBIE_COST = ENERGY_COST/2
EMPTY_COST = ENERGY_COST*2

class SearchNode:
    def __init__(self,state,parent,acc_cost=None,h_cost=None, direction=None):
        self.state = state
        self.parent = parent
        self.acc_cost = acc_cost
        self.h_cost = h_cost
        self.direction = direction
    def __lt__(self, other):
        return self.acc_cost + self.h_cost < other.acc_cost + other.h_cost
    def __le__(self, other):
        return self.acc_cost + self.h_cost <= other.acc_cost + other.h_cost
    def __gt__(self, other):
        return self.acc_cost + self.h_cost > other.acc_cost + other.h_cost
    def __ge__(self, other):
        return self.acc_cost + self.h_cost >= other.acc_cost + other.h_cost
    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + "," + str(self.direction) + ")"
    def __repr__(self):
        return str(self)

class PacmanPathFinder:
    """
    Implements A* star based path finding.
    Based on code from Luis Seabra Lopes, provided for the tp1
    """
    def __init__(self, level_map : Map):
        """
        Constructor.
                                                                                                                                                
        """        
        self.level_map = level_map
        self.energy_pos = []
        self.boost_pos = []
        self.ghost_pos = []
    def updateFinder(self,energy_pos :list, boost_pos : list, ghost_pos : list):
        self.energy_pos = energy_pos
        self.boost_pos = boost_pos
        self.ghost_pos = ghost_pos

    def get_path(self,node):
        if node.parent == None:
            return [node]
        path = self.get_path(node.parent)
        path += [node]
        return(path)

    def result(self, cur_pos, direction):
        # The result of moving in a given direction is already provided
        # by the map
        return self.level_map.calc_pos(cur_pos, direction)

    def actions(self, position):
        # Our possible actions are only those that don't lead us into walls
        # or into ghosts that aren't zombies
        position = (position[0], position[1])
        valid_dirs = []
        for direction in ALL_DIRECTIONS:
            # if it's a wall, then next_pos will be initial position
            next_x, next_y = self.level_map.calc_pos(position, direction)
            next_pos = (next_x, next_y)
            if position != next_pos:
                # if there are no ghosts, then all directions
                # that aren't into walls are valid
                if not self.ghost_pos:
                    valid_dirs += [direction]
                # otherwise, if there are ghosts
                else:
                    for ghost in self.ghost_pos:
                        # TODO: Refactoring potential ? 
                        # TODO: we could check if the ghost's position is in a radius
                        # TODO: Near the next position
                        g_pos = (ghost[0][0], ghost[0][1])
                        # if we're moving towards a ghost
                        if next_pos == g_pos:
                            # and he's a zombie, then that's a valid direction
                            dist = calc_distance(pos1=next_pos, pos2=g_pos,dist_type=DistanceMethod.MANHATTAN)
                            if ghost[1] and dist <= ghost[2]/2:
                                valid_dirs +=[direction]
                        # if we're not moving towards him, then that's a valid direction
                        else:
                            valid_dirs +=[direction]
        # Edge case
        # TODO: Maybe uncomment? Needs testing
        #if not valid_dirs:
            #valid_dirs = [Direction.UP]
        return list(set(valid_dirs))

    def heuristic(self, cur_pos, goal_pos):
        """
        Using Manhattan distance, as per
        http://www.rahulashok.net/images/learningPortfolio/paper1.pdf
        """
        return calc_distance(cur_pos, goal_pos, dist_type=DistanceMethod.MANHATTAN)
    
    def cost(self, cur_pos, direction):
        next_pos = self.level_map.calc_pos(cur_pos, direction)
        # Note: We're assuming the map returns a non-wall position
        #assert not self.level_map.is_wall(next_pos)
        # Check if it's an energy:
        if next_pos in self.energy_pos:
            return ENERGY_COST
        # Otherwise, we need to iterate over the ghosts
        for ghost in self.ghost_pos:
            # check the ghosts coordinates
            if ghost[0][0] == next_pos[0] and  ghost[0][1] == next_pos[1]:
                # If the ghost is a zombie, then it sohuld have a lower cost
                return ZOMBIE_COST if ghost[1] else GHOST_COST
        # If it's not in the ghosts, then we check if it's in the list of boosts
        if next_pos in self.boost_pos:
            return BOOST_COST
        # Otherwise it's an empty position
        return EMPTY_COST
    
    def search(self, start, goal):
        """
        Searches a path, using A* strategy.
        """
        open_nodes = PriorityQueue()
        # using PriorityQueue allows us to save on always having to sort
        open_nodes.put((0,SearchNode(start, None, acc_cost=0,h_cost=0)))
        # Set of the opened states
        gen_nodes = {(start[0],start[1])}
        n_gen_nodes = 1
        while not open_nodes.empty():
            # get the one with the lowest cost
            node = open_nodes.get()[1]
            # If we found the solution, return the path
            if (node.state[0] == goal[0] and node.state[1] == goal[1]) or n_gen_nodes > 2500:
                # without the start node
                return self.get_path(node)[1:]
            
            # For our position, check in which directions we can move
            for action in self.actions(node.state):
                # Find the state we reach following specific action
                new_position = self.result(node.state, action)
                # check if we already checked that state
                if new_position in gen_nodes:
                    # if we did, we don't need to create a node for it
                    continue
                # Find out the new cost
                action_cost =  self.cost(node.state, action)
                acc_cost = node.acc_cost + action_cost
                h_cost = self.heuristic(new_position, goal)
                new_node = SearchNode(new_position, node, acc_cost=acc_cost, h_cost=h_cost, direction=action)
                # Add to the queue
                open_nodes.put((acc_cost + h_cost, new_node))
                # and to the list of opened states
                gen_nodes.add(new_position)
                n_gen_nodes += 1
        return None

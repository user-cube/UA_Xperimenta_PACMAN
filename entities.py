import math
from utils import calc_distance, calc_angle, closest_ghost, closest_point, directions_from_angle
from enums import DistanceMethod, TargetType, Direction
from pathfinding import PacmanPathFinder
from mapa import Map

def reverse_directions(dirs):
    rv = []
    for x in dirs:
        if x == "w":
            rv.append("s")
        elif x == "a":
            rv.append("d")
        elif x == "s":
            rv.append("w")
        else:
            rv.append("a")
    return rv

class PlayerAgent:
    """

    """

    def __init__(self, level: Map, game_settings, **kwargs):
        """

        :param level:
        :param game_settings:
        :param kwargs: additional properties
        """

        MAX_CHASE_DIST = 13
        MIN_RUN_DIST = 7

        self.MAX_STEPS = game_settings["timeout"]
        self.MAX_LIVES = game_settings["lives"]
        self.MAX_CHASE_DISTANCE = kwargs.pop("chase_dist", MAX_CHASE_DIST)
        """chase_dist - Maximum distance (in blocks) ghosts can be for our agent to chase. Defaults to {}""".format(
            MAX_CHASE_DIST
        )
        self.MIN_RUN_DISTANCE = kwargs.pop("run_dist", MIN_RUN_DIST)
        """run_dist - Minimum distance a ghost can be for our agent to decide to run away from it. Defaults to {}""".format(
            MIN_RUN_DIST
        )
        self._lives = self.MAX_LIVES
        self._level = level
        self._prev_position = level.pacman_spawn
        self._next_move = "d"
        self._state = {}
        self._prev_state = {}
        self._step_counter = 0
        self._dead = False
        self._buffer_pos = []
        self._avoid_list = []

    @property
    def dead(self):
        return self._dead

    @property
    def state(self):
        return self._state

    @property
    def step(self):
        return self._step_counter

    @property
    def lives(self):
        return self._lives

    def next_move(self):
        """
        """
        return self._next_move

    def update_state(self, new_state):
        """
        """

        # If we're dead, we can just ignore the state change
        # Although this probably shouldn't happen
        # since check is done before state being updated

        if new_state.get("lives", self._lives) == 0:
            self._lives = 0
            self._dead = True
            return

        # storing current state for debugging
        self._state = new_state
        self._lives = self.state.get("lives")
        self._step_counter = self.state["step"]
        booll = True
        if self.step == 0 and len(self.state["ghosts"]) > 0:
            booll = True
            ghost_x, ghost_y = self.state["ghosts"][0][0]
            self._avoid_list = [
                [ghost_x, ghost_y + 1],
                [ghost_x, ghost_y - 1],
                [ghost_x + 1, ghost_y],
                [ghost_x - 1, ghost_y],
            ]
        # current position by the server
        (cur_pos) = self.state["pacman"]

        if booll:
            dirs = self.directions(boost_list=self.state["boost"], list_not=self._avoid_list)
        else:
            dirs = self.directions(list_not=self._avoid_list)
        score = self.scores(dirs=dirs)
        idx = score.index(max(score))
        if self.step != 0:
            # change our move
            self._next_move = dirs[idx]
        self._step_counter += 1
        # update our position buffer
        self.update_buffer()
        # determine the position we'll be by moving in the next direction
        next_pos = self._level.calc_pos(cur_pos, self._next_move)
        # update our position
        self._prev_position = next_pos

        # storing previous for debugging
        self._prev_state = self.state

    def directions(self, boost_list=None, list_not=[]):
        """
        Returns the possible directions we should move to, ordered by priority
        :param g_is_zombie:
        :param ghost_pos:
        :param boost_list:
        :return:
        """
        ghosts = self.state["ghosts"]
        # default values
        nearby_ghost = None
        chasing_ghost = False
        nearby_ghost_dist = self.MAX_CHASE_DISTANCE + 1
        # if there any ghosts
        if ghosts != []:
            nearby_ghost, nearby_ghost_dist = closest_ghost(self._prev_position, ghosts, avoid_list=list_not)
        # if the closest ghost isn't a zombie, we chase the energy
        if nearby_ghost is None or not nearby_ghost[1]:
            energies_points = self.state["energy"]
            target, target_dist = closest_point(self._prev_position, energies_points)
        # otherwise, we need chase the ghost
        else:
            # if he's within running distance
            # that means, he's not too far out
            # and he won't time out
            if nearby_ghost_dist <= self.MAX_CHASE_DISTANCE \
                and nearby_ghost_dist < nearby_ghost[2] / 2:
                target, target_dist = nearby_ghost[0], nearby_ghost_dist
                chasing_ghost = True
            # otherwise, just chase the energy
            else:
                energies_points = self.state["energy"]
                target, target_dist = closest_point(
                    self._prev_position, energies_points
                )
        theta = calc_angle(self._prev_position, target)
        # if he's chasing the ghost
        # or, despite not chasing, the nearest ghost is too far away
        # we just go get the ghost/energy
        # TODO: make sure to not chase into the box
        if chasing_ghost or nearby_ghost_dist > self.MIN_RUN_DISTANCE:
            dirs = directions_from_angle(theta)
        # otherwise, the ghost is too close, so we need to run away
        else:
            ghost_theta = calc_angle(self._prev_position, nearby_ghost[0])
            dirs_to_ghost = directions_from_angle(ghost_theta)
            dirs = reverse_directions(dirs_to_ghost)
            # # if the ghost is within the range of the energy, we run awy
            # dirs_to_energy = directions_from_angle(theta)
            # print("Dirs to energy", dirs_to_energy)
            # print("Angle to energy", theta)
            # print("Angle to ghost", ghost_theta)
            # print("Dirs to ghost", dirs_to_ghost)
            # # we try to avoid the ghost
            # if dirs_to_energy[0] == dirs_to_ghost[0]:
            #     dirs = dirs_to_energy[1:] + dirs_to_energy[:1]
            # # otherwise, we just keep chasing the energy
            # else:
            #     dirs = dirs_to_energy
        # Debug
        return dirs

    def update_buffer(self, buff_size=1000):
        n_pos = self._level.calc_pos(self._prev_position, self._next_move)
        op = [x for x in self._buffer_pos if x[0] == n_pos]
        if len(op) == 0:
            self._buffer_pos.append((n_pos, 1))
        else:
            self._buffer_pos.remove(op[0])
            self._buffer_pos.append((op[0][0], op[0][1] + 1.0))
        self._buffer_pos.sort(key=lambda x: x[1], reverse=True)

        if len(self._buffer_pos) > buff_size:
            self._buffer_pos = self._buffer_pos[1:]

    def scores(self, dirs):
        score_d = [0.35, 0.35, 0.35, 0.35]
        score_b = []

        for d in dirs:
            n_pos = self._level.calc_pos(self._prev_position, d)
            c = 0
            if n_pos == self._prev_position:
                # WALL
                score_b.append(0.0)
            elif n_pos in self._avoid_list:
                score_b.append(0.0)
            else:
                if len(self._buffer_pos) == 0:
                    score_b.append(1.0)
                else:

                    m = max([x[1] for x in self._buffer_pos])
                    op = [x for x in self._buffer_pos if x[0] == n_pos]
                    if len(op) == 0:
                        score_b.append(1.0)
                    else:
                        c += 0.0
                        score_b.append(1.0 - (op[0][1] / m + c))
        ret = [x * y for x, y in zip(*([score_d, score_b]))]
        return ret


class RefactoredAgent(PlayerAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._score = 0
        self._energies = []
        self._ghosts = []
        self._boosts = []
        self._pathfinder : PacmanPathFinder = PacmanPathFinder(level_map=self._level)
    def update_state(self, new_state):
        # If we're dead, we can just ignore the state change
        # Although this probably shouldn't happen
        # since check is done before state being updated

        if new_state.get("lives", self._lives) == 0:
            self._lives = 0
            self._dead = True
            return

        # storing current state for debugging
        # TODO: no debug is being done (currently) with with state, remove?
        #print(new_state, "Ok")
        self._state = new_state
        self._score = self._state.get("score",0)
        self._lives = self._state.get("lives", 0)
        self._step_counter = self._state["step"]
        self._energies = self._state.get("energy",[])
        #print(self._energies, "ok")
        self._ghosts = self._state.get("ghosts",[])
        self._boosts = self._state.get("boost",[])
        # update the pathfinder
        self._pathfinder.updateFinder(self._energies, self._boosts, self._ghosts)

        self._prev_position = self.state['pacman']
        
        # We need to decide which target to chase
        # So, we need to find which target we should chase
        # 1 - First, we're going to assign scores (read: priorities) to each point
        
        energy_scores = self.build_scores_energy(self._energies)
        # 2 - Then we're going to do the same for ghosts
        ghost_scores = self.build_scores_ghosts(self._ghosts)
        # 3 - Then we're going to do the same for boosts
        boosts_scores = self.build_scores_boosts(self._boosts)
        # 4 - After that, we're going to choose the one with the best score
        best_target, target_type = self.find_best_target(energy_scores=energy_scores, ghosts_scores=ghost_scores, boosts_scores=boosts_scores)        # 5 - Finally, we're going to build the path for it
        # TODO: Finish implementation
        directions = self.find_path(start=self._prev_position, target=best_target[1], target_type=target_type)
        #directions1 = self.find_path(start=self.state['pacman'], target=best_target[1], target_type=target_type)
                
        #print(directions, directions1)
        # 6 - And lastly, we just make our next move to be the first of the path taken
        # TODO: Potentially keep track of previous target? and do some logic on next_move taken?
        # TODO: need to return str due to json encoding + checking map
        self._next_move = str(directions[0])
        # Logging Info
        """ print(
            (
                ""
                + "Step - {}\n"
                + "Lives - {}\n"
                + "Score - {}\n"
                + "Pacman Prev Position - {}\n"
                + "Energy - {}\n"
                + "Boosts - {}\n"
                + "Ghosts - {}\n"
                + "Target - {} - {}\n"
                + "Moving - {} -> {}\n"
                + "Directions - {}\n"
            ).format(
                self._step_counter,
                self._lives,
                self._score,
                self._prev_position,
                self._energies,
                self._boosts,
                self._ghosts,
                best_target,
                target_type,
                self.state['pacman'],
                best_target[1],
                directions
            )
        ) """
        # and update our position 
        #self._prev_position = self.state['pacman']
        # TODO: No debug is being done (currently) with prev state, remove?
        self._prev_state = self.state
    
    def find_path(self, start: tuple, target:tuple, target_type=TargetType.NO_TARGET):
        """
            Finds the best target from the list of energies, ghosts, and boosts
            
            Parameters
            -----------
            start: Tuple
                Coordinates of the starting point
            target: Tuple
                Coordinates of the target
            target_type: :class:`TargetType`
                Type of the target. Defaults to TargetType.NO_TARGET
            Returns
            --------
            """
        valid_path = self._pathfinder.search(start, target)
        #breakpoint()
        # By default, if there's no path
        # we just move upwards
        if not valid_path:
            return [Direction.UP]
        # otherwise, just return the directions for each of 
        lista = [node.direction for node in valid_path]
        if len(lista)>2:
            lista = lista[0:2]
        return lista


    def build_scores_energy(self, energy_list : list) :
        """
        Builds the scores for the list of energies
        
        Parameters
        -----------
        energy_list: List[Tuple]
            List with the coordinates of the energies. Assumes the following format:
            [(x,y)...]
        Returns
        --------
        list_scores: List[Tuple]
            List with the scores and coordinates. Has the following format:
            [(score,(x,y)),...]
        """
        # TODO: Instead of passing the list as arguments, use the attribute? To Discuss

        # edge case
        if energy_list is []:
            return []    
        # The current metric for scoring the energies is
        score_calc = lambda dist: 1 / ((dist * dist)+1)
        # TODO: Maybe turn this into List comprehension?
        list_scores = []
        for energy in energy_list:
            # Calculate the distance, and append the energy, along with its score
            list_scores += [(
                score_calc(calc_distance(pos1=self._prev_position, pos2=energy, dist_type=DistanceMethod.MANHATTAN)),
                energy
            )]
        return list_scores

    def build_scores_ghosts(self,ghost_list : list):
        """
        Builds the scores for the list of ghosts
        
        Parameters
        -----------
        ghost_list: List[List]
            List with the ghosts. Assumes the following format:
            [[(x,y),zombie,steps_timeout],...]
        Returns
        --------
        list_scores: List[Tuple]
            List with the ghosts' scores, coordinates, and original ghost representation. Has the following format:
            [(score,(x,y), [(x,y),zombie,steps_timeout]),...]
        """
        # TODO: Instead of passing the list as arguments, use the attribute? To Discuss

        # edge case
        if ghost_list is []:
            return []
        # The current metric for scoring the ghosts is 
        score_calc = lambda dist, zombie, timeout:  2*(1/((dist*dist)+1)) if zombie and dist <= timeout/2 else -1
        # We'll value more in the case the ghost is chaseable.
        # Being chaseable means is a zombie and the distance he's at is less than the number of steps it'd take us to reach him
        # TODO: Maybe turn this into List comprehension?
        list_scores = []
        for ghost in ghost_list:
            list_scores += [(
                score_calc(
                    calc_distance(pos1=self._prev_position, pos2=ghost[0], dist_type=DistanceMethod.MANHATTAN),
                    ghost[1],
                    ghost[2]
                ),
                ghost[0],
                ghost
            )]
        return list_scores
    
    def build_scores_boosts(self, boost_list : list):
        """
        Builds the scores for the list of boosts
        
        Parameters
        -----------
        boost_list: List[Tuple]
            List with the boosts. Assumes the following format:
            [(x,y),...]
        Returns
        --------
        list_scores: List[Tuple]
            List with the boosts' scores and coordinates. Has the following format:
            [(score,(x,y)),...]
        """
        # TODO: Instead of passing the list as arguments, use the attribute? To Discuss

        # edge case
        if boost_list is []:
            return []
        # The current metric for scoring the boosts is 
        # TODO: Maybe adjust to prioritize boosts if number of energies is low?/ghosts are nearby
        # TODO: Note on above: maybe that prioritization should be post scores?
        score_calc = lambda dist:  1/((dist*dist)+1)
        list_scores = []
        for boost in boost_list:
            list_scores += [(
                score_calc(
                    calc_distance(pos1=self._prev_position, pos2=boost, dist_type=DistanceMethod.MANHATTAN)
                ),
                boost
            )]
        return list_scores
        
    def find_best_target(self, energy_scores : list =[],ghosts_scores: list=[], boosts_scores: list=[]):
        """
        Finds the best target from the list of energies, ghosts, and boosts
        
        Parameters
        -----------
        energy_scores: List[Tuple]
            List with the scores and coordinates of energies. Assumes the following format:
            [(score, (x,y)), ...]
        ghost_scores: List[Tuple]
            List with the ghosts' scores, coordinates, and their original representation. Assumes the following format:
            [(score,(x,y),ghost), ...]
        boosts_scores: List[Tuple]
            List with the scores and coordinates of boosts. Assumes the following format:
            [(score, (x,y)),...]
        Returns
        --------
        best_target: Tuple
            The target with best score. Has (AT LEAST) the following format:
            (score, (x,y), ...)
            Can contain additional values [e.g, in the case of ghosts].
            Defaults to (-1, pacman_pos) if all the lists are empty.

        target_type: :class:`TargetType`
            Type of the target. Defaults to TargetType.NO_TARGET
        """

        # Handling the edge cases, requires us to check whether lists are empty or not
        # So what we'll do is fill it with a default score, so max function still works
        # And have the default target as some NullObject-representation
        # Usually, it should never happen
        # Default score
        best_target  = (-1, self._prev_position)
        # and target type
        target_type = TargetType.NO_TARGET

        # TODO: whole code of function is refactor-able
        if not energy_scores:
            energy_scores = [best_target]
        if not ghosts_scores:
            ghosts_scores = [best_target]
        if not boosts_scores:
            boosts_scores = [best_target]
        
        # Check scores for energies, updating target and score if needed
        best_energy = max(energy_scores)
        if best_energy[0] > best_target[0]:
            #print("ENERGY", best_energy[0], max(ghosts_scores)[0], max(boosts_scores)[0])
            best_target = best_energy
            target_type = TargetType.ENERGY

        # Check scores for ghosts, updating target and score if needed
        best_ghost = max(ghosts_scores)
        if best_ghost[0] > best_target[0]:
            #print("GHOST")
            best_target = best_ghost
            target_type = TargetType.GHOST
        
        # Check scores for boosts
        best_boost = max(boosts_scores)
        if best_boost[0] > best_target[0]:
            #print("BOOST")
            best_target = best_boost
            target_type = TargetType.BOOST
        return best_target, target_type
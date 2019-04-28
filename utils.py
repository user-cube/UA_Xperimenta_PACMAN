from typing import List
import math
from enums import DistanceMethod, TargetType

def directions_from_angle(theta: int):
    """
    Function that gets directions from angles.
    Theta values are assumed to be between [-180, 180]
    positive theta is clockwise, negative theta is counter-clockwise
    Note: We're going to we are rotated 45º clockwise
    """
    #  1st quadrant
    if theta >= 45 and theta < 135:
        # 1st octant
        if theta <= 90:
            dirs = ["s", "d", "a", "w"]
        # 2nd octant
        else:
            dirs = ["s", "a", "d", "w"]
    # 3rd quadrant
    elif theta >= -135 and theta < -45:
        # 5th octant
        if theta >= -90:
            dirs = ["w", "d", "a", "s"]
        # 6th octant
        else:
            dirs = ["w", "a", "d", "s"]
    # 3rd octant
    elif theta >= 135:
        dirs = ["a", "s", "w", "d"]
    # 4th octant
    elif theta < -135:
        dirs = ["a", "w", "s", "d"]
    # 8th octant
    elif theta < 45:
        dirs = ["d", "s", "w", "a"]
    # 7th octant
    else:
        dirs = ["d", "w", "s", "a"]
    return dirs


def calc_angle(pos1: tuple, pos2: tuple):
    """
    Calculates the angle between two points
    
    Parameters
    -----------
    pos1: tuple 
        Coordinates of the first point
    pos2: tuple
        Coordinates of the second point
    Returns
    --------
    theta: int
        The angle (in degrees) between two points
    """
    x1, y1 = pos1
    x2, y2 = pos2
    theta = round(math.degrees(math.atan2(y2 - y1, x2 - x1)))
    return theta

def calc_distance(pos1 : tuple, pos2 : tuple, dist_type: DistanceMethod = DistanceMethod.EUCLIDEAN):
    """
    Calculates the distance between two points
    
    Parameters
    -----------
    pos1: tuple 
        Coordinates of the first point
    pos2: tuple
        Coordinatesof the second point
    dist_type: Optional[`DistanceMethod`]
        Distance method to use. Defaults to Euclidean.
    Returns
    --------
    dist: int
        The angle (in degrees) between two points
    Raises
    ------
    ValueError
        Invalid/Not implemented method chosen.
    """
    x1, y1 = pos1
    x2, y2 = pos2
    if dist_type== DistanceMethod.EUCLIDEAN:
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    elif dist_type== DistanceMethod.MANHATTAN:
        return abs(x1 - x2) + abs(y1 - y2)
    else:
        raise ValueError("Invalid distance method!")

def closest_point(start: tuple, points_list: List[tuple]):
    """
    Finds the closest point to the start point provided.
    If the list is empty, returns the start point
    :param start:
    :param points_list:
    :return: the point and the distance to that point
    """
    if points_list == []:
        return start, calc_distance(start,(0, 0),DistanceMethod.MANHATTAN)
    min_elem = points_list[0]
    min_dist = calc_distance(start,min_elem,DistanceMethod.MANHATTAN)
    for elem in points_list[1:]:
        curr_dist = calc_distance(start,elem,DistanceMethod.MANHATTAN)
        if curr_dist < min_dist:
            min_dist = curr_dist
            min_elem = elem
    return (min_elem, min_dist)




def closest_ghost(start: tuple, ghost_list: list, avoid_list: list = []):
    """
    Finds the closest ghost to the start point provided.

    Parameters
    -----------
    start:
        Starting point
    ghost_list: List[tuple]
        List of ghosts. 
        Each ghost is assumed to have the following structure:
        `[(x,y), is_zombie: bool, zombie_timeout: int]`
        If the list is empty, returns `start` as the "closest ghost" and 0 as the distance
    avoid_list:
        List of ghosts to avoid.

    Returns
    --------
    A tuple with the ghost and the distance to it.
    If the list is empty, returns a tuple with a "ghost-like" list and 0 for the distance `([start, False, -1], 0)` 
    in order to avoid unexpected code breaking (and needlesly handling that case in client code)
    """
    if ghost_list == []:
        return ([start,False, -1], 0)
    min_g = ghost_list[0]
    min_g_dist = calc_distance(start, min_g[0], DistanceMethod.MANHATTAN)
    for g in ghost_list[1:]:
        curr_g_dis = calc_distance(start, g[0], DistanceMethod.MANHATTAN)
        if curr_g_dis < min_g_dist and g not in avoid_list:
            min_g = g
            min_g_dist = curr_g_dis
    return (min_g, min_g_dist)
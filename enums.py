from enum import Enum

class DistanceMethod(Enum):
    EUCLIDEAN = 0
    MANHATTAN = 1
    def __str__(self):
        return self.name

class TargetType(Enum):
    NO_TARGET = -1
    ENERGY = 0
    BOOST = 1
    GHOST = 2
    def __str__(self):
        return self.name

# TODO: We could potentially declare this as a static method?
ALL_DIRECTIONS = ["w", "a","s","d"]
class Direction(Enum):
    UP = "w"
    LEFT = "a"
    DOWN = "s"
    RIGHT = "d"
    def __str__(self):
        return self.value
    def __repr__(self):
        return self.value

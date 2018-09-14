"""
Core classes shared among the other generic gridworld modules.
"""

class ThingTypes:
    AGENT = 'AGENT'
    ACTOR = 'ACTOR'
    CELL = 'CELL'
    OBJECT = 'OBJECT'
    
class Outcomes:
    NOT_DONE = 0
    DONE = 1
    
class _Direction:
    def __init__(self, name, dx, dy, opposite = None):
        self._name = name
        self._dx = dx
        self._dy = dy
        self._opposite = opposite

    @property
    def name(self):
        return self._name

    @property
    def dx(self):
        return self._dx

    @property
    def dy(self):
        return self._dy

    @property
    def opposite(self):
        return self._opposite

    def coordinates(self, x, y):
        return (x + self._dx, y + self._dy)
    
    def next_cell(self, grid, x, y):
        return grid[self.coordindates(x, y)]

class Directions:
    NORTH = _Direction("NORTH", 0, 1)
    EAST = _Direction("EAST", 1, 0)
    SOUTH = _Direction("SOUTH", 0, -1, NORTH)
    WEST = _Direction("WEST", -1, 0, EAST)

    ALL = (NORTH, EAST, SOUTH, WEST)

Directions.NORTH._opposite = Directions.SOUTH
Directions.EAST._opposite = Directions.WEST


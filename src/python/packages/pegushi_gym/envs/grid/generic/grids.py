"""
Cell grids for generic gridworlds
"""

from pegushi_gym.envs.grid.generic.cells import LimboCell

class _Direction:
    def __init__(self, name, dx, dy):
        self._name = name
        self._dx = dx
        self._dy = dy

    @property
    def name(self):
        return self._name

    @property
    def dx(self):
        return self._dx

    @property
    def dy(self):
        return self._dy

    def coordinates(self, x, y):
        return (x + self._dx, y + self._dy)
    
    def next_cell(self, grid, x, y):
        return grid[self.coordindates(x, y)]
        
class Grid:
    """Basic grid implementation for generic gridworld."""
    def __init__(self, cells, boundary, limbo = LimboCell()):
        """
  * cells:     np.ndarray; Cell grid, organized with rows along the y-axis and
               columns along the x-axis.  Values need to implement the "Cell"
               concept.
  * boundary:  cells.Cell or equivalent; Cell that surrounds the grid.
  * limbo:     cells.Cell or equivalent; Cell that represents "nowhere"
               Objects are placed here when they aren't located on the grid.
"""
        self._cells = cells
        self._boundary = boundary
        self._limbo = limbo

    @property
    def min_x(self):
        return 0

    @property
    def max_x(self):
        return self._cells.shape[1]

    @property
    def min_y(self):
        return 0

    @property:
    def max_y(self):
        return self._cells.shape[0]

    @property
    def width(self):
        return self._cells.shape[1]

    @property
    def height(self):
        return self._cells.shape[0]

    @property
    def bounds(self):
        return ((0, 0), self._cells.shape)

    @property
    def limbo(self):
        return self._limbo

    def in_bounds(self, x, y):
        return (x >= 0) and (x < self._cells.shape[1]) and (y >= 0) and \
               (y < self._cells.shape[0])

    def __getitem__(self, coordinates):
        if self.in_bounds(*coordinates):
            return self._cells[coordinates]
        else:
            return self._boundary
        

"""
Cell grids for generic gridworlds
"""

from pegushi_gym.envs.grid.generic.cells import LimboCell
import numpy as np

class Grid:
    """Basic grid implementation for generic gridworld."""
    def __init__(self, cells, boundary, limbo = LimboCell()):
        """
  * cells:     np.ndarray; Cell grid, organized with rows along the y-axis and
               columns along the x-axis.  The cell at (0, 0) is the southeast
               corner.  Values need to implement the "Cell" concept.
  * boundary:  cells.Cell or equivalent; Cell that surrounds the grid.
  * limbo:     cells.Cell or equivalent; Cell that represents "nowhere"
               Objects are placed here when they aren't located on the grid.
"""
        self._cells = cells
        self._boundary = boundary
        self._limbo = limbo

        for c in cells:
            c.set_grid(self)
        self._boundary.set_grid(self)
        self._limbo.set_grid(self)
            

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
            return self._cells[coordinates[1], coordinates[0]]
        else:
            return self._boundary

    @classmethod
    def homogenous(cls, width, height, cell, boundary, limbo = LimboCell()):
        cells = np.ndarray((height, width), dtype = np.object)
        for y in xrange(0, layout.shape[0]):
            for x in xrange(0, layout.shape[1]):
                cells[y, x] = cell.clone(x, y)
        return cls(cells, boundary, limbo)

    @classmethod
    def from_layout(cls, layout, create_cell, boundary, limbo = LimboCell()):
        cells = np.ndarray(layout.shape, dtype = np.object)
        for y in xrange(0, layout.shape[0]):
            for x in xrange(0, layout.shape[1]):
                cells[y, x] = create_cell(layout[y, x], x, y)
        return cls(cells, boundary, limbo)


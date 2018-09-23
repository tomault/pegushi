"""
Implementation of renderers for the generic grid environment
"""

class StandardAnsiGridRenderer:
    def __init__(self, tile_map):
        self._tile_map = tile_map
    
    def render(self, state):
        # Return a string with as many lines as the grid has rows plus two
        # (for the border) and as many columns as the grid has columns
        # plus two for the border)
        grid = state.grid
        tile_cache = { }

        rows = xrange(grid.max_y + 1, grid.min_y - 2, -1)
        return '\n'.join(self._draw_row(grid, y, tile_cache) for y in rows)

    def close(self):
        pass  # Does nothing

    def _draw_row(self, grid, y, tile_cache):
        cols = xrange(grid.min_x - 1, grid.max_x + 2)
        return ''.join(self._get_tile(grid[x, y], tile_cache) for x in cols)

    def _get_tile(self, cell, tile_cache):
        cell_type = cell.__class__
        try:
            return self._tile_map[cell_type]
        except KeyError:
            try:
                return tile_cache[cell_type]
            except KeyError:
                if not hasattr(cell, 'ansi_tile'):
                    raise RenderingError('Cell %s does not have an "ansi_tile" method' % cell_type.__name__)
                tile = cell.ansi_tile()
                tile_cache[cell_type] = tile
                return tile

class StandardGraphicalGridRenderer:
    def __init__(self, tile_map):
        pass
    
    def render(self, state, window, rect = None):
        pass

    def close(self):
        pass

class WindowDisplay:
    def __init__(self, state, renderer):
        self._renderer = renderer
        self._window = None

    def render(self, state):
        if self._window:
            self._resize_if_needed(state)
        else:
            self._window = self._open_window(state)
        renderer.render(state, self._window)

    def _open_window(self, state):
        pass

    def _resize_if_needed(self, state):
        pass
    
class StandardGridRendererFactory:
    SUPPORTED_MODES = ('ansi', 'human')

    def __init__(self, ansi_tile_map = { }, graphical_tile_map = { }):
        self._ansi_tile_map = ansi_tile_map
        self._graphical_tile_map = graphical_tile_map
    
    def create_renderer(self, mode, state):
        if mode == 'ansi':
            return StandardAnsiGridRenderer(tile_map = self._ansi_tile_map)
        elif mode == 'human':
            renderer = \
                StandardGraphicalRenderer(tile_map self._graphical_tile_map)
            return WindowDisplay(state, renderer)
            
        

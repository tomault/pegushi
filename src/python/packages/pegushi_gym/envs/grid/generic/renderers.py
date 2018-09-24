"""
Implementation of renderers for the generic grid environment
"""

import pyglet

class RenderingError(Exception):
    pass

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
    def __init__(self, tile_map, tile_size = 24):
        self._tile_map = tile_map
        self._tile_size = tile_size
        self._background = None

    @property
    def tile_size(self):
        return self._tile_size
    
    def render(self, state, window, rect = None):
        pyglet.gl.glPushMatrix()
        try:
            if not rect:
                rect = (0, 0, window.width, window.height)
            need_texture_scaling = \
                self._set_drawing_area(state.grid.width, state.grid.height,
                                       *rect)
            self._set_background(state.grid.width * self._tile_size,
                                 state.grid.height * self._tile_size)
            self._render(state, window, need_texture_scaling)
        finally:
            pyglet.gl.glPopMatrix()

    def _set_drawing_area(self, grid_width, grid_height, x, y, area_width,
                          area_height):
        if x or y:
            pyglet.gl.glTranslatef(float(x), float(y), 0.0)
        if (grid_width != area_width) or (grid_height != area_height):
            x_scale = float(area_width)/float(grid_width)
            y_scale = float(area_height)/float(grid_height)
            pyglet.gl.glScalef(x_scale, y_scale, 1.0)
            return True
        return False

    def _set_background(self, area_width, area_height):
        if (not self._background) or (self._background.width != area_width) or\
           (self._background.height != area_height):
            self._background = \
                pyglet.image.SolidColorPattern((255, 255, 255, 255))\
                    .create_image(area_width, area_height)

    def _render(self, state, window, need_texture_scaling):
        if need_texture_scaling:
            pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,
                                      pyglet.gl.GL_TEXTURE_MAG_FILTER,
                                      pyglet.gl.GL_NEAREST)
            pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,
                                      pyglet.gl.GL_TEXTURE_MIN_FILTER,
                                      pyglet.gl.GL_NEAREST)
        x = 0
        y = 0

        self._background.blit(0, 0)
        for j in xrange(state.grid.min_y, state.grid.max_y + 1):
            for i in xrange(state.grid.min_x, state.grid.max_x + 1):
                tile = self._get_tile(state.grid[j, i])
                tile.blit(x, y)
                x += self.tile_size
            y += self.tile_size

        for obj in state.objects:
            tile = self._get_tile(obj)
            tile.blit(obj.x * self._tile_size, obj.y * self._tile_size)

        tile = self._get_tile(state.agent)
        tile.blit(agent.x * self._tile_size, agent.y * self._tile_size)

    def _get_tile(self, thing):
        try:
            return self._tile_map[thing]
        except KeyError:
            pass

        try:
            return self._tile_map[thing.__class__]
        except KeyError:
            pass

        if not hasattr(thing, 'graphical_tile'):
            raise RenderingError('%s does not have a graphical_tile() method' % thing.__class__)
        return thing.graphical_tile()

class WindowDisplay:
    # TODO: Default the max window size to be the largest window that
    #       will fit on the screen but still be a multiple of the tile
    #       size.
    def __init__(self, state, renderer, min_window_size = renderer.tile_size,
                 max_window_size = renderer.tile_size * 50):
        self._renderer = renderer
        self._window = None
        self._min_window_size = min_window_size
        self._max_window_size = max_window_size

    def render(self, state):
        if self._window:
            self._resize_if_needed(state)
        else:
            self._window = self._open_window(state)
        renderer.render(state, self._window)

    def close(self):
        if self._window:
            self._window.close()
            self._window = None

    def _open_window(self, state):
        w = state.grid.width * self.renderer.tile_size
        h = state.grid.height * self.renderer.tile_size
        self._window = pyglet.window.Window(width = w, height = h,
                                            vsync = False)

    def _resize_if_needed(self, state):
        def clamp(d):
            return min(max(d, self._min_window_size), self._max_window_size)

        w = clamp(state.grid.width * self.renderer.tile_size)
        h = clamp(state.grid.height * self.renderer.tile_size)
        if (self._window.width != w) or (self._window.height != h):
            self._window.set_size(w, h)
    
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
                StandardGraphicalRenderer(tile_map = self._graphical_tile_map)
            return WindowDisplay(state, renderer)
            
        

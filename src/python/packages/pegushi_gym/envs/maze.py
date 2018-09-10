"""Simple maze environments"""

import gym
import gym.spaces
from gym import error, spaces, utils
from gym.utils.seeding import create_seed, np_random

import numpy as np
import heapq

import pygame
import time

class SimpleMazeRenderer:
    def __init__(self, screen, tile_size, wall_tile_image = None,
                 wall_tile_color = (0, 0, 0),
                 open_space_color = (255, 255, 255)):
        self.screen = screen # pygame.Surface; Where to render the maze
        self.tile_size = tile_size  # int; Size of wall tiles, in pixels

        self._wall_tile = \
            self._create_wall_tile(wall_tile_image, wall_tile_color)
        wall_patterns = \
            self._create_wall_patterns(self._wall_tile, open_space_color)
        self._left_wall_img = wall_patterns[0]
        self._bottom_wall_img = wall_patterns[1]
        self._wall_patterns = wall_patterns[2:]

    def draw(self, maze, origin = (0, 0)):
        top_left = (origin[0] + self.tile_size, origin[1])
        bottom_right = (origin[0] + (2 * maze.shape[1] + 1) * self.tile_size,
                        origin[1] + 2 * maze.shape[0] * self.tile_size)
        for (i, y) in zip(xrange(maze.shape[0] - 1, -1, -1),
                          xrange(top_left[1], bottom_right[1], 2 * self.tile_size)):
            self.screen.blit(self._left_wall_img, (origin[0], y))
            for (j, x) in zip(xrange(0, maze.shape[1]),
                              xrange(top_left[0], bottom_right[0], 2 * self.tile_size)):
                self.screen.blit(self._wall_patterns[maze[i, j]], (x, y))
        self.screen.blit(self._wall_tile, (0, bottom_right[1]))
        for x in xrange(top_left[0], bottom_right[0]):
            self.screen.blit(self._bottom_wall_img, (x, bottom_right[1]))

    def _create_wall_tile(self, image, color):
        return _load_or_create_solid_tile(self.tile_size, image, color)

    def _create_wall_patterns(self, wall_tile, open_space_color):
        def create_tile(width, height, filled):
            tile = pygame.Surface((width * self.tile_size,
                                   height * self.tile_size))
            tile.fill(open_space_color)
            for i in filled:
                x = (i % width) * self.tile_size
                y = (i / width) * self.tile_size
                tile.blit(wall_tile, (x, y))
            return tile
        
        # First tile is 1 x 2 for the left border
        left_border = create_tile(1, 2, (0, 1))

        # Border for the bottom: 2 x 1 tile
        bottom_border = create_tile(2, 1, (0, 1))

        # Passages north and west are blocked
        both_walls = create_tile(2, 2, (0, 1, 3))

        # East passage is open
        north_wall = create_tile(2, 2, (0, 1))

        # North passage is open
        east_wall = create_tile(2, 2, (1, 3))

        # Both passages are open
        both_open = create_tile(2, 2, (1, ))

        return (left_border, bottom_border, both_walls, north_wall,
                east_wall, both_open)

class _FixedMazeEnvironmentDisplay:
    def __init__(self, maze, tile_size, wall_image = None,
                 wall_color = (0, 0, 0), open_space_color = (255, 255, 255),
                 agent_image = None, agent_color = (0, 0, 255),
                 goal_location = (0, 0), goal_image = None,
                 goal_color = (0, 192, 0)):
        self.maze = maze
        self.tile_size = tile_size
        self.goal_location = goal_location
        self._goal_coordinates = \
            self._location_to_coordinates((goal_location[0], goal_location[1],
                                           0, 0))

        self._wall_tile = \
            _load_or_create_solid_tile(tile_size, wall_image, wall_color)
        self._agent_tile = \
            _load_or_create_solid_tile(tile_size, agent_image, agent_color)
        self._goal_tile = \
            _load_or_create_solid_tile(tile_size, goal_image, goal_color)
        self._open_space_color = open_space_color
        self._open_space_tile = \
            _load_or_create_solid_tile(tile_size, None, open_space_color)
        
        # These will be initialized at the first call to draw()
        self._screen = None
        self._maze_renderer = None

    def draw(self, agent_location = None):
        if not self._screen:
            self._initialize_display()
        self._screen.fill(self._open_space_color)
        self._maze_renderer.draw(self.maze)
        self._draw_goal()
        if agent_location:
            self._draw_agent(agent_location)
        pygame.display.flip()

    def move_agent(self, old, new):
        if not self._screen:
            return
        old_coordinates = self._location_to_coordinates(old)
        self._screen.blit(self._open_space_tile, old_coordinates)

        self._draw_goal()
        self._draw_agent(new)
        pygame.display.flip()

    def close(self):
        if self._screen:
            pygame.display.quit()
            self._screen = None
            self._maze_renderer = None

    def _draw_goal(self):
        self._screen.blit(self._goal_tile, self._goal_coordinates)

    def _draw_agent(self, location):
        coordinates = self._location_to_coordinates(location)
        self._screen.blit(self._agent_tile, coordinates)

    def _location_to_coordinates(self, loc):
        x = (2 * loc[0] + 1) * self.tile_size + loc[2]
        y = (2 * (self.maze.shape[0] - loc[1]) - 1) * self.tile_size + loc[3]
        return (x, y)

    def _initialize_display(self):
        display_size = ((2 * self.maze.shape[1] + 1) * self.tile_size,
                        (2 * self.maze.shape[0] + 1) * self.tile_size)
        self._screen = pygame.display.set_mode(display_size)
        self._maze_renderer = \
            SimpleMazeRenderer(self._screen, self.tile_size,
                               wall_tile_image = self._wall_tile,
                               open_space_color = self._open_space_color)
        
        
        
class FixedMazeEnvironment(gym.Env):
    action_space = spaces.Discrete(4)
    metadata = { 'render.modes' : [ 'human', 'ansi' ] }
    
    def __init__(self, layout = None, start = (0, 0), goal = None, width = 0,
                 height = 0, algorithm = 'kruskal', rng = None, seed = None,
                 max_steps = 10000, goal_reward = 100.0, step_reward = -1.0,
                 hit_wall_reward = -5.0, agent_image = None):
        """Create a new FixedMazeEnvironment.
Arguments are:
    layout     numpy.ndarray;  A 2D array of integers indicating connectivity
               between maze cells.  Each cell in the array indicates its
               connectivity to the cell to the right (increasing x) and
               to the cell above (increasing y) by setting the appropriate bit.
               Connectivity to the cells to the left or below is computed by
               going to that cell and checking its connectivity to the
               cell to its right or above.  This removes redundancy in the
               representation.

               If bit 0 is set in the cell's value, it is connected to the
               cell to the right.  If bit 1 is set, it is connected to the
               cell above.  

               If the layout is None, the environment will generate a random
               maze with dimensions specified by the "width" and "height"
               arguments using the algorithm specified by the "algorithm"
               argument.

    start      tuple(int, int); (x, y) coordinates where the agent starts.  If
               the start and the goal are coincident, the starting location
               will be randomized

    goal       tuple(int, int); (x, y) coordinates of the goal; if None, the
               goal will be set randomly

    width      int; Width of randomly-generated mazes, in squares

    height     int; Height of randomly-generated mazes, in squares

    algorithm  str; Algorithm used to generate random mazes.  The currently
               supported algorithms are:
                   kruskal    Kruskal's minimal spanning tree algorithm

    rng        np.random.RandomState or equivalent; the environment's
               source of random numbers.  If None, the environment
               will create its own RNG using gym.utils.seeding.np_random()

    seed       int; If the "rng" argument is None, this seed will be
               used to create and seed the environment's RNG.  If the "rng"
               argument is not None, this argument should contain the
               value used to seed that RNG.  If the "seed" argument is
               None, the environment will create its own seed.

    max_steps  int; Maximum number of steps the agent can take before the
               episode terminates in failure

    goal_reward  float; Reward agent receives upon reaching the goal

    step_reward  float; Reward (usually negative) agent receives for each
                 step that does not contact a wall

    hit_wall_reward float; Reward (usually negative) agent receives when
                 it bumps into a wall

    agent_image  str, unicode or pygame.Surface;  Image to use for the agent
               when the environment is rendered in "human" mode.  If this
               argument is a str or unicode, it specifies the name of a file
               with the image to use for the agent.  If this argument is
               a pygame.Surface, it contains the image itself
"""
        gym.Env.__init__(self)

        if rng:
            if seed == None:
                raise ValueError('If rng is not None, seed cannot be None')
            self.rng = rng
            self.seed = seed
        else:
            if seed == None:
                seed = create_seed()
            (self.rng, self.seed) = np_random(seed)
        
        if not layout is None:
            if len(layout.shape) != 2:
                raise ValueError('Maze layout must be a 2D array')
            self._layout = layout
        elif width < 1:
            raise ValueError('width must be > 0')
        elif height < 1:
            raise ValueError('height must be > 0')
        else:
            self._layout = _generate_random_maze(width, height, algorithm,
                                                 self.rng)

        if not goal:
            goal = (self.rng.randint(0, self._layout.shape[1]),
                    self.rng.randint(0, self._layout.shape[0]))

        self.goal = goal
        self.max_steps = max_steps
        self.goal_reward = goal_reward
        self.step_reward = step_reward
        self.hit_wall_reward = hit_wall_reward
        
        while self.goal == start:
            start = (self.rng.randint(0, self._layout.shape[1]),
                     self.rng.randint(0, self._layout.shape[0]))

        self.start = start

        bounds = (self._layout.shape[1], self._layout.shape[0])
        self.observation_space = spaces.MultiDiscrete(bounds)
        self.reward_range = (-5.0 * max_steps, 100)

        self._delta_x = [  0,  1,  0, -1 ]
        self._delta_y = [  1,  0, -1,  0 ]
        self._can_move = [ self._can_move_north, self._can_move_east,
                           self._can_move_south, self._can_move_west ]

        self._walls1 = (' *', '  ', ' *', '  ',
                        '#*', '# ', '#*', '# ',
                        '$*', '$ ', '$*', '$ ',
                        '!*', '! ', '!*', '! ')
        self._walls2 = ('**', '**', ' *', ' *')

        self._renderer = None
        self.reset()

        self._agent_image = agent_image

    def reset(self):
        (self._x, self._y) = self.start
        self.tick = 0
        return (self._x, self._y)
        
    def step(self, action):
        self.tick += 1

        if self._can_move[action](self._x, self._y):
            self._x += self._delta_x[action]
            self._y += self._delta_y[action]
            if (self._x == self.goal[0]) and (self._y == self.goal[1]):
                return ((self._x, self._y), self.goal_reward, True, {})
            return ((self._x, self._y), self.step_reward,
                    self.tick >= self.max_steps, {})
        return ((self._x, self._y), self.hit_wall_reward,
                self.tick >= self.max_steps, {})

    def render(self, mode = 'human'):
        if mode == 'human':
            return self._render_human()
        elif mode == 'ansi':
            return self._render_ansi()
        else:
            raise ValueError('Unknown rendering mode "%s"' % mode)

    def close(self):
        if self._renderer:
            self._renderer.close()
            self._renderer = None

    def seed(self, seed = None):
        if seed == None:
            seed = create_seed()
        (self.rng, self.seed) = np_random(seed)

    @property
    def current_state(self):
        return (self._x, self._y)
    
    def teleport(self, x, y):
        self._x = x
        self._y = y

    def compute_solution_path(self):
        _, prior = self._compute_solution()
        path = [ self.goal ]
        current = self.goal
        while current != self.start:
            current = prior[current]
            path.append(current)
        path.reverse()
        return tuple(path)

    def compute_solution_length(self):
        distance, _ = self._compute_solution()
        return distance
    
    def _compute_solution(self):
        def next_states(x, y):
            next_states = [ ]
            if self._can_move_north(x, y):
                next_states.append((x, y + 1))
            if self._can_move_east(x, y):
                next_states.append((x + 1, y))
            if self._can_move_south(x, y):
                next_states.append((x, y - 1))
            if self._can_move_west(x, y):
                next_states.append((x - 1, y))
            return next_states

        # Dijkstra's algorithm.  This is overkill if there is only one
        # solution path, but we plan to add multiple solution paths soon.
        heap = [ ]
        shape = tuple(reversed(self._layout.shape))
        prior = np.full(shape, None)
        distance = np.full(shape, np.inf)
        distance[self.start] = 0
        visited = set()

        heapq.heappush(heap, (0, self.start))
        while heap:
            (d, current) = heapq.heappop(heap)
            if not current in visited:
                assert d == distance[current]
                if current == self.goal:
                    return (d, prior)
                d += 1
                for next in next_states(*current):
                    if d < distance[next]:
                        distance[next] = d
                        prior[next] = current
                        heapq.heappush(heap, (d, next))
                visited.add(current)

        raise RuntimeError('Could not find a solution')
        
    def _can_move_north(self, x, y):
        return self._layout[y, x] & 0x2

    def _can_move_east(self, x, y):
        return self._layout[y, x] & 0x1

    def _can_move_south(self, x, y):
        return (y > 0) and self._can_move_north(x, y - 1)

    def _can_move_west(self, x, y):
        return (x > 0) and self._can_move_east(x - 1, y)

    def _render_human(self):
        if self._renderer:
            pos = (self._x, self._y, 0, 0)
            if pos != self._last_rendered_position:
                self._renderer.move_agent(self._last_rendered_position, pos)
                self._last_rendered_position = pos
        else:
            self._renderer = \
                _FixedMazeEnvironmentDisplay(self._layout, 24,
                                             goal_location = self.goal,
                                             agent_image = self._agent_image)
            pos = (self._x, self._y, 0, 0)
            self._renderer.draw(pos)
            self._last_rendered_position = pos
            
    def _render_ansi(self):
        def wall1_index(y, x):
            i = self._layout[y, x]
            if (x == self._x) and (y == self._y):
                i += 4
            if (x == self.goal[0]) and (y == self.goal[1]):
                i += 8
            return i
        
        def walls(y):
            cols = xrange(0, self._layout.shape[1])
            r2 = ''.join(self._walls2[self._layout[y, x]] for x in cols)

            cols = xrange(0, self._layout.shape[1])
            r1 = ''.join(self._walls1[wall1_index(y, x)] for x in cols)
            return '*' + r2 + '\n*' + r1

        rows = xrange(self._layout.shape[0] - 1, -1, -1)
        law_row = '*' + ('**' * self._layout.shape[1])
        return '\n'.join(walls(y) for y in rows) + '\n' + law_row

def _generate_random_maze(width, height, algorithm, rng):
    if algorithm == 'kruskal':
        return _generate_random_maze_kruskal(width, height, rng)
    raise ValueError('Unknown algorithm "%s"' % algorithm)

def _generate_random_maze_kruskal(width, height, rng):
    def renumber_tree(old, new):
        assert new < old

        i = first_cell[old]
        assert i >= 0
        
        while i >= 0:
            tree_for_cell[i] = new
            last_old = i
            i = next_cell[i]

        # Join the lists together
        next_cell[last_old] = first_cell[new]
        first_cell[new] = first_cell[old]
        first_cell[old] = -1
        
    # A graph whose vertecies are maze cells and whose edges represent
    # connections between cells to the north (increasing y/row) or east
    # (increasing x/column) represents the maze.  Initially, each cell is
    # in its own tree.  The algorithm picks cells that neighbor to the north
    # or to the east uniformly and random and merges them into the same
    # polytree if they are not already.

    # TODO: Reimplement this with a disjoint set data structure
    
    # Number of trees.  When this reaches 1, we're done
    num_trees = width * height

    # Tree that each cell belongs to.  Initially, each cell is in its own tree
    tree_for_cell = np.asarray(xrange(0, num_trees), dtype = np.int32)

    # The algorithm maintains a linked list of cells that make up each tree
    # so it can quickly iterate over the cells that make up that tree to
    # assign them to a new tree.  The values in this array are the first
    # cell in the linked list for the corresponding tree, encoded as
    # (y * width + x).  The values in the next_cell array are the next
    # cell in the linked list.
    first_cell = np.asarray(xrange(0, num_trees), dtype = np.int32)
    next_cell = np.full((num_trees,), -1, dtype = np.int32)

    # The connectivity array.
    layout = np.zeros((height, width), dtype = np.int32)

    num_neighbors = 2 * width * height - width - height
    neighbors_per_row = 2 * width - 1
    width_less_1 = width - 1
    neighbor_order = rng.permutation(num_neighbors)
    for neighbor in neighbor_order:
        y = neighbor/neighbors_per_row
        x = neighbor % neighbors_per_row
        if x < width_less_1:
            i = y * width + x
            j = i + 1
            flag = 1
        else:
            x -= width_less_1
            i = y * width + x
            j = i + width
            flag = 2

        ti = tree_for_cell[i]
        tj = tree_for_cell[j]
        if ti != tj:
            renumber_tree(max(ti, tj), min(ti, tj))
            layout[y, x] |= flag
            num_trees -= 1
            if num_trees == 1:
                break

    return layout

def generate_random_maze(width, height, algorithm = 'kruskal', rng = None,
                         seed = None):
    if not rng:
        if not seed:
            seed = create_seed()
        (rng, _) = np_random(seed)
    return _generate_random_maze(width, height, algorithm, rng)

def _load_or_create_solid_tile(tile_size, tile_image, tile_color):
    if isinstance(tile_image, str) or isinstance(tile_image, unicode):
        tile_image = pygame.image.load(tile_image)
    if isinstance(tile_image, pygame.Surface):
        if (tile_image.get_width() != tile_size) or \
           (tile_image.get_height() != tile_size):
            tile_image = pygame.transform.smoothscale(tile_image,
                                                      (tile_size, tile_size))
    else:
        tile_image = pygame.Surface((tile_size, tile_size))
        tile_image.fill(tile_color)
    return tile_image


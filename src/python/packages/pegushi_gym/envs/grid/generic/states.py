"""State representations for the generic grid environment"""

import gym.spaces.Tuple
import pegushi_gym.envs.grid.generic.renderers.StandardGridRendererFactory

class State:
    """
Basic world state for a gridworld environment.
"""
    def __init__(self, agent, grid, objects):
        self._agent = agent
        self._grid = grid
        self._objects = objects

    @property
    def agent(self):
        return self._agent

    @property
    def grid(self):
        return self._grid

    @property
    def objects(self):
        return self._objects

class ExecutableState:
    """
World state with optional goal and methods needed to interact with the
environment
"""
    def __init__(self, agent, grid, objects, goal = None, goal_reward = None,
                 renderer_factory = StandardGridRendererFactory):
        def extend_space(spaces, x):
            if hasattr(x, 'state_space'):
                return spaces + (x.state_space, )
            return spaces
        
        self._agent = agent
        self._grid = grid
        self._objects = objects
        self._create_renderer = renderer_factory
        self.supported_rendering_modes = \
            renderer_factory.supported_rendering_modes

        self._goal = goal

        spaces = reduce(extend_space, self._objects,
                        extend_space(extend_space((), self._agent), self._grid))
        self.state_space = gym.spaces.Tuple(spaces)

        self._visible_state = State(self._agent, self._grid,
                                    tuple(o for o in objects if o.visible))

    @property
    def agent(self):
        return self._agent

    @property
    def grid(self):
        return self._grid

    @property
    def objects(self):
        return self._objects

    def visible(self):
        return self._visible_state
    
    def reset(self):
        self._grid = self._grid.reset()
        self._agent = self._agent.reset(self._grid)
        self._objects = [ o.reset() for o in self._objects ]
        return self

    def execute(self, env, action):
        _, reward = self.agent.execute(env, self, action)
        return self, reward

    def is_terminal(self):
        return self._goal and self._agent.at(*self._goal)

    def create_renderer(self, mode):
        return self._create_renderer(self, mode)

"""Implementation of the generic gridworld environment."""

import cPickle

class GenericGridEnvironment:
    def __init__(self, state, rng, max_steps = None):
        """
Create a grid world with the given agent, grid and objects.
  state:     the world state; see below for the requirements of the state
             instance

  rng:       np.random.RandomState;  the environment's source of randomness.

  max_steps: int; Maximum length of an episode, in steps.  None indicates
             the episode length is unbounded.

The state needs to provide the following fields and methods:
  agent:     grid.generic.agents.Agent or equivalent; the agent

  grid:      grid.generic.grids.Grid or equivalent; the grid

  objects:   list[grid.generic.objects.Object or equivalent]; the objects
             in the environment.  

  visible() -> grid.generic.states.State; returns the visible world state.

  reset() -> grid.generic.states.ExecutableState; reset the state to its
             initial state.

  execute(action) -> grid.generic.states.ExecutableState, int/float;
             Execute the given action, returning the next state, the reward
             and whether the terminal state has been reached or not.

  is_terminal() -> boolean;  returns true if the state is terminal

  create_renderer(mode) -> grid.generic.states.renderers.Renderer;
             Creates the renderer for the given mode.  Raises ValueError
             if mode is unknown or not supported

Applications are expected to extend this class to define the world state,
starting state, goal state and so on."""
        self._state = state
        self._rng = rng
        self.max_steps = max_steps
        self.tick = 0

        self._renderers = { }

        self.state_space = state.state_space
        self.action_space = state.agent.action_space

    @property
    def state(self):
        return self._state.visible()

    @property
    def rng(self):
        return self._rng

    @property
    def reset(self):
        self._state = self._state.reset()
        return self._state.visible()

    def step(self, action):
        self.tick += 1

        action = self._before_action(action)
        next_state, reward = self._state.execute(action)
        done = self._state.is_terminal()
        next_state, reward, done = self._after_action(next_state, reward, done)

        self._state = next_state
        return next_state.visible(), reward, done, {}

    def render(self, mode):
        try:
            renderer = self._renderers[mode]
        except KeyError:
            renderer = self._state.create_renderer(mode)
            self._renderers[mode] = renderer
        return renderer.render(self._state)

    def close(self):
        self.close_all_renderers()
        self._state.close()

    def close_renderer(self, mode):
        try:
            self._renderers[mode].close()
            del self._renderers[mode]
        except KeyError:
            pass

    def close_all_renderers(self):
        for renderer in self._renderers.itervalues():
            renderer.close()
        self._renderers = { }

    def save_state(self):
        return cPickle.dumps(self.state, cPickle.HIGHEST_PROTOCOL)

    def restore_state(self, saved):
        self._state = cPickle.loads(saved)
        
    def _before_action(self, action):
        return action

    def _after_action(self, next_state, reward, done):
        done = done or self._time_limit_exceeded()
        return next_state, reward, done

    def _time_limit_exceeded(self):
        return (self.max_steps != None) and (self.tick >= self.max_steps)

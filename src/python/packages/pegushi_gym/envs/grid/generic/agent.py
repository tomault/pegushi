"""
Implementation of agents for the generic gridworld.
"""
from pegushi_gum.envs.grid.generic.core import Outcomes, ThingTypes, Directions
import gym.spaces

class Agent:
    BEHAVIOR_NAMES = ( 'WAIT', 'MOVE_NORTH', 'MOVE_EAST', 'MOVE_SOUTH',
                       'MOVE_WEST', 'GET', 'DROP', 'PUSH_NORTH', 'PUSH_EAST',
                       'PUSH_SOUTH', 'PUSH_WEST' )
                       
    def __init__(self, x, y, cell):
        self._x = x
        self._y = y
        self._cell = cell
        self._inventory = ()
        
        self.state_space = gym.spaces.Discrete(2)
        self.action_space = gym.spaces.Discrete(len(Agent._BEHAVIOR))

    @property
    def type(self):
        return ThingTypes.AGENT
    
    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def cell(self):
        return self._cell

    @property
    def container(self):
        return self._cell
    
    @property
    def inventory(self):
        return self._inventory
    
    def execute(self, env, state, action, initial_reward):
        behavior = self._BEHAVIOR[action]
        outcome, reward = behavior(self, env, state, initial_reward)
        if reward == None:
            reward = 0.0
        return outcome, reward

    def at(self, x, y):
        return self._x == x and self._y == y

    def wait(self, env, state, initial_reward):
        outcome, reward = self._cell.wait_actor(env, state, reward, self)
        if outcome == Outcomes.NOT_DONE:
            reward = env.reward_map.get('WAIT', 0.0)
        return Outcomes.DONE, reward
    
    def move_north(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[1], env, state, initial_reward,
                          Directions.NORTH)

    def move_east(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[2], env, state, initial_reward,
                          Directions.EAST)

    def move_south(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[3], env, state, initial_reward,
                          Directions.SOUTH)

    def move_west(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[4], env, state, initial_reward,
                          Directions.WEST)

    def get(self, env, state, initial_reward):
        target = self._cell.portable_object
        if not target:
            reward = env.reward_map.get('GET:NO_OBJECT', 0.0)
        else:
            outcome, reward = self._cell.get(env, state, initial_reward,
                                             self, target)
            if outcome == Outcomes.DONE:
                return outcome, reward

            outcome, reward = target.get(env, state, initial_reward, self,
                                         target)
            if outcome == Outcomes.DONE:
                return outcome, reward

            if self._inventory:
                reward = env.reward_map.get('GET:FULL', 0.0)
            else:
                target.container.remove(target)
                target.set_container(self)
                self._inventory = target
                # Reward set by target.get()
                #reward = env.reward_map.get('GET', None)

        return Outcomes.DONE, reward
    
    def drop(self, env, state, initial_reward):
        if not self._inventory:
            reward = env.reward_map.get('DROP:NO_OBJECT', 0.0)
        else:
            outcome, reward = self._cell.drop(env, state, initial_reward,
                                              self, self._inventory)
            if outcome == Outcomes.DONE:
                return outcome, reward

            

            if self._cell.portable_object:
                reward = env.reward_map.get('DROP:FULL')
            else:
                self._cell.put(target)
                target.set_container(self._cell)
                self._inventory = None
                # reward set by target.drop()
                #reward = env.reward_map.get('DROP')

        return Outcomes.DONE, reward

    def push_north(self, env, state, initial_reward):
        return self._push('PUSH_NORTH', env, state, initial_reward,
                          Directions.NORTH)
            
    def push_east(self, env, state, initial_reward):
        return self._push('PUSH_EAST', env, state, initial_reward,
                          Directions.EAST)

    def push_south(self, env, state, initial_reward):
        return self._push('PUSH_SOUTH', env, state, initial_reward,
                          Directions.SOUTH)
            
    def push_west(self, env, state, initial_reward):
        return self._push('PUSH_WEST', env, state, initial_reward,
                          Directions.WEST)

    ## Manipulators

    def set_cell(self, cell):
        self._cell = cell

    def add(self, object):
        if self._inventory:
            raise ValueError('Already holding an object')
        self.

    def _move(self, behavior_name, env, state, initial_reward, direction):
        outcome, reward = self._cell.exit_actor(env, state, initial_reward,
                                                self, direction)
        if outcome == Outcomes.NOT_DONE:
            # Can't go this way
            reward = env.reward_map.get('MOVE:NO_EXIT', 0.0)
        elif reward == None:
            reward = env.reward_map.get(behavior_name, None)
        return outcome, reward

    def _push(self, behavior_name, env, state, initial_reward, direction):
        next_cell = direction.next_cell(state.grid, self._x, self._y)
        if not (next_cell or next_cell.moveable_object):
            reward = env.reward_map.get('PUSH:NO_OBJECT', 0.0)
            return Outcomes.DONE, reward

        target = next_cell.movable_object
        outcome, reward = self._cell.push(env, state, initial_reward,
                                          self, target, direction)
        if outcome == Outcome.NOT_DONE:
            # Can't push
            reward = env.reward_map.get('PUSH:FAILED', 0.0)
        elif reward == None:
            reward = env.reward_map.get(behavior_name, None)
        return outcome, reward
        
Agent._BEHAVIOR = ( Agent.wait, Agent.move_north, Agent.move_south,
                    Agent.move_east, Agent.move_west, Agent.get, Agent.drop,
                    Agent.push_north, Agent.push_east, Agent.push_south,
                    Agent.push_west )
assert len(Agent._BEHAVIOR_NAMES) == len(Agent._BEHAVIOR)
Agent._BEHAVIOR_MAP = dict(zip(Agent.BEHAVIOR_NAMES, Agent._BEHAVIOR))

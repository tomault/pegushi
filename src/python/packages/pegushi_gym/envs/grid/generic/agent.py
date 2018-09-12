"""
Implementation of agents for the generic gridworld.
"""
from pegushi_gym.envs.grid.generic.grids import Directions
from pegushi_gum.envs.grid.generic.behaviors import Outcomes
import gym.spaces

class Agent:
    BEHAVIOR_NAMES = ( 'WAIT', 'MOVE_NORTH', 'MOVE_EAST', 'MOVE_SOUTH',
                       'MOVE_WEST', 'GET', 'DROP', 'PUSH_NORTH', 'PUSH_EAST',
                       'PUSH_SOUTH', 'PUSH_WEST' )
                       
    def __init__(self, x, y, cell, rewards = { }):
        self._x = x
        self._y = y
        self._cell = cell
        self._reward_map = rewards
        self._inventory = ()
        
        self.state_space = gym.spaces.Discrete(2)
        self.action_space = gym.spaces.Discrete(len(Agent._BEHAVIOR))

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def inventory(self):
        return self._inventory
    
    def execute(self, env, state, action, initial_reward):
        return self._BEHAVIOR[action](self, env, state, initial_reward)

    def at(self, x, y):
        return self._x == x and self._y == y

    def wait(self, env, state, initial_reward):
        outcome, reward = self._cell.actor_wait(env, state, reward, self)
        if outcome == Outcomes.NOT_DONE:
            reward = self._reward_map.get('WAIT:FAIL', 0.0)
        elif reward == None:
            reward = self._reward_map.get('WAIT', None)
        return outcome, reward
    
    def move_north(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[1], env, state, initial_reward,
                          Directions.NORTH)

    def move_east(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[1], env, state, initial_reward,
                          Directions.EAST)

    def move_south(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[1], env, state, initial_reward,
                          Directions.SOUTH)

    def move_west(self, env, state, initial_reward):
        return self._move(self._BEHAVIOR_NAMES[1], env, state, initial_reward,
                          Directions.WEST)

    def get(self, env, state, initial_reward):
        def do_get(env, state, reward, actor):
            target = self._cell.portable_object
            if not target:
                reward = self._reward_map.get('GET:NO_OBJECT', 0.0)
                return Outcomes.STOP, reward
            outcome, reward = self._cell.get(env, state, initial_reward,
                                             actor, target)
            if env._object_stack and (env._object_stack[-1] == target):
                self._inventory = object_stack.pop()
            return outcome, reward
        
        if self._inventory:
            return Outcomes.STOP, self.reward_map.get('GET:FULL', 0.0)
        return self._execute_behaviors(self._BEHAVIOR_NAMES[5], env, state,
                                       initial_reward, (do_get,), finalize)
    
    def drop(self, env, state, initial_reward):
        def do_drop(env, state, reward, actor):
            obj = self._inventory
            outcome, reward = \
                self._cell.drop(env, state, initial_reward, actor, obj)
            if obj.owner != self:
                self._inventory = None
            return outcomes, reward    

        if not self._inventory:
            return Outcomes.STOP, self._reward_map.get('DROP:NO_OBJECT', 0.0)
        return self._execute_behaviors(self._BEHAVIOR_NAMES[6], env, state,
                                       initial_reward, (do_drop,))

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


    def _move(self, behavior_name, env, state, initial_reward, direction):
        outcome, reward = self._cell.exit_actor(env, state, initial_reward,
                                                self, direction)
        if outcome == Outcomes.NOT_DONE:
            # Can't go this way
            reward = self._reward_map.get('MOVE:NO_EXIT', 0.0)
        elif reward == None:
            reward = self._reward_map.get(behavior_name, None)
        return outcome, reward

    def _push(self, behavior_name, env, state, initial_reward, direction):
        next_cell = direction.next_cell(state.grid, self._x, self._y)
        if not (next_cell or next_cell.moveable_object):
            reward = self._reward_map.get('PUSH:NO_OBJECT', 0.0)
            return Outcomes.NOT_DONE, reward
        target = next_cell.movable_object
        outcome, reward = self._cell.push(env, state, initial_reward,
                                          self, target, direction)
        if outcome == Outcome.NOT_DONE:
            # Can't push
            reward = self._reward_map.get('PUSH:FAILED', 0.0)
        elif reward == None:
            reward = self._reward_map.get(behavior_name, None)
        return outcome, reward
        
            
        
    def _execute_behaviors(self, name, env, state, initial_reward, behaviors,
                           final_update = None):
        reward = initial_reward
        for behavior in behaviors:
            outcome, reward = behavior(env, state, reward, self)
            if outcome != Outcomes.CONTINUE:
                return outcome, reward
        if final_update:
            reward = final_update(reward)
        if reward == None:
            reward = self._reward_map.get(name, 0.0)
        return outcome, reward
    
        

Agent._BEHAVIOR = ( Agent.wait, Agent.move_north, Agent.move_south,
                    Agent.move_east, Agent.move_west, Agent.get, Agent.drop,
                    Agent.push_north, Agent.push_east, Agent.push_south,
                    Agent.push_west )
assert len(Agent._BEHAVIOR_NAMES) == len(Agent._BEHAVIOR)
Agent._BEHAVIOR_MAP = dict(zip(Agent.BEHAVIOR_NAMES, Agent._BEHAVIOR))
Agent._DEFAULT_REWARD = [ 0.0 ] * len(self._BEHAVIOR)


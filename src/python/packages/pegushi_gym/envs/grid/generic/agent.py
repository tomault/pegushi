"""
Implementation of agents for the generic gridworld.
"""
from pegushi_gym.envs.grid.generic.core import Outcomes, ThingTypes, Directions
from pegushi_gym.envs.grid.generic.rewards import eval_if_needed
import gym.spaces

class Agent:
    BEHAVIOR_NAMES = ( 'WAIT', 'MOVE_NORTH', 'MOVE_EAST', 'MOVE_SOUTH',
                       'MOVE_WEST', 'GET', 'DROP', 'PUSH_NORTH', 'PUSH_EAST',
                       'PUSH_SOUTH', 'PUSH_WEST' )
                       
    def __init__(self, cell = None):
        self._cell = cell
        self._inventory = ()
        
        self.state_space = gym.spaces.Discrete(2)
        self.action_space = gym.spaces.Discrete(len(Agent._BEHAVIOR))

    @property
    def type(self):
        return ThingTypes.AGENT
    
    @property
    def x(self):
        return self._cell.x

    @property
    def y(self):
        return self._cell.y

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
        reward = eval_if_needed(reward, lambda: env.reward_map.get('WAIT', 0.0))
        return Outcomes.DONE, reward
    
    def move_north(self, env, state, initial_reward):
        return self._move('MOVE:NORTH', env, state, initial_reward,
                          Directions.NORTH)

    def move_east(self, env, state, initial_reward):
        return self._move('MOVE:EAST', env, state, initial_reward,
                          Directions.EAST)

    def move_south(self, env, state, initial_reward):
        return self._move('MOVE:SOUTH', env, state, initial_reward,
                          Directions.SOUTH)

    def move_west(self, env, state, initial_reward):
        return self._move('MOVE:WEST', env, state, initial_reward,
                          Directions.WEST)

    def get(self, env, state, initial_reward):
        target = self._cell.portable_object
        if not target:
            reward = find_reward(env, 0.0, 'GET:NO_OBJECT')
        else:
            outcome, reward = target.get(env, state, initial_reward, self,
                                         target)
            if outcome == Outcomes.DONE:
                return outcome, reward

            if self._inventory:
                reward = \
                    eval_if_needed(reward,
                                   lambda: find_reward(env, 0.0, 'GET:FULL')
            else:
                target.container.remove(target)
                target.set_container(self)
                self._inventory = target
                default_reward = \
                    lambda: find_reward(env, 0.0,
                                        'GET:OBJECT[%s]' % target.name,
                                        'GET:OBJECT', 'GET')
                reward = eval_if_needed(reward, default_reward)

        return Outcomes.DONE, reward
    
    def drop(self, env, state, initial_reward):
        if not self._inventory:
            reward = env.reward_map.get('DROP:NO_OBJECT', 0.0)
        else:
            outcome, reward = self._inventory.drop(env, state, initial_reward,
                                                   self, self._inventory)
            
            if self._cell.portable_object:
                reward = env.reward_map.get('DROP:FULL')
            else:
                self._cell.put(target)
                target.set_container(self._cell)
                self.remove(target)
                reward = env.reward_map.get('DROP', reward)

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
        self._inventory = object

    def remove(self, object):
        if self._inventory == object:
            self._inventory = None

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
        outcome, reward = target.push(env, state, initial_reward,
                                      self, target, direction)
        if outcome == Outcome.DONE:
            return outcome, reward

        # Save the current state, then move the actor into the target's
        # cell, followed by the target into the neighboring cell indicated
        # by direction.  If the actor or target fails to move, restore the
        # original state and report failure.
        saved_state = env.save_state()

        outcome, reward = actor.cell.exit_thing(env, state, initial_reward,
                                                actor, direction)
        if outcome == Outcomes.NOT_DONE:
            # Actor failed to move
            return Outcomes.DONE, env.reward_map.get('MOVE:NO_EXIT', 0.0)
        if actor.cell != direction.next_cell(state.grid, target.x, target.y):
            # Actor did not make it into the target cell, so leave object
            # where it is
            return outcome, reward

        outcome, reward = target.cell.exit_thing(env, state, reward,
                                                 target, direction)
        if (outcome == Outcomes.NOT_DONE) or (target.cell == actor.cell):
            # Object didn't move.  Restore original state and exit
            env.restore_state(saved_state)
            return Outcomes.DONE, env.reward_map.get('MOVE:BLOCKED')

        # Both object and actor moved into the expected cells
        reward = env.reward_map.get(behavior_name, reward)
        return Outcomes.DONE, reward
        
Agent._BEHAVIOR = ( Agent.wait, Agent.move_north, Agent.move_south,
                    Agent.move_east, Agent.move_west, Agent.get, Agent.drop,
                    Agent.push_north, Agent.push_east, Agent.push_south,
                    Agent.push_west )
assert len(Agent._BEHAVIOR_NAMES) == len(Agent._BEHAVIOR)
Agent._BEHAVIOR_MAP = dict(zip(Agent.BEHAVIOR_NAMES, Agent._BEHAVIOR))

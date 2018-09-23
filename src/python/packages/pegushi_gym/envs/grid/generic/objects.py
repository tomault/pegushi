"""
Base object classes for the generic gridworld
"""
from pegushi_gum.envs.grid.generic.core import Outcomes, ThingTypes

class Object:
    def __init__(self, name, container, is_portable = False,
                 is_movable = False, is_visible = True, ansi_tile = '?'):
        self._name = name
        self._container = container
        self._is_portable = is_portable
        self._is_movable = is_movable
        self._is_visible = is_visible
        self._ansi_tile = ansi_tile

    @property
    def type(self):
        return ThingTypes.OBJECT

    @property
    def name(self):
        return self._name

    @property
    def container(self):
        return self._container

    @property
    def cell(self):
        return self._container.cell
    
    @property
    def x(self):
        return self._container.x

    @property
    def y(self):
        return self._container.y

    @property
    def is_visible(self):
        return self._is_visible
    
    @property
    def is_portable(self):
        return self._is_portable

    @property
    def is_movable(self):
        return self._is_movable

    def at(self, x, y):
        return (self._x == x) and (self._y == y)

    def ansi_tile(self):
        return self._ansi_tile
    
    def wait_actor(self, env, state, initial_reward, actor):
        return Outcomes.NOT_DONE, initial_reward

    def exit_thing(self, env, state, initial_reward, thing, direction):
        return Outcomes.NOT_DONE, initial_reward

    def enter_thing(self, env, state, initial_reward, thing, origin,
                    direction):
        return Outcomes.NOT_DONE, initial_reward

    def get(self, env, state, initial_reward, actor, target):
        if target == self:
            return self._container.get(env, state, initial_reward, actor,
                                       target)
        else:
            return self._get_other(env, state, initial_reward, actor, target)

    def drop(self, env, state, initial_reward, actor, target):
        if target == self:
            return self._container.get(env, state, initial_reward, actor,
                                       target)
        else:
            return self._drop_other(env, state, initial_reward, actor, target)

    def push(self, env, state, initial_reward, actor, target, direction):
        if target == self:
            return self._container.push(env, state, initial_reward, actor,
                                        target, direction)
        else:
            return self._push_other(env, state, initial_reward, actor, target,
                                    direction)

    # Manipulators
    def set_container(self, c):
        self._container = c

    def _get_other(self, env, state, initial_reward, actor, target):
        return Outcomes.NOT_DONE, initial_reward

    def _drop_other(self, env, state, initial_reward, actor, target):
        return Outcomes.NOT_DONE, initial_reward

    def _push_other(self, env, state, initial_reward, actor, target,
                    direction):
        return Outcomes.NOT_DONE, initial_reward


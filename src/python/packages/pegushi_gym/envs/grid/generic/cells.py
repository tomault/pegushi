"""
Cells for generic gridworlds.
"""

from pegushi_gym.envs.grid.generic.core import Outcomes, ThingTypes
from pegushi_gym.envs.grid.generic.objects import Object

class Cell:
    """Base cell implementation"""
    def __init__(self, grid, x, y, ansi_tile = '.'):
        self._grid = grid
        self._x = x
        self._y = y
        self._inventory = []
        self._portable_object = None
        self._movable_object = None
        self._agent = None
        self._ansi_tile = ansi_tile

    @property
    def type(self):
        return ThingTypes.CELL

    @property
    def container(self):
        return None
    
    @property
    def grid(self):
        return self._grid

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def agent(self):
        return self._agent
    
    @property
    def portable_object(self):
        return self._portable_object

    @property
    def movable_object(self):
        return self._movable_object

    @property
    def inventory(self):
        return self._inventory

    @property
    def objects(self):
        return tuple(x for x in self._inventory if x.type == ThingTypes.OBJECT)

    @property
    def actors(self):
        return tuple(x for x in self._inventory if x.type == ThingTypes.ACTORS)

    def ansi_tile(self):
        return self._ansi_tile
    
    def wait_actor(self, env, state, initial_reward, actor):
        return self._call_objects(Object.wait_actor, env, state,
                                  initial_reward, actor)

    def exit_thing(self, env, state, initial_reward, thing, direction):
        outcome, reward = self._call_objects(Object.exit_thing, env, state,
                                             initial_reward, thing, direction)
        if outcome == Outcomes.DONE:
            return outcome, reward

        destination = direction.next_cell(state.grid, self._x, self._y)
        return destination.enter_thing(env, state, reward, thing,
                                       self, direction.opposite)

    def enter_thing(self, env, state, initial_reward, actor, origin,
                    direction):
        outcome, reward = self._call_objects(Object.enter_thing, env, state,
                                             initial_reward, actor, origin,
                                             direction)
        if outcome == Outcomes.DONE:
            return outcome, reward

        # Move the actor from its current cell into this one
        actor.cell.remove(actor)
        self.put(actor)
        actor.set_cell(self)
        return Outcomes.DONE, initial_reward

    def get(self, env, state, initial_reward, actor, target):
        return self._call_objects(Object.get, env, state, initial_reward,
                                  actor, target, skip = target)

    def drop(self, env, state, initial_reward, actor, target):
        return self._call_objects(Object.drop, env, state, initial_reward,
                                  actor, target, skip = target)

    def push(sef, env, state, initial_reward, actor, target, direction):
        return self._call_objects(Object.get, env, state, initial_reward,
                                  actor, target, skip = target)
    
        return outcomes.DONE, env.reward_map.get('MOVE')
            
    #### Manipulators ###
    def put(self, thing):
        return self._PUT_HANDLER_MAP[thing.type](thing)

    def remove(self, thing):
        if thing.container == self:
            if thing == self._agent:
                self._agent = None
            if thing == self._portable_object:
                self._portable_object = None
            if thing == self._movable_object:
                self._movable_object = None
            self._inventory.remove(thing)
        
    def set_grid(self, g):
        self._grid = g

    def clone(self, x, y):
        return self.__class__(self._grid, x, y)
    
    def _call_objects(self, behavior, env, state, initial_reward, *args,
                      skip = None):
        outcome = Outcomes.NOT_DONE
        reward = initial_reward
        objs = \
            (obj in self._inventory if (obj != skip) and (obj != self._agent))
        for o in objs:
            outcome, reward = behavior(o, env, state, reward, *args)
            if outcome == Outcomes.DONE:
                break
        return outcome, reward

    def _put_agent(self, agent):
        if agent.cell != self:
            self._agent = agent
            self._inventory.append(agent)

    def _put_actor(self, actor):
        if actor.cell != self:
            self._inventory.append(actor)

    def _put_cell(self, cell):
        raise ValueError("Can't put one cell inside another")

    def _put_object(self, obj):
        if obj.container == self:
            return
        if obj.is_portable:
            if self._portable_object:
                raise ValueError('Cell already contains a portable object')
            self._portable_object = obj
        if obj.is_movable(self, obj):
            if self._movable_object:
                raise ValueError('Cell already contains a movable object')
            self._movable_object = obj
        self._inventory.append(obj)

Cell._PUT_HANDLER_MAP = { ThingType.AGENT : Cell._put_agent,
                          ThingType.ACTOR : Cell._put_actor,
                          ThingType.CELL : Cell._put_cell,
                          ThingType.OBJECT : Cell._put_object }

class WallCell(Cell):
    """Cell type representing a wall.  Actors cannot enter this cell and
it cannot contain any objects."""
    def __init__(self, grid, x, y, ansi_tile = '#'):
        Cell.__init__(self, grid, x, y, ansi_tile)
    
    def wait_actor(self, env, state, initial_reward, actor):
        # Nothing should be inside a wall
        return Outcomes.NOT_DONE, initial_reward

    def exit_thing(self, env, state, initial_reward, thing, direction):
        # Neither agents nor actors should be inside a wall, so fail an
        # exit attempt.
        return Outcomes.NOT_DONE, initial_reward

    def enter_thing(self, env, state, initial_reward, actor, origin,
                    direction):
        # Nothing can enter a wall
        return Outcomes.NOT_DONE, initial_reward

    def get(self, env, state, initial_reward, actor, target):
        # Nothing to take
        return Outcomes.NOT_DONE, initial_reward

    def drop(self, env, state, initial_reward, actor, target):
        # Can't drop anything inside a wall.  Report DONE so caller
        # doesn't try to drop anything
        return Outcomes.DONE, env.reward_map.get('DROP:FULL')

    def push(sef, env, state, initial_reward, actor, target, direction):
        # Nothing should be inside the wall
        return Outcomes.NOT_DONE, initial_reward
            
    #### Manipulators ###
    def put(self, thing):
        raise ValueError('Cannot put anything into a wall')

    def remove(self, thing):
        return

class LimboCell(WallCell):
    """Basic implementation of "limbo," a cell that represents "nowhere."
When objects or actors are removed from the grid, they are located here.
Limbo cells have the curious property that they cannot be entered or
left by normal means and always appear to be empty, but can contain actors
and objects nonetheless.  In order to interact with these entities, the
application must use the methods the limbo cell provides for these purposes
rather than the general cell behaviors and properties, which are implemented
to make the cell appear empty (so objects cannot be taken or dropped from it)
and isolated (so actors and objects cannot enter or leave).
"""
    def __init__(self, grid = None):
        WallCell.__init__(grid, -1, -1, ' ')

    @property
    def x(self):
        return -1

    @property
    def y(self):
        return -1

    @property
    def agent(self):
        return None
    
    @property
    def portable_object(self):
        return None

    @property
    def movable_object(self):
        return None

    @property
    def inventory(self):
        return ()

    @property
    def objects(self):
        return ()

    @property
    def actors(self):
        return ()

    @property
    def real_inventory(self):
        return self._inventory
    
    #### Manipulators ###
    def put(self, thing):
        if thing.container != self:
            self._invnetory.append(thing)

    def remove(self, thing):
        if thing.container == self:
            self._inventory.remove(thing)

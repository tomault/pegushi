"""Generic gridworld environments

A generic grid-world environment consists of:
  * An agent, which occupies a location on the grid
  * A rectangular 2D grid
  * A set of objects, which occupy (possibly overlapping) locations on the grid.
  * A set of actions, which allow the agent to interact with the grid and
    the objects contained within

The agent, cells and objects expose behaviors, which query and potentially 
modify the environment.  Examples of behaviors include the agent's MOVE_EAST
behavior (which moves the agent one square east) and a cell's GET behavior
(which reacts to an actor attempting to pick up a portable object contained
in the cell).  The agent's behaviors define the environment's actions and (at 
least in the current iteration of the generic gridworld) do not take arguments.
The agent's behaviors invoke the behaviors of cells and objects as part of
their implementation.  For example, the MOVE_EAST behavior invokes the
EXIT behavior of the cell the agent occupies and the ENTER behavior of the
cell to the agent's east.  Unlike agent behaviors, the behaviors of cells
and objects may take arguments.  The cell and object behaviors will
implement certains parts of the overall action (for example, a cell's
EXIT behavior will remove the agent from the cell's contents) and may block
or alter aspects of the agent's behavior (for example, an object may prevent
the agent from exiting the cell in a certain direction until it is removed).

All behaviors return a reward and an optional exception token.  The exception
token indicates something unusual occured that prevented the normal completion
of the behavior.  The invoking behavior should take note of this condition
and behave accordingly.  Behaviors that complete normally do not return an
exception token.

In the baseline generic gridworld, behaviors provided by the agent map
one-to-one to the actions the agent may take in the environment, so these
behaviors will not have arguments. However, extensions to the generic
gridworld may add arguments to the agent's actions, resulting in a
parameterized action space.  This no-argument limitation imposes some
constraints on the generic gridworld's modeling capabilities:
  * The agent may only carry one object at a time, eliminating any ambiguity
    about the target of the agent's DROP or USE behaviors.  Objects the agent
    may carry are called "portable objects."
  * Each cell may only contain one portable object at a time, eliminating
    any ambiguity in the target of the agent's GET behavior.
  * Objects the agent may push from cell to cell but not pick up are called
    "movable" objects.  Each cell may contain only one movable object,
    eliminating any ambiguity in the target of the PUSH behavior.

In contrast, The behaviors of grid cells and objects are parameterized, to
allow the agent behavior to specify the target of the behavior, if a target
is needed.

The agent in the generic gridworld provides the following behaviors:

  * MOVE_{NORTH,EAST,SOUTH,WEST}
    * Move one step along the grid in the given direction.
  * GET
    * Transfer the portable object in the agent's cell to the agent's
      inventory by invoking the cell's GET behavior to transfer the cell's
      portable object stack, and then popping that object into the agent's
      inventory.  Fails if the agent is already carrying an object or
      if the cell's GET behavior fails.  Reward is equal to the reward
      returned by the cell's GET behavior.
  * DROP
    * Invokes the DROP behavior of the cell the agent occupies on the
      object the agent is carrying to transfer the object from the agent's
      inventory to that cell.  Fails if the agent is not carrying an object
      or if the cell's DROP behavior fails.  Reward is equal to the reward
      returned by the cell's DROP behavior.
  * USE
    * Invokes the USE behavior of the object the agent is carrying and
      returns the result of that behavior.  Fails if the agent is not
      carrying an object.
  * PUSH_{NORTH,EAST,SOUTH,WEST}
    * Push the object in the adjoining cell in the given direction, causing
      both the agent and the object to move one cell in that direction.  The
      adjoining cell must contain a movable object, the agent must be able
      to exit its current cell in the given direction and enter the next
      cell from the opposite direction (as if it executed the appropriate
      move action) and the object must be able to leave its cell and enter
      its neighboring cell along the same direction.  If any of these
      conditions fails, the PUSH behavior fails.

The cells in the generic gridworld provide the following behaviors:
  * EXIT actor direction
    * Called when an actor (e.g. the agent) leaves the cell headed in the
      given direction.  Calls the EXIT behavior of every object in the
      cell and fails if any of them fail.  Removes the actor from the
      cell's contents.
  * ENTER actor direction
    * Called when an actor enters the cell from the given direction to allow
      the cell to react to the entry of that actor.  The default implementation
      calls the ENTER behavior of every object in the cell, fails if any
      of them fail and adds the actor to the cell's contents if they
      all return CONTINUE.
  * GET actor object
    * Called to remove the given object from the cell and push it onto the
      object stack, invoking the GET behavior on each object contained in
      the cell first.  The GET behavior is invoked on every object except
      the target object first, followed by the GET behavior of the target
      object.  eails if the object is not contained in the cell or if any
      of the GET behaviors fail.
  * DROP actor object
    * Called to place the given object into the cell.  Prior to placing the
      object in the cell, this behavior invokes the DROP behavior on each
      object in the cell, followed by the object's own DROP behavior

Objects provide the following behaviors
  * ENTER thing direction
    * Called when an actor (typically the agent) or an object attempts to
      enter the cell occupied by this object from the given direction (in
      the object's case, this means the object is being pushed).  The default
      implementation of this behavior does nothing, but individual objects
      may use this behavior to prevent the entry of actors or objects or
      to intercept actors or objects and send them elsewhere.
  * EXIT thing direction
    * Same as ENTER, but called when an actor or an object (because it is
      being pushed) leaves the cell this object occupies.
  * GET actor object
    * Called when an actor (typically the agent) attempts to pick up an
      object in a cell.  The default implementation of this behavior does
      nothing, but objects can provide implementations that permit themselves
      to be picked up only under certain circumstances or prevent other
      objects from being picked up and so on.
  * DROP actor object
    * Same as GET but called when an actor attempts to place a portable
      object inside the cell occupied by this object.
  * USE actor
    * Invoked when an actor attempts to use this object.  The default
      implementation always fails, but individual objects can override
      this behavior to make themselves usable.
"""    


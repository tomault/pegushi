"""Unit tests for pegushi_gym.envs.maze"""
from pegushi_gym.envs.maze import *
from unittest import TestCase
from unittest import main as unit_test_main
import numpy as np
import os.path
import sys

RESOURCE_DIR = ''
AGENT_IMAGE_FILE = ''

class RandomMazeGenerationTests(TestCase):
    def test_generate_maze_with_kruskal(self):
        truth = np.asarray([ 3, 3, 3, 2, 2, 0, 2, 0, 0, 1, 1, 0 ])\
                  .reshape((3, 4))
        layout = generate_random_maze(4, 3, 'kruskal', seed = 42)
        self.assertEqual(truth.shape, layout.shape)
        if not np.array_equal(truth, layout):
            msg = '%s is not equal to\n%s' % (repr(truth), repr(layout))
            self.fail(msg)

class FixedMazeEnvironmentTests(TestCase):
    def setUp(self):
        self.maze = FixedMazeEnvironment(width = 4, height = 3, seed = 42)

    def test_create_from_layout(self):
        layout = np.asarray([ 1, 3, 3, 2, 2, 0, 2, 0, 1, 1, 1, 0 ])\
                   .reshape((3, 4))
        start = (1, 2)
        goal = (3, 2)
        seed = 42
        max_steps = 15

        maze = FixedMazeEnvironment(layout = layout, start = start, goal = goal,
                                    seed = seed, max_steps = max_steps)
        self.assertTrue(np.array_equal(layout, maze._layout))
        self.assertEqual(seed, maze.seed)
        self.assertIsNotNone(maze.rng)
        self.assertEqual(start, maze.start)
        self.assertEqual(goal, maze.goal)
        self.assertEqual(max_steps, maze.max_steps)
        self.assertEqual(start, maze.current_state)
        self.assertEqual(0, maze.tick)

    def test_create_random_layout(self):
        true_layout = np.asarray([ 3, 3, 3, 2, 2, 0, 2, 0, 0, 1, 1, 0 ])\
                        .reshape((3, 4))
        true_start = (0, 0)
        true_goal = (3, 2)
        seed = 42

        maze = FixedMazeEnvironment(width = 4, height = 3, seed = seed)
        if not np.array_equal(true_layout, maze._layout):
            msg = \
                '%s\nis not equal to\n%s' % (repr(true_layout),
                                             repr(maze._layout))
            self.fail(msg)
        self.assertEqual(seed, maze.seed)
        self.assertEqual(true_start, maze.start)
        self.assertEqual(true_goal, maze.goal)
        self.assertEqual(true_start, maze.current_state)

    def test_create_random_layout_goal_and_start_incident(self):
        true_layout = np.asarray([ 3, 3, 3, 2, 2, 0, 2, 0, 0, 1, 1, 0 ])\
                        .reshape((3, 4))
        true_goal = (3, 2)
        true_start = (3, 0)
        seed = 42

        # The randomly-generated goal will be (3, 2), which is the same
        # as the start, so the constructor will displace the start to
        # a random loc
        maze = FixedMazeEnvironment(width = 4, height = 3, seed = seed,
                                    start = true_goal)
        if not np.array_equal(true_layout, maze._layout):
            msg = \
                '%s\nis not equal to\n%s' % (repr(true_layout),
                                             repr(maze._layout))
            self.fail(msg)
        self.assertEqual(seed, maze.seed)
        self.assertEqual(true_start, maze.start)
        self.assertEqual(true_goal, maze.goal)
        self.assertEqual(true_start, maze.current_state)

    def test_move_north(self):
        state, reward, done, _ = self.maze.step(0)
        self.assertEqual((0, 1), state)
        self.assertEqual(-1.0, reward)
        self.assertFalse(done)

        self.assertEqual((0, 1), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_north_into_wall(self):
        self.maze.teleport(1, 1)
        state, reward, done, _ = self.maze.step(0)

        self.assertEqual((1, 1), state)
        self.assertEqual(-5.0, reward)
        self.assertFalse(done)

        self.assertEqual((1, 1), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)
        
    def test_move_east(self):
        state, reward, done, _ = self.maze.step(1)
        self.assertEqual((1, 0), state)
        self.assertEqual(-1.0, reward)
        self.assertFalse(done)

        self.assertEqual((1, 0), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_east_into_wall(self):
        self.maze.teleport(2, 1)
        state, reward, done, _ = self.maze.step(1)

        self.assertEqual((2, 1), state)
        self.assertEqual(-5.0, reward)
        self.assertFalse(done)

        self.assertEqual((2, 1), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)
                
    def test_move_south(self):
        self.maze.teleport(2, 2)
        state, reward, done, _ = self.maze.step(2)

        self.assertEqual((2, 1), state)
        self.assertEqual(-1.0, reward)
        self.assertFalse(done)

        self.assertEqual((2, 1), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_south_into_wall(self):
        self.maze.teleport(1, 2)
        state, reward, done, _ = self.maze.step(2)

        self.assertEqual((1, 2), state)
        self.assertEqual(-5.0, reward)
        self.assertFalse(done)

        self.assertEqual((1, 2), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_south_into_lower_border(self):
        state, reward, done, _ = self.maze.step(2)

        self.assertEqual((0, 0), state)
        self.assertEqual(-5.0, reward)
        self.assertFalse(done)

        self.assertEqual((0, 0), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_west(self):
        self.maze.teleport(2, 2)
        state, reward, done, _ = self.maze.step(3)

        self.assertEqual((1, 2), state)
        self.assertEqual(-1.0, reward)
        self.assertFalse(done)

        self.assertEqual((1, 2), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_west_into_wall(self):
        self.maze.teleport(1, 2)
        state, reward, done, _ = self.maze.step(3)

        self.assertEqual((1, 2), state)
        self.assertEqual(-5.0, reward)
        self.assertFalse(done)

        self.assertEqual((1, 2), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_west_into_lower_border(self):
        state, reward, done, _ = self.maze.step(3)

        self.assertEqual((0, 0), state)
        self.assertEqual(-5.0, reward)
        self.assertFalse(done)

        self.assertEqual((0, 0), self.maze.current_state)
        self.assertEqual(1, self.maze.tick)

    def test_move_to_goal(self):
        maze = FixedMazeEnvironment(width = 4, height = 3, seed = 42,
                                    start = (2, 2), goal = (3, 2))
        state, reward, done, _ = maze.step(1)
        self.assertEqual((3, 2), state)
        self.assertEqual(100.0, reward)
        self.assertTrue(done)

    def test_move_into_space_with_time_limit_exceeded(self):
        maze = FixedMazeEnvironment(width = 4, height = 3, seed = 42,
                                    goal = (3, 2), max_steps = 1)
        state, reward, done, _ = maze.step(0)
        self.assertEqual((0, 1), state)
        self.assertEqual(-1.0, reward)
        self.assertTrue(done)

    def test_move_into_wall_with_time_limit_exceeded(self):
        maze = FixedMazeEnvironment(width = 4, height = 3, seed = 42,
                                    goal = (3, 2), max_steps = 1)
        state, reward, done, _ = maze.step(2)
        self.assertEqual((0, 0), state)
        self.assertEqual(-5.0, reward)
        self.assertTrue(done)

    def test_reset(self):
        self.maze.step(1)
        self.maze.step(1)
        self.maze.step(0)

        self.assertEqual((2, 1), self.maze.current_state)
        self.assertEqual(3, self.maze.tick)

        self.assertEqual((0, 0), self.maze.reset())
        self.assertEqual((0, 0), self.maze.current_state)
        self.assertEqual(0, self.maze.tick)

    def test_render_to_ansi(self):
        truth = """*********
* *    $*
* *** ***
* * * * *
* * * * *
*#      *
*********"""
        self.assertEqual(truth, self.maze.render('ansi'))

#    def test_render_human(self):
#        maze = FixedMazeEnvironment(width = 4, height = 3, seed = 42,
#                                    start = (0, 0), goal = (3, 2),
#                                    agent_image = AGENT_IMAGE_FILE)
#        actions = (0, 0, 2, 2, 1, 1, 0, 0, 3, 1, 1)
#        maze.render('human')
#        time.sleep(1)
#        for a in actions:
#            maze.step(a)
#            maze.render('human')
#            time.sleep(1)
#        maze.close()
        
    def test_compute_solution_path(self):
        maze = FixedMazeEnvironment(width = 4, height = 3, seed = 42,
                                    start = (0, 0), goal = (3, 2))
        truth = ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2))
        self.assertEqual(truth, maze.compute_solution_path())

    def test_compute_solution_length(self):
        maze = FixedMazeEnvironment(width = 4, height = 3, seed = 42,
                                    start = (0, 0), goal = (3, 2))
        self.assertEqual(5, maze.compute_solution_length())

def full_split(path):
    if path == '/':
        return (path, )
    a, b = os.path.split(path)
    if a and b:
        return full_split(a) + (b, )
    elif a:
        return full_split(a)
    elif b:
        return (b, )
    else:
        return ()
    
def set_resource_dir():
    global RESOURCE_DIR
    full_script_path = full_split(os.path.abspath(sys.argv[0]))[0:-5]
    full_script_path = full_script_path + ('resources', )
    RESOURCE_DIR = os.path.join(*full_script_path)

def set_image_files():
    global AGENT_IMAGE_FILE
    AGENT_IMAGE_FILE = os.path.join(RESOURCE_DIR, 'penguin24x24.png')
    
if __name__ == '__main__':
    set_resource_dir()
    set_image_files()
    print RESOURCE_DIR
    print AGENT_IMAGE_FILE
    unit_test_main()



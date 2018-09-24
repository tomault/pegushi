"""Pyglet implementation of maze"""
from pegushi_gym.envs.maze import generate_random_maze
import pyglet
import pyglet.clock
import time

maze = generate_random_maze(width = 4, height = 3, seed = 42)
path = ((0, 0), (2, 0), (2, 2), (3, 2))
path_pixels = tuple(((2 * x + 1) * 24, (2 * y + 1) * 24) for (x, y) in path)

window = pyglet.window.Window(width = 24 * 9, height = 24 * 7, vsync = False)
window.config.alpha_size = 8

pyglet.resource.path =  [ '/home/tomault/projects/pegushi-git/src/resources' ]
pyglet.resource.reindex()

background = pyglet.image.SolidColorImagePattern((255,255,255,255))\
                 .create_image(window.width, window.height)
wall_block = pyglet.image.SolidColorImagePattern((0, 0, 0, 255))\
                 .create_image(24, 24)
pegu = pyglet.resource.image('penguin24x24.png')

def blit_walls(*coords):
    for c in coords:
        wall_block.blit(*c)

def draw_both_walls(x, y):
    blit_walls((x, y + 24), (x + 24, y), (x + 24, y + 24))

def draw_north_wall(x, y):
    blit_walls((x, y + 24), (x + 24, y + 24))

def draw_east_wall(x, y):
    blit_walls((x + 24, y), (x + 24, y + 24))

def draw_both_open(x, y):
    blit_walls((x + 24, y + 24))

def sgn(v):
    if v < 0:
        return -1
    elif v > 0:
        return 1
    return 0

wall_renderers = [ draw_both_walls, draw_north_wall, draw_east_wall,
                   draw_both_open ]

def draw_maze():
    for x in xrange(0, 9 * 24, 24):
        wall_block.blit(x, 0)
        
    for j in xrange(0, maze.shape[0]):
        y = 24 + j * 48
        wall_block.blit(0, y)
        wall_block.blit(0, y + 24)
        for i in xrange(0, maze.shape[1]):
            wall_renderers[maze[j, i]](24 + i * 48, y)
        
@window.event
def on_draw():
    global num_frames, pegu_x, pegu_y
    window.clear()
    
    pyglet.gl.glDisable(pyglet.gl.GL_BLEND)
    background.blit(0, 0)

    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,
                          pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    draw_maze()
    pegu.blit(pegu_x, pegu_y)
    num_frames += 1

@window.event
def on_close():
    global go
    go = False

def update():
    global pegu_x, pegu_y, next_path
    if next_path < len(path_pixels):
        dest_x, dest_y = path_pixels[next_path]
        pegu_x += sgn(dest_x - pegu_x)
        pegu_y += sgn(dest_y - pegu_y)
        if ((pegu_x == dest_x) and (pegu_y == dest_y)):
            next_path += 1
        
# pyglet.app.run()
go = True
num_frames = 0
num_loops = 0
next_update_time = 0
next_update_delta = 1.0/240.0
(pegu_x, pegu_y) = path_pixels[0]
next_path = 1

pyglet.gl.glPushMatrix()

while go:
    window.switch_to()
    window.dispatch_events()
    now = time.time()
    if now >= next_update_time:
        update()
        window.dispatch_event('on_draw')
        window.flip()
        next_update_time = now + next_update_delta
    num_loops += 1
print num_frames, num_loops

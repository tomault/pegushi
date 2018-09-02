import pygame
from pegushi_gym.envs.maze import generate_random_maze

def main():
    def blit_blocks(*coords):
        for c in coords:
            screen.blit(block_img, c)

    def draw_all_walls(x, y):
        blit_blocks((x, y), (x + block_size, y),
                    (x + block_size, y + block_size))

    def draw_north_wall(x, y):
        blit_blocks((x, y), (x + block_size, y))

    def draw_east_wall(x, y):
        blit_blocks((x + block_size, y), (x + block_size, y + block_size))

    def draw_both_open(x, y):
        blit_blocks((x + block_size, y))

    def sgn(v):
        if v > 0:
            return 1
        elif v < 0:
            return -1
        else:
            return 0

    pygame.init()

    block_size = 24
    maze = generate_random_maze(width = 4, height = 3, seed = 42)
    
    pegu_img = pygame.image.load("/home/tomault/Downloads/penguin24x24.png")
    block_img = pygame.Surface((block_size, block_size))
    block_img.fill((0, 0, 0))

    goal_img = pygame.Surface((block_size, block_size))
    goal_img.fill((0, 192, 0))

    pegu_blank = pygame.Surface((block_size, block_size))
    pegu_blank.fill((255, 255, 255))

    wall_renderers = [ draw_all_walls, draw_north_wall, draw_east_wall,
                       draw_both_open ]
    pygame.display.set_caption("minimal program")

    screen = pygame.display.set_mode((9 * block_size, 7 * block_size))
    screen.fill((255, 255, 255))

    for (j, y) in zip(xrange(maze.shape[0] - 1, -1, -1),
                      xrange(0, 2 * maze.shape[0] * block_size,
                             2 * block_size)):
        blit_blocks((0, y), (0, y + block_size))
        for (i, x) in zip(xrange(0, maze.shape[1]),
                          xrange(block_size,
                                 (2 * maze.shape[1] + 1) * block_size,
                                 2 * block_size)):
            wall_renderers[maze[j, i]](x, y)
    y = 2 * maze.shape[0] * block_size
    for x in xrange(0, (2 * maze.shape[1] + 1) * block_size, block_size):
        screen.blit(block_img, (x, y))

    screen.blit(pegu_img, (block_size, (2 * maze.shape[0] - 1) * block_size))
    screen.blit(goal_img, (block_size * 7, block_size))
    pygame.display.flip()

    path = ((0, 0), (2, 0), (2, 2), (3, 2))
    path_pixels = tuple(((2 * x + 1) * block_size, (5 - 2 * y) * block_size) for (x, y) in path)
    running = True
    (x, y) = path_pixels[0]
    next_path = 1
    print 'Move from (%d, %d) to (%d, %d)' % (x, y, path_pixels[1][0],
                                              path_pixels[1][1])

    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if next_path < len(path_pixels):
            screen.blit(pegu_blank, (x, y))
            x += sgn(path_pixels[next_path][0] - x)
            y += sgn(path_pixels[next_path][1] - y)
            screen.blit(goal_img, (block_size * 7, block_size))
            screen.blit(pegu_img, (x, y))
            pygame.display.flip()
            if (x == path_pixels[next_path][0]) and (y == path_pixels[next_path][1]):
                next_path += 1
                if next_path < len(path_pixels):
                    print 'Move from (%d, %d) to (%d, %d)' % (x, y, path_pixels[next_path][0], path_pixels[next_path][1])
            clock.tick(480)

            
            

if __name__ == '__main__':
    main()


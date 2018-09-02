from gym.envs.registration import register
import pygame

pygame.init()
register(id='pegushi-v1', entry_point='pegushi_gym.envs:FixedMazeEnvironment')


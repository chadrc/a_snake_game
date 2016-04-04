import sys
import pygame
from pygame.locals import *

__author__ = 'Chad Collins'

pygame.init()

FPS = 30
clock = pygame.time.Clock()

display_surface = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Pyventure')


class Color(object):
    @staticmethod
    def black():
        return 0, 0, 0

    @staticmethod
    def white():
        return 255, 255, 255

    @staticmethod
    def red():
        return 255, 0, 0

    @staticmethod
    def green():
        return 0, 255, 0

    @staticmethod
    def red():
        return 0, 0, 255


class SerpentBlock:
    def __init__(self, serpent, parent=None):
        self.leader = parent
        if parent is None:
            self.x = 100
            self.y = 100
        else:
            self.x = parent.x
            self.y = parent.y + parent.size

        self.serpent = serpent
        self.dir_x = 0
        self.dir_y = -1
        self.size = 10
        self.turn_count = 0

    def turn(self, dir_x, dir_y):
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.turn_count += 1

    def update(self):
        if self.turn_count < len(self.serpent.turn_points):
            turn_point = self.serpent.turn_points[self.turn_count]
            if self.x == turn_point['x'] and self.y == turn_point['y']:
                self.turn(turn_point['dir_x'], turn_point['dir_y'])
        self.x += self.dir_x * self.serpent.speed
        self.y += self.dir_y * self.serpent.speed

    def draw(self):
        pygame.draw.rect(display_surface, Color.black(), (self.x, self.y, self.size - 1, self.size - 1))


class Serpent:
    def __init__(self):
        self.speed = 2
        self.turn_points = []
        self.objects = []
        self.head = SerpentBlock(self)
        self.objects.append(self.head)
        for i in range(0, 10):
            new_snake = SerpentBlock(self, self.objects[len(self.objects) - 1])
            self.objects.append(new_snake)

    def draw(self):
        for o in self.objects:
            o.draw()

    def update(self):
        for o in self.objects:
            o.update()

    def add_turn_point(self, dir_x, dir_y):
        self.turn_points.append(dict(x=self.head.x, y=self.head.y, dir_x=dir_x, dir_y=dir_y))


# Game Setup
serpent = Serpent()
objects = {serpent}

# previous_time = 0
# delta_time = 0

# Game Loop
while True:
    display_surface.fill(Color.white())

    for obj in objects:
        obj.update()
        obj.draw()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == pygame.K_UP:
                serpent.add_turn_point(dir_x=0, dir_y=-1)
            elif event.key == pygame.K_DOWN:
                serpent.add_turn_point(dir_x=0, dir_y=1)
            elif event.key == pygame.K_LEFT:
                serpent.add_turn_point(dir_x=-1, dir_y=0)
            elif event.key == pygame.K_RIGHT:
                serpent.add_turn_point(dir_x=1, dir_y=0)

    pygame.display.update()
    clock.tick(FPS)
    # delta_time = pygame.time.get_ticks() - previous_time
    # previous_time = pygame.time.get_ticks()

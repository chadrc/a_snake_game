import sys
import pygame
import random
from pygame.locals import *

__author__ = 'Chad Collins'

pygame.init()

FPS = 30
clock = pygame.time.Clock()

GameWidth = 300
GameHeight = 650

display_surface = pygame.display.set_mode((GameWidth, GameHeight))
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


class GameObject(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def draw(self):
        pass

    def update(self):
        pass


class Block(GameObject):
    def __init__(self):
        super(Block, self).__init__()
        self.width = 9
        self.height = 9

    def draw(self):
        pygame.draw.rect(display_surface, Color.black(), (self.x, self.y, self.width, self.height))

    def update(self):
        pass

    def hit_test_point(self, x, y):
        return self.x <= x <= (self.x + self.width) and self.y <= y <= (self.y + self.height)

    def hit_test_block(self, test_block):
        return self.hit_test_point(test_block.x, test_block.y) \
               or self.hit_test_point(test_block.x, test_block.y + test_block.height) \
               or self.hit_test_point(test_block.x + test_block.width, test_block.y) \
               or self.hit_test_point(test_block.x + test_block.width, test_block.y + test_block.height)


class SerpentBlock(Block):
    def __init__(self, owner=None, parent=None):
        super(SerpentBlock, self).__init__()
        self.leader = parent
        if parent is None:
            self.x = 100
            self.y = 100
            self.dir_x = 0
            self.dir_y = 0
            self.turn_count = 0
        else:
            self.x = parent.x
            if self.leader.dir_x != 0:
                self.x += (self.leader.width+1) * -self.leader.dir_x
            self.y = parent.y
            if self.leader.dir_y != 0:
                self.y += (self.leader.height+1) * -self.leader.dir_y
            self.dir_x = self.leader.dir_x
            self.dir_y = self.leader.dir_y
            self.turn_count = parent.turn_count

        self.owner = owner

    def turn(self, dir_x, dir_y):
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.turn_count += 1

    def update(self):
        if self.turn_count < len(self.owner.turn_points):
            turn_point = self.owner.turn_points[self.turn_count]
            if self.x == turn_point['x'] and self.y == turn_point['y']:
                self.turn(turn_point['dir_x'], turn_point['dir_y'])
        self.x += self.dir_x * self.owner.speed
        self.y += self.dir_y * self.owner.speed


class Serpent(GameObject):
    def __init__(self):
        super(Serpent, self).__init__()
        self.speed = 2
        self.turn_points = []
        self.blocks = []
        self.head = SerpentBlock(self)
        self.head.dir_y = 1
        self.blocks.append(self.head)
        for i in range(0, 3):
            self.add_block()

    def draw(self):
        for o in self.blocks:
            o.draw()

    def update(self):
        for o in self.blocks:
            o.update()

    def add_block(self):
        new_snake = SerpentBlock(self, self.blocks[len(self.blocks) - 1])
        self.blocks.append(new_snake)
        print("block added")

    def add_turn_point(self, dir_x, dir_y):
        self.turn_points.append(dict(x=self.head.x, y=self.head.y, dir_x=dir_x, dir_y=dir_y))


# Game Setup
serpent = Serpent()
objects = [GameObject(), serpent]

collectables = []

for i in range(0, 10):
    randX = random.randrange(GameWidth)
    randY = random.randrange(GameHeight)
    block = Block()
    block.x = randX
    block.y = randY
    collectables.append(block)
    objects.append(block)

# previous_time = 0
# delta_time = 0

# Game Loop
while True:
    display_surface.fill(Color.white())

    for obj in objects:
        obj.update()
        obj.draw()

    # Check for serpent collisions with collectables
    to_remove = None
    for col in collectables:
        if col.hit_test_block(serpent.head):
            to_remove = col
            serpent.add_block()
            break

    if to_remove is not None:
        collectables.remove(to_remove)
        objects.remove(to_remove)

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

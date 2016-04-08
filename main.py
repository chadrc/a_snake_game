import sys
import pygame
import random
import math
import collections
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
    def blue():
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
    def __init__(self, x=0, y=0, width=0, height=0):
        super(Block, self).__init__(x, y)
        self.width = width
        self.height = height

    def draw(self):
        pygame.draw.rect(display_surface, Color.black(), (self.x, self.y, self.width, self.height))

    def update(self):
        pass

    def distance_to(self, b):
        x = self.x - b.x
        y = self.y - b.y
        return math.sqrt(x*x + y*y)

    def distance_to_point(self, x, y):
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx*dx + dy*dy)

    def hit_test_point(self, x, y):
        return self.x <= x <= (self.x + self.width) and self.y <= y <= (self.y + self.height)

    def hit_test_block(self, test_block):
        return self.hit_test_point(test_block.x, test_block.y) \
               or self.hit_test_point(test_block.x, test_block.y + test_block.height) \
               or self.hit_test_point(test_block.x + test_block.width, test_block.y) \
               or self.hit_test_point(test_block.x + test_block.width, test_block.y + test_block.height)


class ScrollingBlock(Block):
    def __init__(self):
        super(ScrollingBlock, self).__init__()
        self.width = 9
        self.height = 9

    def update(self):
        self.y += game.scroll_speed * delta_time


class SerpentBlock(Block):
    def __init__(self, owner=None, parent=None):
        super(SerpentBlock, self).__init__()
        self.width = 9
        self.height = 9
        self.leader = parent
        self.follower = None
        self.path = collections.deque()
        if parent is None:
            self.x = 100
            self.y = 100
            self.dir_x = 0
            self.dir_y = 0
            self.turn_count = 0
        else:
            self.leader.follower = self
            self.x = parent.x
            if self.leader.dir_x != 0:
                self.x = parent.x + (self.leader.width+1) * -self.leader.dir_x
            self.y = parent.y
            if self.leader.dir_y != 0:
                self.y += (self.leader.height+1) * -self.leader.dir_y
            self.dir_x = self.leader.dir_x
            self.dir_y = self.leader.dir_y
            self.turn_count = parent.turn_count

        self.lasttp = None
        self.last_x = self.x
        self.last_y = self.y
        self.owner = owner

    def turn(self, dir_x, dir_y):
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.turn_count += 1
        if self.leader is not None:
            self.x = self.leader.x
            if self.leader.dir_x != 0:
                self.x = self.leader.x + (self.leader.width+1) * -self.leader.dir_x
            self.y = self.leader.y
            if self.leader.dir_y != 0:
                self.y += (self.leader.height+1) * -self.leader.dir_y

    def update(self):
        self.last_x = self.x
        self.last_y = self.y

        # if self.turn_count < len(self.owner.turn_points):
        #     turn_point = self.owner.turn_points[self.turn_count]
        #     if self.dir_x == -1 and self.x <= turn_point['x'] or \
        #         self.dir_x == 1 and self.x >= turn_point['x'] or \
        #         self.dir_y == -1 and self.y <= turn_point['y'] or \
        #         self.dir_y == 1 and self.y >= turn_point['y']:
        #         self.turn(turn_point['dir_x'], turn_point['dir_y'])
        self.x += self.dir_x * float(self.owner.speed) * delta_time
        self.y += self.dir_y * float(self.owner.speed) * delta_time

        lasttp = None if self.turn_count == 0 or self.turn_count-1 >= len(self.owner.turn_points) \
            else self.owner.turn_points[self.turn_count-1]
        dist = 0 if lasttp is None else self.distance_to_point(lasttp['x'], lasttp['y'])
        if lasttp is None or dist >= 10:
            child_x = self.x + ((self.width+1) * -self.dir_x)
            child_y = self.y + ((self.height+1) * -self.dir_y)
        else:
            x_dif = self.x - lasttp['x']
            y_dif = self.y - lasttp['y']
            child_x = -x_dif + (10 - math.fabs(y_dif)) * -lasttp['from_dir_x']
            child_y = -y_dif + (10 - math.fabs(x_dif)) * -lasttp['from_dir_y']
            child_x += self.x
            child_y += self.y

        if self.follower is not None:
            # self.follower.update()
            old_dir_x = self.follower.dir_x
            old_dir_y = self.follower.dir_y
            self.follower.move(child_x, child_y)
            if self.follower.dir_x != old_dir_x or self.follower.dir_y != old_dir_y:
                self.follower.lasttp = lasttp
            self.follower.move_child()

    def move(self, x, y):
        dif_x = self.x - x
        dif_y = self.y - y

        if dif_x > 0:
            self.dir_x = -1
        elif dif_x < 0:
            self.dir_x = 1
        else:
            self.dir_x = 0

        if dif_y > 0:
            self.dir_y = -1
        elif dif_y < 0:
            self.dir_y = 1
        else:
            self.dir_y = 0

        self.x = x
        self.y = y

    def move_child(self):
        dist = 0 if self.lasttp is None else self.distance_to_point(self.lasttp['x'], self.lasttp['y'])
        if self.lasttp is None or dist >= 10:
            child_x = self.x + ((self.width+1) * -self.dir_x)
            child_y = self.y + ((self.height+1) * -self.dir_y)
        else:
            x_dif = self.x - self.lasttp['x']
            y_dif = self.y - self.lasttp['y']
            child_x = -x_dif + (10 - math.fabs(y_dif)) * -self.lasttp['from_dir_x']
            child_y = -y_dif + (10 - math.fabs(x_dif)) * -self.lasttp['from_dir_y']
            child_x += self.x
            child_y += self.y

        if self.follower is not None:
            old_dir_x = self.follower.dir_x
            old_dir_y = self.follower.dir_y
            self.follower.move(child_x, child_y)
            if self.follower.dir_x != old_dir_x or self.follower.dir_y != old_dir_y:
                self.follower.lasttp = self.lasttp
            self.follower.move_child()


class Serpent(GameObject):
    def __init__(self, start_blocks):
        super(Serpent, self).__init__()
        self.speed = .2
        self.turn_points = []
        self.blocks = []
        self.head = SerpentBlock(self)
        self.head.dir_y = 1
        self.blocks.append(self.head)
        for i in range(0, start_blocks-1):
            self.add_block()

    def draw(self):
        for o in self.blocks:
            o.draw()

    def update(self):
        self.head.update()

    def add_block(self):
        new_snake = SerpentBlock(self, self.blocks[len(self.blocks) - 1])
        self.blocks.append(new_snake)

    def add_turn_point(self, dir_x, dir_y):
        self.turn_points.append(dict(x=self.head.x, y=self.head.y, dir_x=dir_x, dir_y=dir_y,
                                     from_dir_x=self.head.dir_x, from_dir_y=self.head.dir_y))
        self.head.turn(dir_x, dir_y)

    def length(self):
        return len(self.blocks)

    def hit_self(self):
        child = self.head.follower
        while child is not None:
            if self.head.distance_to(child) < 5:
                return True
            child = child.follower
        return False


class Game:
    def __init__(self):
        self.scroll_speed = 10

        self.serpent_start_blocks = 3
        self.serpent = Serpent(self.serpent_start_blocks)
        self.serpent_start_speed = 50
        self.serpent.speed = self.serpent_start_speed
        self.serpent.head.dir_y = -1
        self.serpent.head.x = GameWidth/2 - self.serpent.head.width/2
        self.serpent.head.y = GameHeight - 200

        self.speed_increase_per_second = .1
        self.objects = [GameObject(), self.serpent]
        self.spawn_range = 100
        self.spawn_time = self.spawn_range / self.scroll_speed
        self.spawn_timer = 0
        self.collectibles = []

        for i in range(0, 10):
            range_x = GameWidth/10
            range_y = (GameHeight/2)/10
            rand_x = random.randrange(range_x)
            rand_y = random.randrange(range_y)
            block = ScrollingBlock()
            block.x = rand_x * 10
            block.y = rand_y * 10
            self.collectibles.append(block)
            self.objects.append(block)

        self.score = 0
        self.multiplier = 1.0
        self.score_per_second = 1.0

    def update(self):
        self.spawn_timer += delta_time
        self.serpent.speed += self.speed_increase_per_second * delta_time
        self.scroll_speed += self.speed_increase_per_second * delta_time

        # Score Calculation
        base_score = self.score_per_second * delta_time
        self.score += base_score * self.multiplier

        if self.spawn_timer >= self.spawn_time:
            for i in range(0, 5):
                range_x = GameWidth/10
                range_y = self.spawn_range/10
                rand_x = random.randrange(range_x)
                rand_y = -random.randrange(range_y)
                block = ScrollingBlock()
                block.x = rand_x * 10
                block.y = rand_y * 10
                self.collectibles.append(block)
                self.objects.append(block)
            self.spawn_timer = 0

        for obj in self.objects:
            obj.update()
            obj.draw()

        game_box = Block(0, 0, GameWidth, GameHeight - 100)

        if not game_box.hit_test_block(self.serpent.head) or self.serpent.hit_self():
            global game_state
            game_state = 'game_over'

        # Check for serpent collisions with collectables and collectibles leaving the play area
        to_remove = []
        for col in self.collectibles:
            if col.y > game_box.height:
                to_remove.append(col)
                self.multiplier = 1.0
                continue

            if col.hit_test_block(self.serpent.head):
                to_remove.append(col)
                self.serpent.add_block()
                self.multiplier += .1
                continue

        for o in to_remove:
            self.collectibles.remove(o)
            self.objects.remove(o)

        # UI Rendering
        pygame.draw.rect(display_surface, Color.black(), (0, GameHeight-100, GameWidth, 100))
        display_surface.blit(score_text_label, score_text_label_rect)
        render_text(str(int(self.score)), display_surface.get_rect().centerx, GameHeight - 40)
        render_text("X" + str(self.multiplier), 40, GameHeight - 50)


def render_text(s, x, y, clr=Color.white()):
    r_text = main_font.render(s, True, clr)
    r_text_rect = r_text.get_rect()
    r_text_rect.centerx = x
    r_text_rect.centery = y
    display_surface.blit(r_text, r_text_rect)


def restart():
    global game, game_state
    game = Game()
    game_state = 'playing'


# Game Setup
game = Game()

game_state = 'start'

main_font = pygame.font.SysFont(None, 40)
score_text_label = main_font.render('Score', True, Color.white())
score_text_label_rect = score_text_label.get_rect()
score_text_label_rect.centerx = display_surface.get_rect().centerx
score_text_label_rect.centery = GameHeight - 75

input_timer = float(0)
previous_time = 0
delta_time = float(0)
frame_count = 0

# Game Loop
while True:
    frame_count += 1
    delta_time = (pygame.time.get_ticks() - previous_time) / float(1000)
    previous_time = pygame.time.get_ticks()

    display_surface.fill(Color.white())

    if game_state == 'playing':
        game.update()
    elif game_state == 'start':
        render_text("Start", GameWidth/2, GameHeight/2, Color.black())
        render_text("Press 's' to restart", GameWidth/2, GameHeight/2 + 75, Color.black())
    elif game_state == 'game_over':
        display_surface.fill(Color.black())
        render_text('Game Over', GameWidth/2, GameHeight/2)
        render_text("Press 's' to restart", GameWidth/2, GameHeight/2 + 75)
    elif game_state == 'paused':
        pass

    input_timer += delta_time
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif input_timer >= .3 and event.type == KEYDOWN:
            if event.key == pygame.K_UP and game.serpent.head.dir_y != -1:
                game.serpent.add_turn_point(dir_x=0, dir_y=-1)
            elif event.key == pygame.K_DOWN and game.serpent.head.dir_y != 1:
                game.serpent.add_turn_point(dir_x=0, dir_y=1)
            elif event.key == pygame.K_LEFT and game.serpent.head.dir_x != -1:
                game.serpent.add_turn_point(dir_x=-1, dir_y=0)
            elif event.key == pygame.K_RIGHT and game.serpent.head.dir_x != 1:
                game.serpent.add_turn_point(dir_x=1, dir_y=0)
            elif event.key == pygame.K_s and (game_state == 'start' or game_state == 'game_over'):
                restart()
            input_timer = 0

    pygame.display.update()
    clock.tick(FPS)

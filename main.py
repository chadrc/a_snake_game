import sys
import pygame
import random
import math
from pygame.locals import *

__author__ = 'Chad Collins'

pygame.init()

FPS = 30
clock = pygame.time.Clock()

GameWidth = 300
GameHeight = 650

display_surface = pygame.display.set_mode((GameWidth, GameHeight))
pygame.display.set_caption('Python - A snake game')


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
    """ Base class for all updatable and renderable objects in the game.

        Meant to be subclassed with draw and update overridden.
    """

    def __init__(self, x=0, y=0):
        """ Initialize a GameObject with a position.

        Args:
            x(int): Initial x position of object.
            y(int): Initial y position of object.
        """

        self.x = x
        self.y = y

    def draw(self):
        """ Render the GameObject. """
        pass

    def update(self):
        """ Progress the GameObject a single frame. """
        pass


class Block(GameObject):
    """ Base class for a on screen box. Can also be used for hit testing against a rectangle. """

    def __init__(self, x=0, y=0, width=0, height=0):
        """ Initialize a Block with starting values.

        Args:
            x(int): Optional. Initial x position of Block. Default=0.
            y(int): Optional. Initial y position of Block. Default=0.
            width(int): Optional. Width of Block. Default=0.
            height(int): Optional. Height of Block. Default=0.
        """

        super(Block, self).__init__(x, y)
        self.width = width
        self.height = height

    def draw(self):
        pygame.draw.rect(display_surface, Color.black(), (self.x, self.y, self.width, self.height))

    def update(self):
        pass

    def distance_to(self, b):
        """ Calculate the distance to another block and returns that value.

        Args:
             b(Block): Block to find distance from.

        Returns a single float value.
        """

        x = self.x - b.x
        y = self.y - b.y
        return math.sqrt(x*x + y*y)

    def distance_to_point(self, x, y):
        """ Calculate the distance to a specific point and return that value.

        Args:
            x(int): X coordinate of point.
            y(int): Y coordinate of point.

        Returns the distance between self and the specified point as a float value.
        """

        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx*dx + dy*dy)

    def hit_test_point(self, x, y):
        """ Test to see if a point is in the bounds of this block.

        Args:
            x(int): X coordinate of point.
            y(int): Y coordinate of point.

        Returns a boolean value indicating whether the specified point is in this block.
        """

        return self.x <= x <= (self.x + self.width) and self.y <= y <= (self.y + self.height)

    def hit_test_block(self, test_block):
        """ Test to see if another block is intersecting this one.

        Checks to see if any of the four corners of test_block are within this block.

        Args:
            test_block(Block): Block to test against.

        Returns a boolean value indicating whether the these two blocks are intersecting.
        """

        return self.hit_test_point(test_block.x, test_block.y) \
            or self.hit_test_point(test_block.x, test_block.y + test_block.height) \
            or self.hit_test_point(test_block.x + test_block.width, test_block.y) \
            or self.hit_test_point(test_block.x + test_block.width, test_block.y + test_block.height)


class ScrollingBlock(Block):
    """ Block that will animate down the screen based on the game's scroll speed. """
    def __init__(self):
        """ Initialize a ScrollingBlock with default values """

        super(ScrollingBlock, self).__init__()
        self.width = 9
        self.height = 9

    def update(self):
        self.y += game.scroll_speed * delta_time


class SerpentBlock(Block):
    """ An individual block of a Serpent. """
    def __init__(self, lead):
        """ Initialize a SerpentBlock with lead and default values.

        Args
            lead(SerpentHead or SerpentBlock): The object this SerpentBlock will follow.
        """

        super(SerpentBlock, self).__init__()
        self.width = 9
        self.height = 9
        self.follower = None
        self.last_turn_point = None

        lead.follower = self
        self.x = lead.x + (lead.width + 1) * -lead.dir_x
        self.y = lead.y + (lead.height + 1) * -lead.dir_y
        self.dir_x = lead.dir_x
        self.dir_y = lead.dir_y

    def move(self, x, y):
        """ Set the position of this block.

        Also calculates which direction this block is moving in.

        Args:
            x(int): New x position.
            y(int): New y position.
        """

        dif_x = self.x - x
        dif_y = self.y - y

        # Set direction based on difference between last position and new position
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

    @staticmethod
    def position_child_block(parent):
        """ Position the child to be behind the parent.

        Note: Recursively calls itself to position the child of the child if there is one.

        Args:
             parent(SerpentBlock or SerpentHead): Block who's child will be positioned.
        """

        dist = 0 if parent.last_turn_point is None else \
            parent.distance_to_point(parent.last_turn_point['x'], parent.last_turn_point['y'])

        if parent.last_turn_point is None or dist >= 10:
            # Set child to be behind head by its width/height
            child_x = parent.x + ((parent.width + 1) * -parent.dir_x)
            child_y = parent.y + ((parent.height + 1) * -parent.dir_y)
        else:
            # Set child to be around the corner by this head's width (+1 for separation) by Manhattan distance
            # Distance from last turn point. Only one can be more than zero
            x_dif = parent.x - parent.last_turn_point['x']
            y_dif = parent.y - parent.last_turn_point['y']
            # Calculate the number of remaining units to set other coordinate to and add to the distance
            child_x = -x_dif + (10 - math.fabs(y_dif)) * -parent.last_turn_point['from_dir_x']
            child_y = -y_dif + (10 - math.fabs(x_dif)) * -parent.last_turn_point['from_dir_y']
            child_x += parent.x
            child_y += parent.y

        if parent.follower is not None:
            # Store follower's current direction
            old_dir_x = parent.follower.dir_x
            old_dir_y = parent.follower.dir_y
            parent.follower.move(child_x, child_y)
            # If follower's new direction is different from old direction; set follower's last turn point
            if parent.follower.dir_x != old_dir_x or parent.follower.dir_y != old_dir_y:
                parent.follower.last_turn_point = parent.last_turn_point
            # Move follower's child
            SerpentBlock.position_child_block(parent.follower)


class SerpentHead(Block):
    """ The head (or first) block of a Serpent.

        Maintains and controls a list of SerpentBlocks. Responsible for positioning them and creating them.
    """

    def __init__(self, owner):
        """ Initialize a SerpentHead with an owner and default values.

        Args:
            owner(Serpent): The Serpent object this SerpentHead belongs to.
        """

        super(SerpentHead, self).__init__()
        self.width = 9
        self.height = 9
        self.follower = None
        self.owner = owner
        self.dir_x = 0
        self.dir_y = 0
        self.turn_count = 0
        self.last_x = self.x
        self.last_y = self.y
        self.last_turn_point = None

    def turn(self, dir_x, dir_y):
        """ Change the direction this SerpentHead is moving.

        Args:
            dir_x(int): X direction that this SerpentHead will move in. Should be -1, 0, or 1.
            dir_y(int): Y direction that this SerpentHead will move in. Should be -1, 0, or 1.
        """

        self.dir_x = dir_x
        self.dir_y = dir_y
        self.turn_count += 1

    def update(self):
        self.last_x = self.x
        self.last_y = self.y

        self.x += self.dir_x * float(self.owner.speed) * delta_time
        self.y += self.dir_y * float(self.owner.speed) * delta_time

        # Get last turn point and distance to it; set to invalid values if there is no last turn point
        self.last_turn_point = None if self.turn_count == 0 or self.turn_count - 1 >= len(self.owner.turn_points) \
            else self.owner.turn_points[self.turn_count - 1]

        SerpentBlock.position_child_block(self)


class Serpent(GameObject):
    """ The main Serpent class.

        Contains all information and functionality of the game's serpent.
    """

    def __init__(self, start_blocks):
        """ Initialize a Serpent with default values and a set amount of blocks.

        Args
            start_blocks(int): Number of blocks this Serpent will start with.
        """

        super(Serpent, self).__init__()
        self.speed = .2
        self.turn_points = []
        self.blocks = []
        self.head = SerpentHead(self)
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
        """ Add a single block to the end of the Serpent. """

        new_snake = SerpentBlock(self.blocks[len(self.blocks) - 1])
        self.blocks.append(new_snake)

    def add_turn_point(self, dir_x, dir_y):
        """ Add turn point and immediately turn the snake in that direction.

        Args:
            dir_x(int): X direction to turn toward. Should be -1, 0 or 1.
            dir_y(int): Y direction to turn toward. Should be -1, 0 or 1.
        """

        self.turn_points.append(dict(x=self.head.x, y=self.head.y, dir_x=dir_x, dir_y=dir_y,
                                     from_dir_x=self.head.dir_x, from_dir_y=self.head.dir_y))
        self.head.turn(dir_x, dir_y)

    def length(self):
        """ The length of the snake represented by how many blocks are in the chain.

        Returns the number of blocks attached to this snake as an integer.
        """

        return len(self.blocks)

    def hit_self(self):
        """ Check whether or not the Serpent as collided with itself.

        Compares the distance between the head of the Serpent and each of its blocks.
        If that distance is less than half of size of the block, the Serpent is considered to have intersected itself.

        Returns a boolean value. True if the Serpent is intersecting itself; False otherwise.
        """

        child = self.head.follower
        while child is not None:
            if self.head.distance_to(child) < self.head.width/2:
                return True
            child = child.follower
        return False


class Game:
    """ Information class for the snake game.

        Contains entry point update for running the game.
        Keeps track of necessary information to start and restart the game.
    """

    def __init__(self):
        """ Create default Game setup. """

        self.scroll_speed = 10

        self.serpent_start_blocks = 3
        self.serpent = Serpent(self.serpent_start_blocks)
        self.serpent_start_speed = 50
        self.serpent.speed = self.serpent_start_speed
        self.serpent.head.dir_y = -1
        self.serpent.head.x = GameWidth/2 - self.serpent.head.width/2
        self.serpent.head.y = GameHeight - 200

        self.speed_increase_per_second = .2
        self.objects = [GameObject(), self.serpent]
        self.spawn_range = 100
        self.spawn_time = self.spawn_range / self.scroll_speed
        self.spawn_timer = 0
        self.collectibles = []

        # Create starting collectibles.
        # Area of creation is the entire width of the screen and top half of the screen.
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

        # Spawn additional collectibles after an elapsed time interval
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

        # Update and draw all child objects
        for obj in self.objects:
            obj.update()
            obj.draw()

        # Block for hit testing purposes
        # Represents the playable area of the game (i.e. Excluding the UI display at bottom of the screen)
        game_box = Block(0, 0, GameWidth, GameHeight - 100)

        # Check to see if serpent is of screen
        # If it is; end the game
        if not game_box.hit_test_block(self.serpent.head) or self.serpent.hit_self():
            global game_state
            game_state = 'game_over'

        # Check for serpent collisions with collectables and collectibles leaving the play area
        to_remove = []
        for col in self.collectibles:
            # If a collectible has gone of screen; mark it for deletion and reset the multiplier.
            if col.y > game_box.height:
                to_remove.append(col)
                self.multiplier = 1.0
                continue

            # If the serpent head has collided with a collectible;
            # mark collectible for deletion and add a block to the serpent.
            if col.hit_test_block(self.serpent.head):
                to_remove.append(col)
                self.serpent.add_block()
                self.multiplier += .1
                continue

        # Remove blocks from update and check lists
        for o in to_remove:
            self.collectibles.remove(o)
            self.objects.remove(o)

        # UI Rendering
        # Black bottom rectangle
        pygame.draw.rect(display_surface, Color.black(), (0, GameHeight-100, GameWidth, 100))
        # Score Text
        display_surface.blit(score_text_label, score_text_label_rect)
        # Score Number
        render_text(str(int(self.score)), display_surface.get_rect().centerx, GameHeight - 40)
        # Multiplier
        render_text("X" + str(self.multiplier), 40, GameHeight - 50)


def render_text(s, x, y, clr=Color.white()):
    """ Renders text on the screen.

    Args:
        s(string): The text to be rendered
        x(int): The x center the text will be rendered at.
        y(int): The y center the text will be rendered at.
        clr(tuple): Optional. The color the text will be rendered in.
    """

    r_text = main_font.render(s, True, clr)
    r_text_rect = r_text.get_rect()
    r_text_rect.centerx = x
    r_text_rect.centery = y
    display_surface.blit(r_text, r_text_rect)


def restart():
    """ Restart the Game. """

    global game, game_state

    # Create new game with default values and set state to 'playing'.
    game = Game()
    game_state = 'playing'


# Game Setup
game = Game()
game_state = 'start'

# Create global font and pre-render Score text label
main_font = pygame.font.SysFont(None, 40)
score_text_label = main_font.render('Score', True, Color.white())
score_text_label_rect = score_text_label.get_rect()
score_text_label_rect.centerx = display_surface.get_rect().centerx
score_text_label_rect.centery = GameHeight - 75

# Set up timing globals
input_timer = float(0)
previous_time = 0
delta_time = float(0)
frame_count = 0

# Game Loop
while True:
    frame_count += 1
    delta_time = (pygame.time.get_ticks() - previous_time) / float(1000)
    previous_time = pygame.time.get_ticks()

    # Clear screen
    display_surface.fill(Color.white())

    # Render the screen based on the game state
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

    # Update input timer and check events
    input_timer += delta_time
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # Check key down events only if input timer is up. Reset input timer only when the serpent turns.
        # Serpent will not turn if the pressed direction is the same as the direction the serpent is already going.
        elif input_timer >= .3 and event.type == KEYDOWN:
            if event.key == pygame.K_UP and game.serpent.head.dir_y != -1:
                game.serpent.add_turn_point(dir_x=0, dir_y=-1)
                input_timer = 0
            elif event.key == pygame.K_DOWN and game.serpent.head.dir_y != 1:
                game.serpent.add_turn_point(dir_x=0, dir_y=1)
                input_timer = 0
            elif event.key == pygame.K_LEFT and game.serpent.head.dir_x != -1:
                game.serpent.add_turn_point(dir_x=-1, dir_y=0)
                input_timer = 0
            elif event.key == pygame.K_RIGHT and game.serpent.head.dir_x != 1:
                game.serpent.add_turn_point(dir_x=1, dir_y=0)
                input_timer = 0
            # 's' key for starting and restarting the game
            elif event.key == pygame.K_s and (game_state == 'start' or game_state == 'game_over'):
                restart()

    # Update pygame and clock
    pygame.display.update()
    clock.tick(FPS)

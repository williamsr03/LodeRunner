import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from loderunner.drawable import Drawable
from loderunner.tiles import *
from loderunner.event import Event
import csv, os
from loderunner.config import Config
import loderunner.util as util
from loderunner.graphics import Image, Point, GraphWin, Text

#from tiles import Tile, Empty
#from event import Event
import csv, os
#from config import Config


class Character (Drawable):
    char_map = {}

    @staticmethod
    def load_characters(source, level_index=0):
        for baddie in Baddie.baddies:
            baddie.die()
        Baddie.baddies = []

        # If source is an int, treat as CSV level number
        if isinstance(source, int):
            file_path = os.path.join('levels', f'level{source}.csv')
            with open(file_path) as file_data:
                row_num = 0
                for row in csv.reader(file_data):
                    for col, value in enumerate(row):
                        if value in char_map:
                            char_map[value](col, row_num)
                    row_num += 1

        # If source is a JSON file path, use JSON
        elif isinstance(source, str) and source.endswith('.json'):
            import json
            with open(source, 'r') as f:
                levels = json.load(f)
                # Expecting a 'scene' key with a 2D array of tile codes
                scene = levels[level_index].get('scene')
                if scene is None:
                    raise ValueError("JSON level missing 'scene' key")
                for row_num, row in enumerate(scene):
                    for col, value in enumerate(row):
                        if str(value) in char_map:
                            char_map[str(value)](col, row_num)
        else:
            raise ValueError("source must be a level number or a .json file path")

    def __init__(self, x, y, img_path=None):
        super(Character, self).__init__((x, y), img_path)
        self.draw()

        self._x = x
        self._y = y
        self.fall_counter = 0

    def pos(self):
        return self._x, self._y

    def same_loc(self, x, y):
        return (self._x == x and self._y == y)

    def move(self, dx, dy):
        """ Applies a move, if valid. """
        tx = self._x + dx
        ty = self._y + dy
        next_pos = (tx, ty)

        # Only allow movement inside the map
        if tx >= 0 and ty >= 0 and tx < Config.LEVEL_WIDTH and ty < Config.LEVEL_HEIGHT:

            # Only allow movement into passable tiles
            if Tile.query(next_pos, 'passable'):
                # Do not allow player to climb if they are not in a climbable tile
                if dy < 0 and not Tile.query(self.pos(), 'climbable'):
                    return

                self.apply_move(dx, dy)

    def apply_move(self, dx, dy):
        if self._y + 1 < Config.LEVEL_HEIGHT:
            self.schedule_fall(frames=7)
        self._x += dx
        self._y += dy
        self.move_img(dx, dy)

    def schedule_fall(self, frames=7):
        """Schedule a floating fall after a number of in-game frames."""
        from loderunner.event import Event
        Event(self.fall, frames)

    def fall(self):
        next_pos = (self._x, self._y+1)

        if self._y+1 < Config.LEVEL_HEIGHT:
            if not Tile.query(next_pos, 'standable') and not Tile.query(self.pos(), 'grabbable'):
                for baddie in Baddie.baddies:
                    if baddie.pos() == next_pos:
                        return
                self.apply_move(0, 1)
                # Schedule the next fall if still in the air
                self.schedule_fall(frames=7)  # Adjust frames for fall speed

    def redraw(self):
        self.undraw()
        self.draw()


class Player (Character):
    main = None

    def __init__(self, x, y):
        super(Player, self).__init__(x, y, 'new_user.gif')
        Player.main = self

    def at_exit(self):
        return (self._y == 0)
        #return False  # Exit condition is handled elsewhere

    def apply_move(self, dx, dy):
        super(Player, self).apply_move(dx, dy)
        Tile.tile_at(self.pos()).take()
        for baddie in Baddie.baddies:
            if baddie.pos() == self.pos():
                Drawable.lost()

    def dig(self, direction):
        
        def refill(tile):    
            tile.show()
            if Player.main.pos() == tile.coord:
                Drawable.lost()
            for baddie in Baddie.baddies:
                if baddie.pos() == tile.coord:
                    baddie.die()
                    baddie.respawn()

        x = self._x + direction
        y = self._y + 1

        if self._y < Config.LEVEL_HEIGHT - 1:
            if Tile.query((x, y), 'diggable'): #and isinstance(Tile.tile_at((x, y-1)), Empty):
                Tile.tile_at((x,y)).hide()
                normal_time = 120
                time_to_refill = normal_time * 1.5
                Event(refill, time_to_refill, args=[Tile.tile_at((x, y))])
                for baddie in Baddie.baddies:
                    baddie.fall_and_redraw()




class Baddie (Character):
    baddies = []
    image_path = os.path.join(os.path.dirname(__file__), 'graphics_images','new_enemy.gif')
    def __init__(self, x, y):
        super(Baddie, self).__init__(x, y, Baddie.image_path)
        self.move_event = Event(self.move, 30, recurring=True)
        Baddie.baddies.append(self)
        self.carrying_gold = False
        self.spawn = x, y
        self.last_tile = self.pos()
        self.below = x, y + 1

    def move(self):
        move = PathFinder.run(self.pos())
        super().fall()
        self.last_tile = self.pos()
        if move and (Tile.query(self.below(), 'standable') or Tile.query(self.below(), 'grabbable')):
            new_pos = (self._x + move[0], self._y + move[1])

            # Prevent multiple baddies on the same tile
            if any(b.pos() == new_pos for b in Baddie.baddies if b is not self):
                return
                
            super(Baddie, self).move(*move)
        if self.pos() == Player.main.pos():
            Drawable.lost()
        tile = Tile.tile_at(self.pos())
        if isinstance(tile, Gold) and not self.carrying_gold:
            tile.enemy_take()
            self.carrying_gold = True
        

    def die(self):
        self.undraw()
        Event.delete(self.move_event)
        Baddie.baddies.remove(self)

    def respawn(self):
        # Reset position
        self._x, self._y = self.spawn
    
        # Redraw the enemy GIF at the spawn location
        self.redraw_enemy()
    
        # Re-add movement
        self.move_event = Event(self.move, 30, recurring=True)
        
        # Re-add to global baddies list
        Baddie.baddies.append(self)
        
    def redraw_enemy(self):
        # Undraw any existing image
        self.undraw()
    
        # Reset position to spawn
        self._x, self._y = self.spawn
    
        # Create a new image at the spawn position
        tile_size = Config.CELL_SIZE  # Assuming CELL_SIZE defines pixel size of each tile
        pixel_x = (self._x + 1) * tile_size
        pixel_y = (self._y + 1) * tile_size
        self._img = Image(Point(pixel_x, pixel_y), Baddie.image_path)
    
        # Draw it on the window
        self._img.draw(Drawable._window)
        
    def fall_and_redraw(self):
        # Check if falling into a dug hole (i.e., onto an Empty tile)
        below = (self._x, self._y + 1)
        position = (self._x, self._y)
        if 0 <= below[0] < Config.LEVEL_WIDTH and 0 <= below[1] <= Config.LEVEL_HEIGHT:
            if not Tile.query(below, 'standable') and not Tile.query(below, 'grabbable') and not Tile.query(position, 'grabbable'):
                if self.carrying_gold:
                    Tile.draw_gold_for_enemy(self.last_tile)
                    self.carrying_gold = False
                    #print("Number of gold left:", Gold._num_gold)
        super().fall()

char_map = {'6': Player,
            '4': Baddie}

class PathFinder:
    tiles = None

    @staticmethod
    def valid_tile(pos, last_pos):
        x, y = pos
        if x >= 0 and y >= 0 and x < Config.LEVEL_WIDTH and y < Config.LEVEL_HEIGHT:
            if Tile.query(pos, 'passable'):
                under = (x, y+1)

                if Tile.query(pos, 'grabbable') or Tile.query(under, 'standable'):
                    if not PathFinder.tiles[x][y]:
                        PathFinder.tiles[x][y] = True
                        return True
        return False

    @staticmethod
    def run(start_pos):
        """
        Returns the optimal move from start_pos to get to the Player.
        If no valid path exists, returns the move that gets closer to the player (even if not valid).
        """
        PathFinder.tiles = [[False for y in range(Config.LEVEL_HEIGHT)] for x in range(Config.LEVEL_WIDTH)]

        x, y = start_pos
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        valid_neighbors = [neighbor for neighbor in neighbors if PathFinder.valid_tile(neighbor, start_pos)]

        children = []
        for valid_pos in valid_neighbors:
            children.append(PathFinder(valid_pos, start_pos))

        
        while children:
            remove_list = []
            for child in children:
                state = child.update()
                if state == 1:
                    return (child.pos[0] - start_pos[0], child.pos[1] - start_pos[1])
                elif state == -1:
                    remove_list.append(child)

            for child in remove_list:
                children.remove(child)

        px, py = Player.main.pos()
        best_move = None
        min_dist = float('inf')
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            #dist = abs(nx - px) + abs(ny - py)
            if 0 <= nx < Config.LEVEL_WIDTH and 0 <= ny < Config.LEVEL_HEIGHT:
                dist = abs(nx - px) + abs(ny - py)
                if dist < min_dist:
                    min_dist = dist
                    best_move = (dx, dy)
        return best_move

    @staticmethod
    def valid_neighbors(pos, last_pos):
        x, y = pos
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [neighbor for neighbor in neighbors if not neighbor == last_pos and PathFinder.valid_tile(neighbor, pos)]



    def __init__(self, pos, last_pos):
        self._children = []
        self._x = pos[0]
        self._y = pos[1]
        self.pos = pos
        self.last_pos = last_pos


    def update(self):
        # Get all valid positions for children
        children_pos = PathFinder.valid_neighbors(self.pos, self.last_pos)



        # If children have not yet been created (ie this is a new node)
        if not self._children:
            # If we occupy the player's position, flag this node
            if self.pos == Player.main.pos():
                return 1

            # If there are no valid moves from this child, delete this branch
            if not children_pos:
                return -1

            # Create children at all valid locations
            for child_pos in children_pos:
                if child_pos == Player.main.pos():
                    return 1
                else:
                    self._children.append(PathFinder(child_pos, self.pos))

            return 0


        remove_list = []
        for child in self._children:
            state = child.update()
            if state == 1:
                return 1
            elif state == -1:
                remove_list.append(child)

        for child in remove_list:
            self._children.remove(child)

        if not self._children:
            return -1

        return 0

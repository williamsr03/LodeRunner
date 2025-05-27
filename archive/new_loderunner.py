#
# MAZE
# 
# Example game
#
# Version without baddies running around
#


from graphics import *
import csv
import json
import os

LEVEL_WIDTH = 20
LEVEL_HEIGHT = 20

CELL_SIZE = 24
WINDOW_WIDTH = CELL_SIZE*LEVEL_WIDTH
WINDOW_HEIGHT = CELL_SIZE*LEVEL_HEIGHT

CELL_TYPE = {
  'EMPTY':  0,
  'BRICK':  1,
  'LADDER': 2,
  'ROPE':   3,
  'GOLD':   4,
  'BADDIE': 5
}

IMAGE_MAP = {
	1: 'new_block.gif',
	2: 'new_ladder.gif',
	3: 'new_rope.gif',
	4: 'new_gold.gif'
}

IMPASSABLE = [CELL_TYPE['BRICK']]
PASSABLE = [elem for elem in CELL_TYPE.values() if elem not in IMPASSABLE]
STANDABLE = [CELL_TYPE['LADDER'], CELL_TYPE['BRICK']]
GRABBABLE = [CELL_TYPE['ROPE'], CELL_TYPE['LADDER']]
CLIMBABLE = [CELL_TYPE['LADDER']]
TAKEABLE = [CELL_TYPE['GOLD']]

def screen_pos (x,y):
	return (x*CELL_SIZE+10,y*CELL_SIZE+10)

def screen_pos_index (index):
	x = index % LEVEL_WIDTH
	y = (index - x) / LEVEL_WIDTH
	return screen_pos(x,y)

def index (x,y):
	return x + (y*LEVEL_WIDTH)

def coord(index):
	return index % LEVEL_WIDTH, index // LEVEL_WIDTH

class Item (object):
	_window = None

	def __init__(self, pos, img):
		self._x = pos[0]
		self._y = pos[1]
		self._img = Image(Point((self._x+1)*CELL_SIZE-1, (self._y+1)*CELL_SIZE-1), img)
		self._img.draw(Item._window)

	def remove(self):
		self._img.undraw()
	
class Character (object):

    def __init__ (self,pic,x,y,window,level):
        (sx,sy) = screen_pos(x,y)
        self._img = Image(Point(sx+CELL_SIZE/2,sy+CELL_SIZE/2+2),pic)
        self._window = window
        self._img.draw(window)
        self._x = x
        self._y = y
        self._level = level

    def pos(self):
        return self._x, self._y

    def same_loc(self, x, y):
        return (self._x == x and self._y == y)

    def move(self, dx, dy):
        """ Applies a move, if valid. """
        tx = self._x + dx
        ty = self._y + dy

        # Only allow movement inside the map
        if tx >= 0 and ty >= 0 and tx < LEVEL_WIDTH and ty < LEVEL_HEIGHT:

            # Only allow movement into passable tiles
            if self._level[index(tx, ty)] in PASSABLE:

                # Do not allow player to climb if they are not in a climbable tile
                if dy < 0 and self._level[index(self._x, self._y)] not in CLIMBABLE:
                    return

                self._x = tx
                self._y = ty
                self._img.move(dx*CELL_SIZE, dy*CELL_SIZE)
                self.fall()
        print(self._x, self._y)

    def fall(self):
        cur_tile = self._level[index(self._x, self._y)]
        next_tile = self._level[index(self._x, self._y+1)]

        if not next_tile in STANDABLE and not cur_tile in GRABBABLE:
            self._y += 1
            self._img.move(0, CELL_SIZE)
            if self._y + 1 < LEVEL_HEIGHT:
            	self.fall()


class Player (Character):
	def __init__ (self,x,y,window,level, item_map):
		Character.__init__(self,'new_user.gif',x,y,window,level)
		self._item_map = item_map

	def at_exit (self):
		return (self._y == 0)

	def take(self):
		# remove from the level
		self._level[index(self._x,self._y)] = 0
		
		# destroy the image
		self._item_map[index(self._x, self._y)].remove()

		# remove the item from the item map
		self._item_map[index(self._x, self._y)] = None

	def dig(self, direction):
		x = self._x + direction
		y = self._y + 1

		if self._y < LEVEL_HEIGHT - 1:
			if self._level[index(x, y)] == 1 and self._level[index(x, y-1)] == 0:
				self._level[index(x, y)] = 0
				self._item_map[index(x, y)].remove()
				self._item_map[index(x, y)] = None

class Baddie (Character):
	def __init__ (self,x,y,window,level,player):
		Character.__init__(self,'new_enemy.gif',x,y,window,level)
		self._player = player

def lost (window):
	t = Text(Point(WINDOW_WIDTH/2+10,WINDOW_HEIGHT/2+10),'YOU LOST!')
	t.setSize(36)
	t.setTextColor('red')
	t.draw(window)
	window.getKey()
	exit(0)

def won (window):
	t = Text(Point(WINDOW_WIDTH/2+10,WINDOW_HEIGHT/2+10),'YOU WON!')
	t.setSize(36)
	t.setTextColor('red')
	t.draw(window)
	window.getKey()
	exit(0)


# Cache for loaded levels
_loaded_levels = None

def create_level(num):
    global _loaded_levels
    if _loaded_levels is None:
        # Load the levels from the JSON file once
        with open(os.path.join(os.path.dirname(__file__), '../../LR_Levels.json'), 'r') as f:
            _loaded_levels = json.load(f)
    # Levels are 0-indexed in the JSON, so subtract 1 from num
    level = _loaded_levels[num - 1]
    return level

def create_item_map(level):
	item_map = []
	for index, value in enumerate(level):
		if value in IMAGE_MAP:
			pos = coord(index)
			item = Item(pos, IMAGE_MAP[value])
			item_map.append(item)
		else:
			item_map.append(None)
	return item_map

MOVE = {
	'Left': (-1,0),
	'Right': (1,0),
	'Up' : (0,-1),
	'Down' : (0,1)
}


def main ():

	window = GraphWin("LodeRunner", WINDOW_WIDTH+20, WINDOW_HEIGHT+20)
	Item._window = window

	rect = Rectangle(Point(5,5),Point(WINDOW_WIDTH+15,WINDOW_HEIGHT+15))
	rect.setFill('sienna')
	rect.setOutline('sienna')
	rect.draw(window)
	rect = Rectangle(Point(10,10),Point(WINDOW_WIDTH+10,WINDOW_HEIGHT+10))
	rect.setFill('black')
	rect.setOutline('black')
	rect.draw(window)

	level = create_level(1)
	item_map = create_item_map(level) #
	#screen = create_screen(level, window)

	p = Player(10,18,window,level, item_map)

	baddie1 = Baddie(5,1,window,level,p)
	baddie2 = Baddie(10,1,window,level,p)
	baddie3 = Baddie(15,1,window,level,p)

	while not p.at_exit():
		key = window.checkKey()
		if key == 'q':
			window.close()
			exit(0)
		if key in MOVE:
			(dx,dy) = MOVE[key]
			p.move(dx,dy)

		if level[index(p._x,p._y)] in TAKEABLE:
			p.take()
		if key == 'a':
			p.dig(-1)
		if key == 'z':
			p.dig(1)

		# baddies should probably move here

	won(window)

if __name__ == '__main__':
	main()


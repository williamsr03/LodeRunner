import csv, util, os
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from LodeRunner.drawable import Drawable
#from drawable import Drawable
from  LodeRunner import util

class Tile(Drawable):
    level = []

    tile_map = {
        #'0': Ladder,
        #'1': Rope,
        #'2': Empty,
        #'3': Brick,
        #'4': Enemy,
        #'5': Gold,
        #'6': Spawn,
        #'7': Brick
    }

    _hidden_tiles = []

    @staticmethod
    def load_level(source, level_index=0):
        Tile.level = []
        row_num = 0

        # If source is an int, treat as CSV level number
        if isinstance(source, int):
            file_path = os.path.join('levels', f'level{source}.csv')
            with open(file_path) as file_data:
                for row in csv.reader(file_data):
                    Tile.level.extend([
                        Tile.tile_map[elem]((index, row_num)) if elem in Tile.tile_map else Empty((index, row_num))
                        for index, elem in enumerate(row)
                    ])
                    row_num += 1

        # If source is a JSON file path, use JSON
        elif isinstance(source, str) and source.endswith('.json'):
            with open(source, 'r') as f:
                levels = json.load(f)
                if not (0 <= level_index < len(levels)):
                    raise IndexError(f"Requested level_index {level_index} but only {len(levels)} levels available in {source}")
                scene = levels[level_index].get('scene')
                if scene is None:
                    raise ValueError("JSON level missing 'scene' key")
                for row in scene:
                    Tile.level.extend([
                        Tile.tile_map.get(str(elem), Empty)((index, row_num))
                        for index, elem in enumerate(row)
                    ])
                    row_num += 1
        else:
            raise ValueError("source must be a level number or a .json file path")

    @staticmethod
    def query(coord, property):
        tile = Tile.level[util.index(*coord)]
        return tile.properties[property]

    @staticmethod
    def tile_at(coord):
        return Tile.level[util.index(*coord)]

    @staticmethod
    def clear(coord):
        Tile.level[util.index(*coord)].undraw()
        Tile.level[util.index(*coord)] = Empty(coord)

    def __init__(self, coord, img_path=None, properties={}, hidden=False):
        super(Tile, self).__init__(coord, img_path)
        if not hidden:
            self.draw()

        # Set up tile properties
        self.properties = {'passable':  True,
                           'takable':   False,
                           'standable': False,
                           'climbable': False,
                           'grabbable': False,
                           'diggable':  False}

        for key in properties:
            if key in self.properties:
                self.properties[key] = properties[key]

        self.coord = coord

        if hidden:
            self.hide()

    def hide(self):
        self.hidden_properties = self.properties
        self.properties = {'passable':  True,
                           'takable':   False,
                           'standable': False,
                           'climbable': False,
                           'grabbable': False,
                           'diggable':  False}
        self.undraw()

    def show(self):
        self.draw()
        self.properties = self.hidden_properties

    def take(self):
        pass


class Empty(Tile):
    def __init__(self, coord):
        super(Empty, self).__init__(coord)


class Brick(Tile):
    def __init__(self, coord):
        properties = {'passable':   False,
                      'standable':  True,
                      'diggable':   True}
        super(Brick, self).__init__(coord, 'new_block.gif', properties)

class solid_Brick(Tile):
    def __init__(self, coord):
        properties = {'passable':   False,
                      'standable':  True,
                      'diggable':   False}
        super(solid_Brick, self).__init__(coord, 'new_solidBlock.gif', properties)

class Ladder(Tile):
    def __init__(self, coord, hidden=False):
        properties = {'standable':  True,
                      'climbable':  True,
                      'grabbable': True}
        super(Ladder, self).__init__(coord, 'new_ladder.gif', properties, hidden)


class Rope(Tile):
    def __init__(self, coord):
        properties = {'grabbable':  True}
        super(Rope, self).__init__(coord, 'new_rope.gif', properties)


class Gold(Tile):
    _num_gold = 0

    @staticmethod
    def all_taken():
        return Gold._num_gold <= 0

    def __init__(self, coord):
        Gold._num_gold += 1
        properties = {'takable': True}
        super(Gold, self).__init__(coord, 'new_gold.gif', properties)

    def take(self):
        Gold._num_gold -= 1
        Tile.clear(self.coord)


class HiddenLadder(Ladder):
    _hidden = []
    @staticmethod
    def showAll():
        for ladder in HiddenLadder._hidden:
            ladder.show()
        HiddenLadder._hidden = []

    def __init__(self, coord):
        super(HiddenLadder, self).__init__(coord, hidden=True)
        HiddenLadder._hidden.append(self)


Tile.tile_map = {
        '0': Ladder,
        '1': Rope,
        '2': Empty,
        '3': solid_Brick,
        #'4': Enemy,
        '5': Gold,
        #'6': Spawn,
        '7': Brick
        }


if __name__ == "__main__":
    Tile.load_level(1)

    # After loading the level and before starting the game loop
    spawn_coord = ... # get spawn coordinates from level
    spawn_tile = Tile.tile_at(spawn_coord)
    if not (spawn_tile.properties['standable'] or spawn_tile.properties['climbable'] or spawn_tile.properties['grabbable']):
        print("Warning: Spawn is not on a valid tile! The player may fall or the game may crash.")

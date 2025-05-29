import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from LodeRunner.config import Config
from config import Config


def index(x, y):
    return x + (y*Config.LEVEL_WIDTH)


def coord(index):
    return index % Config.LEVEL_WIDTH, index // Config.LEVEL_WIDTH


def screen_pos(x, y):
    return (x*Config.CELL_SIZE+10, y*Config.CELL_SIZE+10)


def screen_pos_index(index):
    x = index % Config.LEVEL_WIDTH
    y = (index - x) / Config.LEVEL_WIDTH
    return screen_pos(x, y)

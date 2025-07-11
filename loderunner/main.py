"""
LodeRunner Clone
----------------
By: Bonnie Ishiguro and Nick Francisci and Reid Williams
for SURF 2025
"""

import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from loderunner.config import Config
from loderunner.graphics import *
from loderunner.drawable import Drawable
from loderunner.tiles import Tile, Gold, HiddenLadder
from loderunner.characters import *
from loderunner.event import Event 
import datasets


def load_level(source, level_index=0):
    Event.clear()
    Config.config_level(source, level_index)
    Drawable.recreateWindow()
    Tile.load_level(source, level_index)
    Character.load_characters(source, level_index)
    print("Number of baddies after level load:", len(Baddie.baddies))

KEYMAP = {
    'Left':     'Player.main.move(-1, 0)',
    'Right':    'Player.main.move(1, 0)',
    'Up':       'Player.main.move(0, -1)',
    'Down':     'Player.main.move(0, 1)',
    'a':        'Player.main.dig(-1)',
    'z':        'Player.main.dig(1)',
    'q':        'exit(0)'
}

def main():
    frame_duration = 1.0/60.0

    # Get file and optional level index from command line
    if len(sys.argv) < 2:
        print("Usage: python main.py <level_file> [level_index]")
        sys.exit(1)

    level_file = sys.argv[1]
    # Change default level_index from 0 to 1
    level_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    # Support both CSV and JSON
    if level_file.endswith('.json'):
        LEVELS = [(level_file, level_index - 1)]
    else:
        LEVELS = [int(level_index) if level_index else 0]

    for level in LEVELS:
        if isinstance(level, tuple):
            load_level(level[0], level[1])
        else:
            load_level(level)

        while not Gold.all_taken():
            frame_start_time = time.time()

            key = Drawable._window.checkKey()

            if key in KEYMAP:
                eval(KEYMAP[key])

            Event.update()

            if not Config.hidden_flag:
                if Gold.all_taken():
                    HiddenLadder.showAll()
                    Player.main.redraw()
                    for baddie in Baddie.baddies:
                        baddie.redraw()
                    Config.hidden_flag = True

            frame_time = time.time() - frame_start_time
            if frame_time < frame_duration:
                time.sleep(frame_duration - frame_time)
        Drawable.won()

def play_lr_level(level_file, level_index=1):
    """
    Play a Lode Runner level from another script.
    level_file: path to the level file (CSV or JSON)
    level_index: 1-based index for JSON, or level number for CSV
    """

    frame_duration = 1.0/60.0
    # Adjust index for JSON (1-based to 0-based)
    if level_file.endswith('.json'):
        LEVELS = [(level_file, level_index - 1)]
    else:
        LEVELS = [int(level_index) if level_index else 1]

    for level in LEVELS:
        if isinstance(level, tuple):
            #print("Level: ", level)
            load_level(level[0], level[1])
        else:
            load_level(level)

        while not Gold.all_taken() or any(baddie.carrying_gold for baddie in Baddie.baddies):
            frame_start_time = time.time()
            key = Drawable._window.checkKey()
            if key in KEYMAP:
                eval(KEYMAP[key])
            Event.update()
            if not Config.hidden_flag:
                if Gold.all_taken():
                    HiddenLadder.showAll()
                    Player.main.redraw()
                    for baddie in Baddie.baddies:
                        baddie.redraw()
                    Config.hidden_flag = True
            frame_time = time.time() - frame_start_time
            if frame_time < frame_duration:
                time.sleep(frame_duration - frame_time)
        for baddie in Baddie.baddies:
            baddie.die()
        Baddie.baddies = []
        print("Resetting baddies in main!")
        Drawable.won()

if __name__ == '__main__':
    play_lr_level(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
# If you want to run the game directly, uncomment the following line:
    #main()

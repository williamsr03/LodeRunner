"""
LodeRunner Clone
----------------
By: Bonnie Ishiguro and Nick Francisci
for Game Programming: Level 4
"""

import time
from config import Config
from graphics import *
from drawable import Drawable
from tiles import Tile, Gold, HiddenLadder
from characters import *
from event import Event


# TODO: Move these somewhere more appropriate (drawable?)

def load_level(source, level_index=0):
    Config.config_level(source, level_index)
    Drawable.recreateWindow()
    Tile.load_level(source, level_index)
    Character.load_characters(source, level_index)

# Example usage:
# For JSON:
# LEVELS = [('MarioDiffusion/LR_LevelsAndCaptions-regular.json', 0), ('MarioDiffusion/LR_LevelsAndCaptions-regular.json', 1)]
# For CSV:
# LEVELS = [1, 2]

LEVELS = [('MarioDiffusion/LR_LevelsAndCaptions-regular.json', 0)]  # or [1, 2] for CSV

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

    for level in LEVELS:
        if isinstance(level, tuple):
            load_level(level[0], level[1])
        else:
            load_level(level)

        while not Player.main.at_exit():
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

            # baddies should probably move here

            frame_time = time.time() - frame_start_time
            if frame_time < frame_duration:
                time.sleep(frame_duration - frame_time)
        Drawable.won()

if __name__ == '__main__':
    main()
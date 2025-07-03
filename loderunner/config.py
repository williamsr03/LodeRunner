import os, csv
import json
import os
import sys

class Config:
    LEVEL_WIDTH = 32
    LEVEL_HEIGHT = 32

    CELL_SIZE = 24
    WINDOW_WIDTH = CELL_SIZE*LEVEL_WIDTH
    WINDOW_HEIGHT = CELL_SIZE*LEVEL_HEIGHT

    hidden_flag = False

    @staticmethod
    def config_level(source, level_index=0):
        #print("source: ", source)
        if source.endswith('.json'):
            with open(source, 'r') as f:
                levels = json.load(f)
                # Use the first level in the JSON file as an example
                scene = levels[0]['scene']
                Config.LEVEL_HEIGHT = len(scene)
                Config.LEVEL_WIDTH = max(len(row) for row in scene) if scene else 0
        else:
            with open(source) as file_data:
                row_num = 0
                for row in csv.reader(file_data):
                    Config.LEVEL_WIDTH = len(row)
                    row_num += 1
                Config.LEVEL_HEIGHT = row_num

        Config.WINDOW_WIDTH = Config.CELL_SIZE * Config.LEVEL_WIDTH
        Config.WINDOW_HEIGHT = Config.CELL_SIZE * Config.LEVEL_HEIGHT
        Config.hidden_flag = False

import os
import sys

sys.path.insert(0, os.path.abspath("../../../.."))
import time
from iafModel import IAFModel
from mesa.visualization import Slider, SolaraViz, make_space_component
from mesa.mesa_logging import get_rootlogger
import logging
logger = get_rootlogger()
log_file = "agent_log.txt"  # Specify your log file name
file_handler = logging.FileHandler(log_file, mode='w')  # 'w' mode will overwrite the file each time
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)

width = 50
height = 50


model = IAFModel(width=width, height=height, population_size=1)

while True:
    model.step()
    time.sleep(0.1)
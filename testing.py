import os
import sys

sys.path.insert(0, os.path.abspath("../../../.."))
import time
from boidFlockersModel import BoidFlockers
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

def boid_draw(agent):
    neighbors = len(agent.neighbors)

    if neighbors <= 1:
        return {"color": "red", "size": 20}
    elif neighbors >= 2:
        return {"color": "green", "size": 20}


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "population_size": Slider(
        label="Number of boids",
        value=10,
        min=10,
        max=200,
        step=10,
    ),
    "width": width,
    "height": height,
    "speed": Slider(
        label="Speed of Boids",
        value=5,
        min=1,
        max=20,
        step=1,
    ),
    "vision": Slider(
        label="Vision of Bird (radius)",
        value=10,
        min=1,
        max=50,
        step=1,
    ),
    "separation": Slider(
        label="Minimum Separation",
        value=2,
        min=1,
        max=20,
        step=1,
    ),
}


model = BoidFlockers(width=width, height=height)

while True:
    model.step()
    time.sleep(0.1)
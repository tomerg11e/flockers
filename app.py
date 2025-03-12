import os
import sys

sys.path.insert(0, os.path.abspath("../../../.."))

from boidFlockersModel import BoidFlockers
from mesa.visualization import Slider, SolaraViz, make_space_component
from mesa.mesa_logging import get_rootlogger
import logging
logger = get_rootlogger()
log_file = "agent_log.txt"  # Specify your log file name
file_handler = logging.FileHandler(log_file, mode='w')  # 'w' mode will overwrite the file each time
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)

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
        value=100,
        min=10,
        max=200,
        step=10,
    ),
    "width": 100,
    "height": 100,
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

model = BoidFlockers()

page = SolaraViz(
    model,
    components=[make_space_component(agent_portrayal=boid_draw, backend="matplotlib")],
    model_params=model_params,
    name="Boid Flocking Model",
)
page  # noqa

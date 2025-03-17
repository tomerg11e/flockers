import os
import sys
import numpy as np
sys.path.insert(0, os.path.abspath("../../../.."))
import matplotlib.pyplot as plt
from iafModel import IAFModel
from mesa.visualization import Slider, SolaraViz, make_space_component
from mesa.mesa_logging import get_rootlogger
import logging
from matplotlib.colors import to_hex
logger = get_rootlogger()
log_file = "agent_log.txt"  # Specify your log file name
file_handler = logging.FileHandler(log_file, mode='w')  # 'w' mode will overwrite the file each time
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)

width = 50
height = 50

def airplane_draw(agent, palette="tab10"):
    if agent.mission is not None:
        cmap = plt.get_cmap(palette)
        color = to_hex(cmap(agent.group_number % cmap.N))
        marker = "o"
    else:
        color = "#000000"
        marker = "X"
    return {"color": color, "size": 20, "marker": marker}


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "population_size": Slider(
        label="Number of boids",
        value=10,
        min=1,
        max=20,
        step=1,
    ),
    "width": width,
    "height": height,
    "speed": Slider(
        label="Speed of Boids",
        value=1,
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

model = IAFModel(width=width, height=height)

page = SolaraViz(
    model,
    components=[make_space_component(agent_portrayal=airplane_draw, backend="matplotlib")],
    model_params=model_params,
    name="Israeli Air Force",
)
page  # noqa

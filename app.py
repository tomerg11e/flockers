import os
import sys
import numpy as np
sys.path.insert(0, os.path.abspath("../../../.."))
import matplotlib.pyplot as plt
from iafModel import IAFModel
from airplaneAgent import AirplaneAgent
from baseAgent import BaseAgent
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

def agent_draw(agent, palette="tab10"):
    plot_kwargs = {
        "size": 20,
        "marker": ">",
    }
    if isinstance(agent, AirplaneAgent):
        if agent.mission is not None:
            cmap = plt.get_cmap(palette)
            plot_kwargs["color"] = to_hex(cmap(agent.group_number % cmap.N))
            plot_kwargs["marker"] = "o"
        else:
            plot_kwargs["color"] = "#000000"
            plot_kwargs["marker"] = "X"
    elif isinstance(agent,BaseAgent):
        cmap = plt.get_cmap(palette)
        plot_kwargs["color"] = to_hex(cmap(agent.group_number % cmap.N))
        plot_kwargs["marker"] = "s"
        plot_kwargs["size"] = 50
    return plot_kwargs

model_params = {
    "width": width,
    "height": height,
    "speed": Slider(
        label="Speed of planes",
        value=1,
        min=1,
        max=20,
        step=1,
    ),
    "generateMissionInterval": Slider(
        label="generate mission every X ticks",
        value=80,
        min=50,
        max=200,
        step=10,
    ),
}

model = IAFModel(width=width, height=height)

page = SolaraViz(
    model,
    components=[make_space_component(agent_portrayal=agent_draw, backend="matplotlib")],
    model_params=model_params,
    name="Israeli Air Force",
)
page  # noqa

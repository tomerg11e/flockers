"""
Boids Flocking Model
===================
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("../../../.."))
from queue import Queue
import numpy as np
from mission import Mission
from mesa import Model
from airplaneAgent import AirplaneAgent
from mesa.experimental.continuous_space import ContinuousSpace
from mesa.mesa_logging import create_module_logger, method_logger

_mesa_logger = create_module_logger()


class IFAModel(Model):
    """Flocker model class. Handles agent creation, placement and scheduling."""

    def __init__(
        self,
        population_size=10,
        width=50,
        height=50,
        speed=1,
        vision=10,
        separation=2,
        cohere=0.03,
        separate=0.075,
        match=0.05,
        seed=None,
        boidObject=AirplaneAgent,
    ):
        """Create a new Boids Flocking model.

        Args:
            population_size: Number of Boids in the simulation (default: 100)
            width: Width of the space (default: 100)
            height: Height of the space (default: 100)
            speed: How fast the Boids move (default: 1)
            vision: How far each Boid can see (default: 10)
            separation: Minimum distance between Boids (default: 2)
            cohere: Weight of cohesion behavior (default: 0.03)
            separate: Weight of separation behavior (default: 0.015)
            match: Weight of alignment behavior (default: 0.05)
            seed: Random seed for reproducibility (default: None)
        """
        super().__init__(seed=seed)

        # Set up the space
        self.space = ContinuousSpace(
            [[0, width], [0, height]],
            torus=True,
            random=self.random,
            n_agents=population_size,
        )
        self.boidObject = boidObject

        # Create and place the Boid agents
        maxGroups = 3
        bases_position = self.rng.random(size=(maxGroups, 2)) * self.space.size
        groups = self.rng.integers(0, maxGroups, size=(population_size,))
        positions = bases_position[groups].squeeze() + self.rng.uniform(-1, 1, size=(population_size, 2))
        # positions = self.rng.random(size=(population_size, 2)) * self.space.size
        directions = self.rng.uniform(-1, 1, size=(population_size, 2))
        self.boidObject.create_agents(
            self,
            population_size,
            self.space,
            position=positions,
            direction=directions,
            cohere=cohere,
            separate=separate,
            match=match,
            speed=speed,
            vision=vision,
            separation=separation,
            group = groups
        )
        self.missions = Queue()
        self.generate_missions()


    def generate_missions(self, numMissions=5):
        for _ in range(numMissions):
            mission_type = self.random.choice(Mission.valid_mission_types)
            location = self.random.random(2) * self.space.size
            self.missions.put(Mission(mission_type, location))

    def assign_missions(self):
        for mission in self.missions:
            if mission.status == "PENDING":
                agents, distances = self.calculate_distances(mission.location)
                if agents:
                    agent = self.random.choice(agents)
                    agent.mission = mission
                    self.missions.remove(mission)

    def step(self):
        """Run one step of the model.

        All agents are activated in random order using the AgentSet shuffle_do method.
        """
        # if self.steps % 5 == 0:
        #     self.generate_missions()
        # self.assign_missions()
        _mesa_logger.warning(f"Running step {self.steps}")
        self.agents.shuffle_do("step")
        self.update_average_heading()

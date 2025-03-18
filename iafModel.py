import os
import sys

sys.path.insert(0, os.path.abspath("../../../.."))
import numpy as np
from mission import Mission, OptionalMissionClasses
from typing import List, Optional
from mesa import Model
from airplaneAgent import AirplaneAgent
from baseAgent import BaseAgent
from mesa.experimental.continuous_space import ContinuousSpace
from mesa.mesa_logging import create_module_logger, method_logger

_mesa_logger = create_module_logger()


class IAFModel(Model):
    """
    This Python module defines an agent-based simulation of the Israeli Air Force (IAF) 
    using the Mesa framework. 
    Each agent represents an airplane that can be assigned to missions, or a base. 
    The simulation includes airbases, mission generation, and agent movement within a continuous space.
    """

    def __init__(
        self,
        population_size=10,
        width=50,
        height=50,
        speed=1,
        vision=10,      #boid physics - not used
        separation=2,   #boid physics - not used
        cohere=0.03,    #boid physics - not used
        separate=0.075, #boid physics - not used
        match=0.05,     #boid physics - not used
        seed=42,
        generateMissionInterval=80,
        basesNum = 3
    ):
        """Create a new IAF model.

        Args:
            population_size (int): Number of airplane agents.
            width, height (int): Dimensions of the simulation space.
            speed (float): Movement speed of agents.
            seed (int, optional): Random seed for reproducibility.
            generateMissionInterval (int) : Interval (in steps) at which new missions are generated.
            basesNum (int) : Number of airbases in the simulation.
            bases_position (ndarray) : Positions of the airbases.
            missions (List[Mission]) : Active missions in the simulation.
        """
        super().__init__(seed=seed)
        self.population_size = population_size
        # Set up the space
        self.space = ContinuousSpace(
            [[0, width], [0, height]],
            torus=True,
            random=self.random,
            n_agents=population_size,
        )

        # Create airbases and airplanes
        self.basesNum = basesNum
        self.bases_position = self.rng.random(size=(basesNum, 2)) * self.space.size
        groups = self.rng.integers(0, basesNum, size=(population_size,))
        positions = self.bases_position[groups].squeeze()
        directions = np.zeros(shape=(population_size, 2))
        AirplaneAgent.create_agents(
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
        BaseAgent.create_agents(
            self,
            basesNum,
            self.space,
            position=self.bases_position,
            group = np.arange(basesNum)
        )
        #mission handling and initial generation
        self.generateMissionInterval = generateMissionInterval
        self.missions: List[Mission] = []
        self.generate_missions(population_size-1)


    def generate_missions(self, numMissions=3):
        """
        Generates a specified number of missions and adds them to the mission list.
        the generated mission types are taken from the OptionalMissionClasses list in the mission.py file.
        """
        for _ in range(numMissions):
            mission_type = self.random.choice(OptionalMissionClasses)
            self.missions.append(mission_type(self))

    def mission_finished(self, finished_mission: Mission):
        for mission in self.missions:
            if mission.uuid == finished_mission.uuid:
                mission.stage = Mission.MISSION_COMPLETE
                _mesa_logger.warning(f"{mission}")

    def assign_missions(self):
        """
        Assigns missions to free agents.
        right now this is done by assigning the closest free agent to the mission.
        """
        for mission in self.missions:
            if mission.stage == Mission.MISSION_PENDING:
                distances, agents = self.space.calculate_distances(mission.destination)
                sorted_free_agents = [agents[i] for i in np.argsort(distances) if isinstance(agents[i], AirplaneAgent) and agents[i].mission is None]
                if len(sorted_free_agents) != 0:
                    agent = sorted_free_agents[0]
                    agent.mission = mission
                    mission.agent = agent
                    mission.change_stage()
                    _mesa_logger.warning(f"{mission} assigned to agent {agent.unique_id}")

    def step(self):
        """
        Run one step of the model.

        All agents are activated in random order using the AgentSet shuffle_do method.
        """
        if self.steps % self.generateMissionInterval == 0:
            self.generate_missions(self.population_size)
        self.assign_missions()
        _mesa_logger.warning(f"Running step {self.steps}")
        self.agents.shuffle_do("step")
    
    def getFullStatus(self):
        """
        Returns the status of all agents in the model.
        """
        status = []
        for agent in self.agents:
            status.append(agent.__repr__())
        status = "\n".join(status)
        return status
from itertools import compress
from typing import Optional
import numpy as np
from mesa.experimental.continuous_space import ContinuousSpaceAgent
from mesa.mesa_logging import create_module_logger, method_logger
from mission import Mission
_mesa_logger = create_module_logger()

class AirplaneAgent(ContinuousSpaceAgent):
    """
    Represents an airplane agent in a continuous space simulation. 
    The agent moves either towards a mission destination or follows a flocking behavior inspired by Boid algorithms.

    Attributes:
        base_location (np.ndarray): Initial position of the airplane.
        position (np.ndarray): Current position of the airplane.
        speed (float): Speed of the airplane.
        direction (np.ndarray): Direction vector of movement.
        vision (float): Radius within which the agent perceives neighbors. (boid algorithm)
        separation (float): Distance threshold to maintain separation from neighbors. (boid algorithm)
        cohere_factor (float): Factor controlling the tendency to move toward neighbors. (boid algorithm)
        separate_factor (float): Factor controlling the tendency to move away from neighbors. (boid algorithm)
        match_factor (float): Factor controlling the tendency to align with neighbors. (boid algorithm)
        starting_factor (float): Factor influencing return to base behavior. (boid algorithm)
        base_id (int): Identifier for the airplane's base.
        neighbors (list): List of neighboring agents.
        mission (Optional[Mission]): Current mission assigned to the airplane.
        inAction (bool): Whether the agent is currently active.
    """
    def __init__(
        self,
        model,
        space,
        position=np.array([ 0, 0]),
        speed=1,
        direction=np.array([ 1, 1]),
        vision=1,
        separation=1,
        cohere=0.03,
        separate=0.015,
        match=0.05,
        starting_factor=0.01,
        group = 1
    ):
        super().__init__(space, model)
        self.base_location = position
        self.position = position
        self.speed = speed
        self.direction = direction
        self.vision = vision
        self.separation = separation
        self.cohere_factor = cohere
        self.separate_factor = separate
        self.match_factor = match
        self.starting_factor = starting_factor
        self.base_id = group
        self.neighbors = []
        self.mission: Optional[Mission] = None
        self.inAction = True
    
    def calculate_direction_by_boid_forces(self):
        """
        not in use right now!
        Get the Boid's neighbors, compute the new vector based on Craig Reynolds' Boids.
        """
        # calc base vector
        base_vector = (self.position - self.base_location) * self.starting_factor

        # get only neigbors that are in the same group and not self
        neighbors, distances = self.space.get_agents_in_radius(self.position, radius=self.vision)
        NeighborInGroupFlag =  np.asarray([agent.base_id == self.base_id and agent is not self and isinstance(agent, AirplaneAgent) for agent in neighbors])
        neighbors = list(compress(neighbors, NeighborInGroupFlag))
        self.neighbors = [n for n in neighbors if n is not self]
        
        if len(neighbors) == 0: # If no neighbors, maintain current direction and return a bit to base
            return base_vector
        
        distances = distances[NeighborInGroupFlag]
        delta = self.space.calculate_difference_vector(self.position, agents=neighbors)
        cohere_vector = delta.sum(axis=0) * self.cohere_factor
        separation_vector = (
            -1 * delta[distances < self.separation].sum(axis=0) * self.separate_factor
        )
        match_vector = (
            np.asarray([n.direction for n in neighbors]).sum(axis=0) * self.match_factor
        )

        # Update direction based on behaviors
        new_direction = (base_vector + cohere_vector + separation_vector + match_vector) / len(neighbors)

        return new_direction

    def calculate_direction_by_mission(self):
        """
        Get the direction to the mission destination
        """
        direction_to_mission = (self.mission.destination - self.position)
        return direction_to_mission

    @method_logger(__name__)
    def step(self):
        """
        move the agent based on the mission destination or the boid logic (depricated for now)
        """
        if self.mission is not None:
            # get direction by mission logic
            new_direction = self.calculate_direction_by_mission()
        else:
            #get direction by boid logic for fluid movement based on neighbors
            # new_direction = self.calculate_direction_by_boid_forces()
            new_direction = -self.direction
        
        # calc new direction based on old direction and new direction
        self.direction = self.direction + new_direction
        direction_norm = np.linalg.norm(self.direction)
        if direction_norm>1:
            self.direction = self.direction / np.linalg.norm(self.direction)
        # Move boid
        self.position += self.direction * self.speed

        _mesa_logger.warning(self)

        self.check_mission()
    
    def change_base(self, base_id, base_location):
        """
        change the airplane "base"
        """
        self.base_id = base_id
        self.base_location = base_location

    def check_mission(self):
        """
        check whether the agent is close enough to the mission destination to change the mission stage
        """
        if self.mission is not None:
            distance_to_destination = np.linalg.norm(self.position - self.mission.destination)
            self.mission.check_stage(distance_to_destination)

    def __repr__(self):
        return f"(Agent:{self.unique_id} l {self.position} {self.mission})"
"""A Boid (bird-oid) agent for implementing Craig Reynolds's Boids flocking model.

This implementation uses numpy arrays to represent vectors for efficient computation
of flocking behavior.
"""
from itertools import compress
from typing import Optional
import numpy as np
import uuid
import random
from mesa.experimental.continuous_space import ContinuousSpaceAgent
from mesa.mesa_logging import create_module_logger, method_logger
from mission import Mission
_mesa_logger = create_module_logger()

class AirplaneAgent(ContinuousSpaceAgent):
    """A Boid-style flocker agent.

    The agent follows three behaviors to flock:
        - Cohesion: steering towards neighboring agents
        - Separation: avoiding getting too close to any other agent
        - Alignment: trying to fly in the same direction as neighbors

    Boids have a vision that defines the radius in which they look for their
    neighbors to flock with. Their speed (a scalar) and direction (a vector)
    define their movement. Separation is their desired minimum distance from
    any other Boid.
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
        """Create a new Boid flocker agent.

        Args:
            model: Model instance the agent belongs to
            speed: Distance to move per step
            direction: numpy vector for the Boid's direction of movement
            vision: Radius to look around for nearby Boids
            separation: Minimum distance to maintain from other Boids
            cohere: Relative importance of matching neighbors' positions (default: 0.03)
            separate: Relative importance of avoiding close neighbors (default: 0.015)
            match: Relative importance of matching neighbors' directions (default: 0.05)
        """
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
        self.group_number = group
        self.neighbors = []
        self.uuid = uuid.uuid4()
        self.mission: Optional[Mission] = None
        self.inAction = True
    
    def calculate_direction_by_boid_forces(self):
        """Get the Boid's neighbors, compute the new vector, and move accordingly."""
        # calc base vector
        base_vector = (self.position - self.base_location) * self.starting_factor

        # get only neigbors that are in the same group and not self
        neighbors, distances = self.space.get_agents_in_radius(self.position, radius=self.vision)
        NeighborInGroupFlag =  np.asarray([agent.group_number == self.group_number and agent is not self for agent in neighbors])
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
        return None
    
    def setMisiion(self, mission):
        self.mission = mission
        self.inAction = True

    @method_logger(__name__)
    def step(self):
        if self.mission is not None:
            # get direction by mission logic
            new_direction = self.calculate_direction_by_mission()
        else:
            #get direction by boid logic
            new_direction = self.calculate_direction_by_boid_forces()
        
        # _mesa_logger.warning(new_direction)
        _mesa_logger.warning(f"{self.mission},{self.direction}, {new_direction}")
        self.direction = self.direction + new_direction
        self.direction = self.direction / np.linalg.norm(self.direction)
        # Move boid
        self.position += self.direction * self.speed

        _mesa_logger.warning(self)
    
    def __repr__(self):
        return f"(agent {self.unique_id} g {self.group_number} l {self.position} d {self.direction})"
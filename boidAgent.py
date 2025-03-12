"""A Boid (bird-oid) agent for implementing Craig Reynolds's Boids flocking model.

This implementation uses numpy arrays to represent vectors for efficient computation
of flocking behavior.
"""
from itertools import compress
import numpy as np
import uuid
import random
from mesa.experimental.continuous_space import ContinuousSpaceAgent
from mesa.mesa_logging import create_module_logger, method_logger

_mesa_logger = create_module_logger()

class MyBoid(ContinuousSpaceAgent):
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
        position=(0, 0),
        speed=1,
        direction=(1, 1),
        vision=1,
        separation=1,
        cohere=0.03,
        separate=0.015,
        match=0.05,
        starting_factor=0.01,
        Maxgroup = 1
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
        self.startign_position = position
        self.position = position
        self.speed = speed
        self.direction = direction
        self.vision = vision
        self.separation = separation
        self.cohere_factor = cohere
        self.separate_factor = separate
        self.match_factor = match
        self.starting_factor = starting_factor
        self.group = random.randint(1, Maxgroup)
        self.neighbors = []
        self.uuid = uuid.uuid4()
    
    @method_logger(__name__)
    def step(self):
        """Get the Boid's neighbors, compute the new vector, and move accordingly."""
        # calc base vector
        base_vector = (self.position - self.startign_position) * self.starting_factor
        base_vector = 0


        # get only neigbors that are in the same group and not self
        neighbors, distances = self.space.get_agents_in_radius(self.position, radius=self.vision)
        NeighborInGroupFlag =  np.asarray([agent.group == self.group and agent is not self for agent in neighbors])
        neighbors = list(compress(neighbors, NeighborInGroupFlag))
        self.neighbors = [n for n in neighbors if n is not self]
        
        if len(neighbors) == 0: # If no neighbors, maintain current direction and return a bit to base
            self.direction += base_vector
            self.position += self.direction * self.speed
            return
        
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
        self.direction += (base_vector + cohere_vector + separation_vector + match_vector) / len(neighbors)

        # Normalize direction vector
        self.direction /= np.linalg.norm(self.direction)

        # Move boid
        self.position += self.direction * self.speed

        _mesa_logger.warning(self)
    
    def __repr__(self):
        return f"(agent {self.unique_id} g {self.group} l {self.position} d {self.direction})"
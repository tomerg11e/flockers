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

class BaseAgent(ContinuousSpaceAgent):
    """A static agent repressenting air force base.
    """
    def __init__(
        self,
        model,
        space,
        position=np.array([ 0, 0]),
        group = 1
    ):
        """Create a new Base agent.

        Args:
            model: Model instance the agent belongs to
            position: numpy vector for the Base's position
            group: the group number of the base
        """
        super().__init__(space, model)
        self.position = position
        self.group_number = group

    def step(self):
        pass

    def __repr__(self):
        return f"(base:{self.unique_id} l {self.position})"
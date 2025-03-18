import numpy as np
import uuid
from typing import List, Optional
class Mission:

    valid_mission_types = ["ATTACK", "SWITCH_BASE", "Take_To_BASE", "RESCUE"]
    MISSION_COMPLETE = "COMPLETED"
    MISSION_PENDING = "PENDING"
    def __init__(self, model, mission_type: str, destination: np.ndarray, mission_stages: List[str], detection_radius: float = 0.5):
        if mission_type not in Mission.valid_mission_types:
            raise ValueError(f"Invalid mission type. Choose from: {Mission.valid_mission_types}")
        
        if not (isinstance(destination, np.ndarray) and destination.shape == (2,)):
            raise ValueError("destination must be a NumPy ndarray of shape (2,).")
        
        if not isinstance(mission_stages, List):
            raise ValueError("Stages must be a list.")
        self.model = model
        self.mission_type = mission_type
        self.destination = destination
        self.stages = [Mission.MISSION_PENDING, *mission_stages, Mission.MISSION_COMPLETE]
        self.stage = self.stages[0]
        self.uuid = uuid.uuid4()
        self.detection_radius = detection_radius
    
    def change_stage(self):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def check_stage(self, distance_to_destination):
        if distance_to_destination < self.detection_radius:
            self.change_stage()
    
    def __repr__(self):
        return f"Mission(type={self.mission_type}, mission_location={self.destination}, stage={self.stage})"

class BaseMission(Mission):
    """
    BaseMission is a mission that completed by going to a base
    """

    BASE_STAGES = ["TO_BASE"]

    def __init__(self, model, mission_type: str, base_id: Optional[int] = None):
        if base_id is None:
            base_id = model.rng.integers(0, model.basesNum)
        self.base_id = base_id
        destination = model.bases_position[self.base_id]
        super().__init__(model, mission_type, destination, BaseMission.BASE_STAGES)
        self.agent = None
    
    def change_stage(self):
        if self.stage == Mission.MISSION_PENDING:
            self.stage = BaseMission.BASE_STAGES[0]
            return
        if self.stage == BaseMission.BASE_STAGES[0]:
            self.stage = Mission.MISSION_COMPLETE
            self.agent.change_base(self.base_id ,self.destination)
            self.model.mission_finished(self)
            self.agent.mission = None
            return

class BoomerangMission(Mission):
    """
    A mission that consist of going to a location and back to base
    """
    BOOMERANG_STAGES = ["TO_TARGET", "TO_BASE"]

    def __init__(self, model, mission_type: str, destination: Optional[np.ndarray] = None):
        if destination is None:
            destination = model.rng.uniform(0, 1, size=(2,)) * model.space.size
        super().__init__(model, mission_type, destination, BoomerangMission.BOOMERANG_STAGES)
        self.target_location = destination
        self.agent = None
    
    def change_stage(self):
        if self.stage == Mission.MISSION_PENDING:
            self.stage = BoomerangMission.BOOMERANG_STAGES[0]
            self.destination = self.target_location
            return
        if self.stage == BoomerangMission.BOOMERANG_STAGES[0]:
            self.stage = BoomerangMission.BOOMERANG_STAGES[1]
            self.destination = self.agent.base_location
            return
        if self.stage == BoomerangMission.BOOMERANG_STAGES[1]:
            self.stage = Mission.MISSION_COMPLETE
            self.model.mission_finished(self)
            self.agent.mission = None
            return

class AttackMission(BoomerangMission):

    def __init__(self, model):
        super().__init__(model, "ATTACK")

class RescueMission(BoomerangMission):

    def __init__(self, model):
        super().__init__(model, "RESCUE")

class SwitchBaseMission(BaseMission):

    def __init__(self, model):
        super().__init__(model, "SWITCH_BASE")

class TakeToBaseMission(BaseMission):

    def __init__(self, model):
        super().__init__(model, "Take_To_BASE")

OptionalMissionClasses = [AttackMission, SwitchBaseMission, TakeToBaseMission, RescueMission]
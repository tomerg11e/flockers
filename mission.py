import numpy as np
import uuid
from typing import List, Optional
class Mission:

    valid_mission_types = ["ATTACK", "SWITCH_BASE"]
    MISSION_COMPLETE = "COMPLETED"
    MISSION_PENDING = "PENDING"
    def __init__(self, model, mission_type: str, destination: np.ndarray, mission_stages: List[str], detection_radius: float = 0.5):
        if mission_type not in Mission.valid_mission_types:
            raise ValueError(f"Invalid mission type. Choose from: {Mission.valid_mission_types}")
        
        if not (isinstance(destination, np.ndarray) and destination.shape == (2,)):
            raise ValueError("Location must be a NumPy ndarray of shape (2,).")
        
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

class AttackMission(Mission):
    ATTACK_STAGES = ["TO_TARGET", "TO_BASE"]

    def __init__(self, model):
        destination = model.rng.uniform(0, 1, size=(2,)) * model.space.size
        super().__init__(model, "ATTACK",destination, AttackMission.ATTACK_STAGES)
        self.attack_location = destination
        self.agent = None
    
    def change_stage(self):
        if self.stage == Mission.MISSION_PENDING:
            self.stage = AttackMission.ATTACK_STAGES[0]
            self.destination = self.attack_location
            return
        if self.stage == AttackMission.ATTACK_STAGES[0]:
            self.stage = AttackMission.ATTACK_STAGES[1]
            self.destination = self.agent.base_location
            return
        if self.stage == AttackMission.ATTACK_STAGES[1]:
            self.stage = Mission.MISSION_COMPLETE
            self.model.mission_finished(self)
            self.agent.mission = None
            return

class SwitchBaseMission(Mission):

    SWITCH_BASE_STAGES = ["TO_BASE"]

    def __init__(self, model):
        self.base_id = model.rng.integers(0, model.basesNum)
        destination = model.bases_position[self.base_id]
        super().__init__(model, "SWITCH_BASE", destination, SwitchBaseMission.SWITCH_BASE_STAGES)
        self.agent = None
    
    def change_stage(self):
        if self.stage == Mission.MISSION_PENDING:
            self.stage = SwitchBaseMission.SWITCH_BASE_STAGES[0]
            return
        if self.stage == SwitchBaseMission.SWITCH_BASE_STAGES[0]:
            self.stage = Mission.MISSION_COMPLETE
            self.agent.change_base(self.base_id ,self.destination)
            self.model.mission_finished(self)
            self.agent.mission = None
            return

OptionalMissionClasses = [AttackMission, SwitchBaseMission]
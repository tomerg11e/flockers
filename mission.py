class Mission:

    valid_mission_types = ["FLY", "SURV"]
    valid_mission_statuses = ["PENDING", "ASSIGNED", "COMPLETED"]

    def __init__(self, mission_type, location):
        if mission_type not in Mission.valid_mission_types:
            raise ValueError(f"Invalid mission type. Choose from: {Mission.valid_mission_types}")
        
        if not (isinstance(location, tuple) and len(location) == 2 and 
                all(isinstance(coord, (int, float)) for coord in location)):
            raise ValueError("Location must be a tuple with two numeric values (x, y).")
        
        self.mission_type = mission_type
        self.location = location
        self.status = "PENDING"
    
    def __repr__(self):
        return f"Mission(type={self.mission_type}, location={self.location}, status={self.status})"
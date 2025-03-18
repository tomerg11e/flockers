This project is a Mesa-based multi-agent simulation that models the movement of airplanes in a dynamic environment. Each airplane agent moves within a continuous space, influenced by factors like speed, direction, and nearby agents. Additionally, airplanes are assigned generated missions, which dictate their movement and behavior.

Airplane Agent Behavior

    If a mission is assigned, the airplane moves toward its destination.
    Without a mission, it follows Boid-style flocking (currently deprecated).
    Airplanes can change bases dynamically.
    Missions are checked in every step to determine if they are complete.
    An example to the flocking behaviour can be viewed in
    https://mesa.readthedocs.io/stable/examples/basic/boid_flockers.html

can be run using 
solara run app.py
or running the testing.py file


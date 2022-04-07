# Robot_Communication_Hub
This Repository is the source code for a Communication Hub which allows the communication of robots across a particularly network.

## Requirements
The following requirements are needed:
- Python 3.X
- opencv-python
- opencv_contrib-python

## Implementation
The main entry file to the repository is 'CommHub_udp.py'. Running this code will instantiate two objects: A main Communication Hub object, class found in 'commhub.py' and a Camera Tracker object, class found in 'ArUcoTracker.py'.

The Robot Arena (the area where robots are held) need to be defined by two positioning ArUco markers. These should be positioned at a fixed real world distance and set in the ArUcoTracker.py under the 'self.arenaMeasurement' variable (measured in metres).
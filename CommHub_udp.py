#!/usr/bin/python3
import time

from threading import Lock

from ArUcoTracker import ArUcoTracker
from commhub import CommHub
from graphMaker import graphMaker

# Parameters for the Buzz ComHub
FORWARD_FREQ = 500  # Hz

# This is the IP address in which the Camera and Communication Hub are hosted
SERVER_IP = '144.32.175.138'
PORT = 4242

if __name__ == '__main__':

  comm_hub = CommHub(forward_freq=FORWARD_FREQ, host=SERVER_IP, port=PORT)
  robotTracker = ArUcoTracker(HOST=SERVER_IP, PORT=PORT, commHub=comm_hub)

  graphs = graphMaker(commHub=comm_hub, frequency=1, experiment_length=10, num_robots=10)

  time.sleep(0.25)
  while graphs.gatherDataThread.is_alive():
    time.sleep(0.1)
  graphs.draw_graphs()

  try:
    while True:
      time.sleep(0.1)
  except KeyboardInterrupt:
    pass
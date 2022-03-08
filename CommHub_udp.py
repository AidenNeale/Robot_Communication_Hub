#!/usr/bin/python3
import time

from threading import Lock

from ArUcoTracker import ArUcoTracker
from commhub import CommHub

# Parameters for the Buzz ComHub
FORWARD_FREQ = 50  # Hz

# This is the IP address in which the Camera and Communication Hub are hosted
SERVER_IP = '144.32.175.138'


if __name__ == '__main__':

  comm_hub = CommHub(forward_freq=FORWARD_FREQ, host=SERVER_IP)
  # robotTracker = ArUcoTracker()
  try:
    while True:
      time.sleep(0.1)
  except KeyboardInterrupt:
    pass
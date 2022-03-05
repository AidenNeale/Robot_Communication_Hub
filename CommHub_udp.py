#!/usr/bin/python3

import time
from threading import Lock

from commhub import *

# Parameters for the Buzz ComHub
FORWARD_FREQ = 50  # Hz

CAM_IP = '127.0.0.1'
HUB_IP = '127.0.0.1'

lock_opti = Lock()



if __name__ == '__main__':

  comm_hub = CommHub(forward_freq=FORWARD_FREQ)

  try:
    while True:
      time.sleep(0.1)
  except KeyboardInterrupt:
    pass
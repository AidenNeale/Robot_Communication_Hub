from threading import Thread, Lock

import numpy as np
import socket
import sys
import time

import cv2

from packet import Packet

class ArUcoTracker:
  ARUCO_DICT = {
    # "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    # "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    # "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    # "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    # "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    # "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    # "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    # "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    # "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    # "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    # "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    # "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    # "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    # "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    # "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    # "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    # "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    # "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    # "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    # "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
  }
  POSSIBLE_RESOLUTIONS = {
    "160x120":   [160, 120],
    "176x144":   [176, 144],
    "320x240":   [320, 240],
    "352x288":   [352, 288],
    "640x480":   [640, 480],
    "1024x768":  [1024, 768],
    "1280x720": [1280, 720]
  }

  def __init__(self, arUco_type="DICT_5X5_50", HOST = '127.0.0.1', PORT = '4242',
                    CHOSEN_CAMERA = 2, POSITION_MARKERS = 0) -> None:

    self.CHOSEN_CAMERA = CHOSEN_CAMERA
    self.DESTINATION = (HOST, PORT)
    self.POSITION_MARKERS = POSITION_MARKERS

    self.packets_lock = Lock()

    self.arucoDict = cv2.aruco.Dictionary_get(self.ARUCO_DICT[arUco_type])
    self.arucoParams = cv2.aruco.DetectorParameters_create()
    self.id2coords = {}

    self.arenaMaxX = 0
    self.arenaMaxY = 0
    self.arenaMinX = 0
    self.arenaMinY = 0

    self.arenaMeasurement = 0.88 # This is relevant to the distance of ArUco Tags defining the Robot Arena in m

    self.cap = self.init_camera()
    self.socket = self.init_socket()
    self.scale = self.calculate_scale()
    print(f"Scaling Factor for 1m: {self.scale}")

    self.trackRobots_thread = Thread(target=self.track_robots, name="Track Robots")
    self.trackRobots_thread.start()
    self.sendCoordinates_thread = Thread(target=self.send_coordinates, name="Send Coordinates")
    self.sendCoordinates_thread.start()

  '''

  '''
  def init_camera(self) -> cv2.VideoCapture:
    # Open Video Capture with Chosen Camera on appropriate USB
    cap = cv2.VideoCapture(self.CHOSEN_CAMERA)
    if not cap.isOpened():
      # Fallback attempt to open Video Capture with Laptop Webcam
      cap = cv2.VideoCapture(0)
    if not cap.isOpened():
      print("Cannot Open Camera")
      exit()

    # Change Resolution of the frame to 1024X768
    self.change_res(cap, self.POSSIBLE_RESOLUTIONS["1280x720"])
    time.sleep(1.5)
    return cap


  '''

  '''
  def change_res(self, cap, resolution) -> None:
    cap.set(3, resolution[0])
    cap.set(4, resolution[1])

  '''

  '''
  def init_socket(self) -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      # Send to server using created UDP socket


  '''

  '''
  def calculate_scale(self) -> float:
    oneMetreScaleFactor = 0

    while True:
      ret, frame = self.cap.read()
      if not ret:
        print("Can't received frame (stream end?). Exiting...")
        break

      # detect ArUco markers in the input frame
      (tags, ids, rejected) = cv2.aruco.detectMarkers(frame,
        self.arucoDict, parameters=self.arucoParams)
      # verify *at least* one ArUco marker was detected
      # and that two Identifying Markers were detected
      if len(tags) > 0 and np.count_nonzero(ids.flatten() == self.POSITION_MARKERS) == 2:
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        positionMarkers = {}
        for index, (markerCorner, markerID) in enumerate(zip(tags, ids)):
          positionMarkers[index] = {}
          if markerID != 0:
            pass
          corners = markerCorner.reshape((4, 2))
          (positionMarkers[index]["topLeft"],
            positionMarkers[index]["topRight"],
            positionMarkers[index]["bottomRight"],
            positionMarkers[index]["bottomLeft"]) = corners

        # At this stage, position_markers will have stored the corners of the
        # ArUco Tags
        # print(f"{positionMarkers}") # Debug
        topMaxX, topMaxY = float('-inf'), float('-inf')
        bottomMinX, bottomMinY = float('inf'), float('inf')

        # Note: Top Left corner of the Camera is 0, 0
        # This means the top corners are closer to zero (Y Min) and
        # bottom corners are closer to Y Max
        for indexes in positionMarkers:
          topMaxX = max(positionMarkers[indexes]['bottomRight'][0], topMaxX)
          topMaxX = max(positionMarkers[indexes]['topRight'][0], topMaxX)
          topMaxY = max(positionMarkers[indexes]['bottomLeft'][1], topMaxY)
          topMaxY = max(positionMarkers[indexes]['bottomRight'][1], topMaxY)

          bottomMinX = min(positionMarkers[indexes]['topLeft'][0], bottomMinX)
          bottomMinX = min(positionMarkers[indexes]['bottomLeft'][0], bottomMinX)
          bottomMinY = min(positionMarkers[indexes]['topLeft'][1], bottomMinY)
          bottomMinY = min(positionMarkers[indexes]['topRight'][1], bottomMinY)
        print(f"Highest Coordinate: {topMaxX}: {topMaxY}, Lowest Coordinate: {bottomMinX}: {bottomMinY}") # Debug

        # Set global values to keep track of arena Coordinates
        self.arenaMaxX, self.arenaMaxY = topMaxX, topMaxY
        self.arenaMaxY, self.arenaMinY = bottomMinX, bottomMinY

        # Calculates the number of pixels in 1 Metre
        oneMetreScaleFactor = (topMaxY - bottomMinY) / self.arenaMeasurement

        # Cleans up Window created
        cv2.destroyAllWindows()
        return oneMetreScaleFactor

      # Display the resulting frame
      cv2.imshow('Arena_Calibration', frame)
      # Waits for exit of the program
      if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        return -1

  '''

  '''
  def track_robots(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        print("Can't received frame (stream end?). Exiting...")
        break

      (tags, ids, rejected) = cv2.aruco.detectMarkers(frame,
        self.arucoDict, parameters=self.arucoParams)

      cv2.aruco.drawDetectedMarkers(frame, tags, borderColor = (0, 255, 0))


      if len(tags) > 0:
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        positionMarkers = {}
        for (markerCorner, markerID) in zip(tags, ids):
          # Ignores ArUco Tags of ID 'POSITION_MARKERS' as these are reserved for trackers
          # if markerID == self.POSITION_MARKERS:
            # pass
          corners = markerCorner.reshape((4, 2))
          (topLeft, topRight, bottomRight, bottomLeft) = corners

          # Finds the Centre Point of the robot and draws onto the frame
          centreX, centreY = self.get_robot_centre(topLeft, bottomRight)
          cv2.circle(frame, (int(centreX), int(centreY)), 4, (0, 0, 255), -1)

          # Scales the Robots Centre Point to Metres
          coordinates = self.scale_coordinates(centreX, centreY)
          # print(f"Robot {markerID} is positioned: {coordinates}")
          self.packets_lock.acquire()
          self.id2coords[markerID] = coordinates
          self.packets_lock.release()

      # Display the resulting frame
      cv2.imshow('Robot_Detection', frame)
      # Waits for exit of the program
      if cv2.waitKey(1) == ord('q'):
        sys.exit()

  '''
  Scales any coordinates to convert pixels to metres
  '''
  def scale_coordinates(self, x, y):
    scaledX = (x - self.arenaMinX) / self.scale
    scaledY = (y - self.arenaMinY) / self.scale
    scaledZ = 0
    return (scaledX, scaledY, scaledZ)

  '''
  Calculates the centre of the robot by taking the averages of the Tag Corners
  '''
  def get_robot_centre(self, topLeft, bottomRight):
    centreX = (abs(topLeft[0]+bottomRight[0])/2)
    centreY = (abs(topLeft[1]+bottomRight[1])/2)
    return (centreX, centreY)



  '''

  '''
  def send_coordinates(self):
    while True:
      readDictionary = self.id2coords.items()
      for robotID, robotCoordinates in readDictionary:
        # Send Packet to the Communication Hub for auto-forwarding onto robots
        self.packets_lock.acquire()
        packet = Packet(
          robotCoordinates[0], robotCoordinates[1], robotCoordinates[2], robotID)
        self.packets_lock.release()
        msg = packet.byte_string()
        self.socket.sendto(msg, self.DESTINATION)

'''
  TODO:
    - Add Pinhole Camera Calibration to accomodate for Camera Distortion
      |-> Look into: https://automaticaddison.com/how-to-perform-pose-estimation-using-an-aruco-marker/

'''
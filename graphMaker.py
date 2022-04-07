from threading import Thread, Lock
import itertools
import math
import matplotlib.pyplot as plt
import time
import numpy

class graphMaker():
  def __init__(self, commHub=None, frequency=1, experiment_length=30):
    self.commHub = commHub
    self.frequency = frequency
    self.experiment_length = experiment_length

    self.current_time = 0
    self.X = []
    self.Y = []
    self.gatherDataThread = Thread(target=self.gather_data, name="Retrieve Data")
    self.gatherDataThread.start()


  def gather_data(self):
    while self.experiment_length > self.current_time:
      saved_locations = self.commHub.get_locations()
      total_dist = 0
      num_of_indiv_comps = 0

      try:
        for comparison in itertools.combinations(saved_locations.values(), 2):
          #Comparison saved in the form ((ID, POSE), (ID, POSE))
          distance = math.sqrt(math.pow(comparison[0][0] - comparison[1][0], 2) +
                              math.pow(comparison[0][1] - comparison[1][1], 2) +
                              math.pow(comparison[0][2] - comparison[1][2], 2))
          total_dist += distance
          num_of_indiv_comps += 1

        total_average_distance = total_dist / num_of_indiv_comps

        self.X.append(self.current_time)
        self.Y.append(total_average_distance)
      except ZeroDivisionError:
        continue # Robot Comm Hub not yet initialised
      time.sleep(self.frequency)
      self.current_time += self.frequency


  def draw_graphs(self):
    print(self.X)
    print(self.Y)

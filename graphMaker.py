from threading import Thread, Lock
import csv
import itertools
import math
import matplotlib.pyplot as plt
import time
import numpy

class graphMaker():
  def __init__(self, commHub=None, frequency=1, experiment_length=30, num_robots=10):
    self.commHub = commHub
    self.frequency = frequency
    self.experiment_length = experiment_length
    self.num_robots = num_robots

    self.current_time = 0

    #Graph Variables
    self.time_axis = []
    self.total_distance_axis = []
    self.indiv_distance_axis = {}

    input("Press Enter to Begin Data Collection")
    self.gatherDataThread = Thread(target=self.gather_data, name="Retrieve Data")
    self.gatherDataThread.start()


  def calc_average_total_distance(self, saved_locations, comparison):
    return math.sqrt(math.pow(saved_locations[comparison[0]][0] - saved_locations[comparison[1]][0], 2) +
                    math.pow(saved_locations[comparison[0]][1] - saved_locations[comparison[1]][1], 2) +
                    math.pow(saved_locations[comparison[0]][2] - saved_locations[comparison[1]][2], 2))

  def write_to_csv(self, total_dist):
    with open(r'results/total_dist.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(total_dist)


  def gather_data(self):
    while self.experiment_length > self.current_time:
      saved_locations = self.commHub.get_locations()
      total_dist = 0
      num_of_indiv_comps = 0
      indiv_distance = {}

      try:
        for comparison in itertools.combinations(saved_locations, 2):
          #Comparison saved in the form (ID, ID)
          distance = self.calc_average_total_distance(saved_locations, comparison)
          total_dist += distance
          num_of_indiv_comps += 1

          for indiv_robot in comparison:
            try:
              indiv_distance[indiv_robot].append(distance)
            except:
              indiv_distance[indiv_robot] = []

        total_average_distance = total_dist / num_of_indiv_comps

        for key in indiv_distance:
          try:
            self.indiv_distance_axis[key].append(sum(indiv_distance[key])/(self.num_robots-1))
          except:
            self.indiv_distance_axis[key] = [sum(indiv_distance[key])/(self.num_robots-1)]

        print(self.indiv_distance_axis)
        self.time_axis.append(self.current_time)
        self.total_distance_axis.append(total_average_distance)
      except ZeroDivisionError:
        continue # Robot Comm Hub not yet initialised

      time.sleep(self.frequency)
      self.current_time += self.frequency
    self.write_to_csv([total_average_distance])


  def draw_graphs(self):
    plt.title('Graph showing total average distance for the swarm')
    plt.xlabel('Time Steps')
    plt.ylabel('Average Distance (m)')

    plt.plot(self.time_axis, self.total_distance_axis, color='blue', linewidth=3)

    plt.savefig('graphs/test1.png')
    plt.clf()

    plt.title('Graph showing individual average distance for the swarm')
    plt.xlabel('Time Steps')
    plt.ylabel('Average Distance (m)')
    for key, value in self.indiv_distance_axis.items():
      plt.plot(self.time_axis, value, label=key)
    plt.savefig('graphs/indiv1.png')

    pass

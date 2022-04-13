import csv
import matplotlib.pyplot as plt
import numpy

if __name__ == '__main__':
  my_control_data = numpy.genfromtxt('results/control_data.csv', delimiter=',')
  packet_loss_data_25 = numpy.genfromtxt('results/packet_loss_25.csv', delimiter=',')
  packet_loss_data_50 = numpy.genfromtxt('results/packet_loss_50.csv', delimiter=',')
  packet_loss_data_75 = numpy.genfromtxt('results/packet_loss_75.csv', delimiter=',')


  my_dict = {'Control': my_control_data,
              'Packet Loss 25%': packet_loss_data_25,
              'Packet Loss 50%': packet_loss_data_50,
              'Packet Loss 75%': packet_loss_data_75
            }

  packet_loss_title = "Comparison showing Buzz's aggregation performance when experiencing packet loss"
  positioning_noise_title = "Comparison showing Buzz's aggregation performance when introducing positioning noise"

  plt.boxplot(my_dict.values())
  plt.title(packet_loss_title)
  plt.xlabel('Experiments')
  plt.ylabel('Average Distance (m) after 45 time units')
  plt.xticks([1, 2, 3, 4], my_dict.keys())
  plt.show()
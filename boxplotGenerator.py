import csv
import matplotlib.pyplot as plt
import numpy

if __name__ == '__main__':
  my_control_data = numpy.genfromtxt('results/control_data.csv', delimiter=',')

  packet_loss_data_25 = numpy.genfromtxt('results/packet_loss_25.csv', delimiter=',')
  packet_loss_data_50 = numpy.genfromtxt('results/packet_loss_50.csv', delimiter=',')
  packet_loss_data_75 = numpy.genfromtxt('results/packet_loss_75.csv', delimiter=',')

  # position_noise_data_1cm = numpy.genfromtxt('results/position_noise_data_1cm.csv', delimiter=',')
  # position_noise_data_5cm = numpy.genfromtxt('results/position_noise_data_5cm.csv', delimiter=',')
  # position_noise_data_10cm = numpy.genfromtxt('results/position_noise_data_10cm.csv', delimiter=',')
  # position_noise_data_20cm = numpy.genfromtxt('results/position_noise_data_20cm.csv', delimiter=',')


  my_dict = {'Control': my_control_data,
              'Packet Loss 25%': packet_loss_data_25,
              'Packet Loss 50%': packet_loss_data_50,
              'Packet Loss 75%': packet_loss_data_75
            }

  # my_dict = {'Control': my_control_data,
  #             'Position Noise 1cm std': position_noise_data_1cm,
  #             'Position Noise 5cm std': position_noise_data_5cm,
  #             'Position Noise 10cm std': position_noise_data_10cm,
  #             'Position Noise 20cm std': position_noise_data_20cm
  #           }

  packet_loss_title = "Comparison showing Buzz's aggregation performance when experiencing packet loss"
  positioning_noise_title = "Comparison showing Buzz's aggregation performance when introducing positioning noise"

  plt.boxplot(my_dict.values())
  plt.title(packet_loss_title)
  # plt.title(positioning_noise_title)
  plt.xlabel('Experiments')
  plt.ylabel('Average Distance (m) after 45 time units')
  plt.xticks([1, 2, 3, 4], my_dict.keys())
  # plt.xticks([1, 2, 3, 4, 5], my_dict.keys())
  plt.savefig('graphs/packet_loss_boxplots.png')
  plt.show()
  plt.clf()
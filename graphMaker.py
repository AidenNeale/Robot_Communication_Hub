from threading import Thread, Lock
import matplotlib.pyplot as plt


class graphMaker():
  def __init__(self, commHub):
    self.commHub = commHub

    self.X = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    self.Y = [100, 120, 132, 140, 156, 158, 172, 189, 200, 225]

    self.gatherDataThread = Thread(target=self.gather_data, name="Retrieve Data")
    self.gatherDataThread.start()


  def gather_data(self):
    print(self.commHub.get_locations())

  def draw_graphs(self):
    pass

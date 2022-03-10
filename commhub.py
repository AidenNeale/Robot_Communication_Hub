import numpy as np
import socket
import time

from collections import defaultdict
from threading import Thread, Lock

from packet import Packet


class CommHub:
    '''
    Communication Hub
    Facilitate communication between the robots, as well as update their absolute positions
    :param clients: list. Destination IPs served by this CommHub
    :param forward_freq: float. Frequency of automatic calls to CommHub.forward_packets in Hertz
        Set forward_freq=0 for maximum frequency
        If left as None, CommHub.forward_packets must be called manually
    :param neighbor_distance: float. The range for communication between robots. Distance units must
        be consistent with the units used for CommHub.update_position
    :param host: string. The host of the CommHub. HOST default is "localhost"
    :param port: int. The port of the CommHub. PORT default is 8000
    '''

    def __init__(self, forward_freq=None, neighbor_distance=1.7, host='144.32.175.138', port=4242):
        self.alive = True
        self.locs = {}  # comm_id : np.array()
        self.neighbor_distance = neighbor_distance
        self.packets = defaultdict(list)
        self.packets_lock = Lock()
        self.id2ip = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.socket.bind((host, port))
        except OSError as e:
            self.socket.close()
            print("ERROR: Trying to create a CommHub on a busy address")
            raise e

        if forward_freq is not None:
            if forward_freq:
                period = 1/forward_freq
            else:
                period = 0

            self.forward_thread = Thread(target=self.auto_forward, args=(
                period,), name="Auto Forwarder")
            self.forward_thread.start()

        self.received_thread = Thread(target=self.receive, name="Receiver")
        self.received_thread.start()


    '''
    PRIVATE
    New thread that blocks until new packet comes. Packets are added to self.packets
    '''

    def receive(self):
        print("Receiving Thread Initialised...")  # Debug
        while self.alive: # While Comm Hub Alive
            received_packet = Packet.from_socket(self.socket) # Read Packet from Socket
            # Update IP/id database
            self.id2ip[received_packet.comm_id] = received_packet.addr

            if received_packet:
                print("Received packet from Robot {}".format(received_packet.comm_id))  # Debug
                self.packets_lock.acquire()
                self.packets[received_packet.comm_id].append(received_packet)
                self.packets_lock.release()
            else:
                break


    '''
    PRIVATE
    Automatically call CommHub.forward_packets at a certain frequency
    :param period: float. Time between calls to CommHub.forward_packets in seconds
    '''
    def auto_forward(self, period):
      print("Forwarding Thread Initialised...")
      while self.alive:
        self.forward_packets()
        time.sleep(period)


    '''
    Keep the communication flowing between robots.
    All information shared between robots, and any updates to positions
    are not sent unless this function is called.
    '''
    def forward_packets(self):
        # For all known robots, get addresses and ids
        for robot_id1, robot_addr1 in self.id2ip.items():

            # If there are packets from these robots, put them into a data structure
            self.packets_lock.acquire()
            tmppackets = self.packets[robot_id1][:]
            self.packets[robot_id1] = []
            self.packets_lock.release()
            if len(tmppackets) == 0:
              tmppackets = [Packet(0.0, 0.0, 0.0, robot_id1)]
            # Cycle through all other robots and forward the packets
            for robot_id2, addr2 in self.id2ip.items():
                try:
                    # Compute relative vector and distance
                    rel_vector = self.locs[robot_id1][:-1] - self.locs[robot_id2][:-1]
                    distance = np.linalg.norm(rel_vector)

                    # Send updated own location to the robot
                    if robot_id1 == robot_id2:
                        self.send_to(robot_id2, Packet(
                            self.locs[robot_id1][0], self.locs[robot_id1][1], self.locs[robot_id1][2], robot_id1, theta=self.locs[robot_id1][3]), robot_id1)

                    # Only forward packets if within comms distance, in RAB format
                    else:  # if distance < self.neighbor_distance:
                        # Compute azimuth (theta) and elevation (phi)
                        rel_theta = np.arctan2(rel_vector[1], rel_vector[0])
                        rel_phi = np.arctan2(
                            rel_vector[2], np.linalg.norm(rel_vector[:2]))

                        # convert angle to receivers coordinate
                        rel_theta = rel_theta - self.locs[robot_id2][3]
                        # Wrap angles
                        azimuth = rel_theta + 2*np.pi if rel_theta < 0. else rel_theta
                        elevation = rel_phi + 2*np.pi if rel_phi < 0. else rel_phi

                        self.send_to_with_rb(robot_id2, tmppackets, np.array(
                            (distance*100.0, azimuth, elevation)))  # *100.0 to obtain [cm] on board
                except KeyError as e:
                    pass  # print("No locs for Robot {}".format(robot_id2))


    '''
    PRIVATE
    Send packets to a destination
    :param destination: the id of the robot to send the packages to
    :param packets: a list of Packet objects, or just a single Packet
    '''
    def send_to(self, destination, packets, sender):
        try:
            packets[0]
        except (AttributeError, TypeError):
            self.socket.sendto(packets.byte_string(), self.id2ip[destination])
            print(" comm packet sender {} receiver {}".format(sender,destination))
            return

        for packet in packets:
            msg = packet.byte_string()
            self.socket.sendto(msg, self.id2ip[destination])


    '''
    PRIVATE
    Send packets to a destination with range and bearing incorporated
    :param destination: the id of the robot to send the packages to
    :param packets: a list of Packet objects, or just a single Packet
    '''
    def send_to_with_rb(self, destination, packets, rel_rb):
        try:
            packets[0]
        except (AttributeError, TypeError):
            packets.set_rb(rel_rb[0], rel_rb[1], rel_rb[2])
            self.socket.sendto(packets.byte_string(), self.id2ip[destination])
            return

        for packet in packets:
            packet.set_rb(rel_rb[0], rel_rb[1], rel_rb[2])
            msg = packet.byte_string()
            self.socket.sendto(msg, self.id2ip[destination])



    # '''
    # Update the position of the specified robot.
    # :param robot_id: int. the id of the robot whose position is to be updated
    # :param loc: list, tuple, or numpy.array. The updated position of the robot
    # :param yaw float yaw euiler angle
    # :return: bool. True if update was successful
    # '''

    # def update_position(self, robot_id, loc, yaw):
    #     self.locs[int(robot_id)] = np.append(np.array(loc), yaw)
    #     print("Robot {} pos {}".format(robot_id, self.locs[robot_id]))
    #     return True

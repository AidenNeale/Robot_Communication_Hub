import struct
import time

MSG_SIZE = 500

class Packet:
    '''
    PRIVATE
    Create a Packet to be sent over a socket
    :params x, y, z: absolute coordinates of sender
    :param sender_id: comm_id of sender
    :param msgs: list of bytes objects. Each bytes object is fed directly to the buzz script using feed_buzz_message
    '''

    def __init__(self, x, y, z, sender_id, msgs=[], theta=0, received_time=0, addr=('0.0.0.0', 4242)):
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.comm_id = sender_id
        self.msgs = msgs
        self.received_time = received_time
        self.addr = addr


    def set_rb(self, rng, bearing, elevation):
      '''
      Setter Function for Range, Bearing and Elevation

      Parameters:
      ------------
      rng ->
        Range between two robots
      bearing ->
        Bearing between two robots
      elevation ->
        Elevation between the robot and the camera
      '''
      self.x = rng
      self.y = bearing
      self.z = elevation


    def byte_string(self):
      '''
      Convert packet to a bytes object containing all the information.

      Contents:
      ---------
      * 2 bytes comm_id
      * 4 bytes x
      * 4 bytes y
      * 4 bytes z
      * 4 bytes theta
      * for each message {
        2 bytes message length (n)
        n bytes message
      }
      * 4 bytes (0000)

      Returns:
      -----------
      b_string -> bytes
        Bytes object representing entire packet
      '''
      b_string = struct.pack('=H4f', int(self.comm_id), float(
        self.x), float(self.y), float(self.z), float(self.theta))
      for msg in self.msgs:
        b_string += struct.pack('H', len(msg))
        b_string += msg
      b_string += struct.pack('I', 0)
      while len(b_string) < MSG_SIZE:
        b_string += struct.pack('B', 0)
      return b_string



    @staticmethod
    def from_socket(socketUDP):
      '''
      Create a packet from a socket
      Block until a string of bytes comes in, and unpack these bytes into a new Packet object.
      The incoming bytes are in the form described in the documentation for Packet.byte_string

      Parameters:
      ------------
      s: socket object
        Socket object

      Returns:
      ---------
      Packet object ~ if successful

      False         ~ if socket.error occured
      '''
      addr = ('0.0.0.0', 4242)
      try:
        try:
          msg, addr = socketUDP.recvfrom(MSG_SIZE)
          # print(f"m={m} -=- addr={addr}")
        except:
          return False

        if len(msg) == 0:
          # The socket is broken
          return False

        # Process the message
        sender_id, x, y, z, theta = struct.unpack_from('=H4f', msg)
        # print('Pos ({},{},{}) angle {} of ID: {}'.format(x,y,z,theta,sender_id) )
        tot = struct.calcsize('=H4f')
        msgs = []
        while (tot < MSG_SIZE):
          try:
            msg_size = struct.unpack_from('H', msg, tot)[0]
            tot += 2
          except struct.error as e:
            print(e)
            return False
          if msg_size == 0:
            break
          msgs.append(msg[tot:tot+msg_size])

          tot += msg_size
          # print('rcv msg from {} size {} tot {}'.format(sender_id, msg_size, tot))
        return Packet(x, y, z, sender_id, msgs, received_time=time.time(), addr=addr)
      except:
        return False

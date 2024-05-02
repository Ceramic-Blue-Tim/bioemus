# Consumer ##########################

import zmq

IP_ADDR = "tcp://10.42.0.44:6667"

context = zmq.Context()
zmq_socket = context.socket(zmq.PULL)
zmq_socket.connect(IP_ADDR)
zmq_socket.recv()

# Producer ##########################
import zmq
import numpy as np
import time

NB_TEST = 10
IP_ADDR = "tcp://127.0.0.1:6666"

context = zmq.Context()
zmq_socket = context.socket(zmq.PUSH)
zmq_socket.bind(IP_ADDR)

tx = []
for _ in range (NB_TEST):
    zmq_socket.send(np.zeros(1024, dtype=np.uint32).tobytes())

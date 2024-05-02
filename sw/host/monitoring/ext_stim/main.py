import time
import zmq
import numpy as np


NB_NRN = 1024
IP_ADDR = "tcp://*:5559"
stim = np.zeros(NB_NRN, dtype=np.uint32)
# stim[   0] = 1000
# stim[ 1023] = 2000
# stim[1023] = 2000
stim[0 : 1024] = 500

def main():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind(IP_ADDR)
    print("Start producer")

    for i in range(10):
        zmq_socket.send(stim.tobytes())
        time.sleep(1)

main()
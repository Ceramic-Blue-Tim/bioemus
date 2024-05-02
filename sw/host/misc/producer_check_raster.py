import time
import zmq
from math import ceil

IP_ADDR             = "tcp://127.0.0.1:5557"
NB_NRN              = 512

NB_REGS_SPK         = 16
NB_TAB_PER_FRAME    = 512
NB_BYTES_PER_REGS   = 4
BYTE_SIZE_FRAME     = (NB_REGS_SPK+1)*NB_BYTES_PER_REGS

def producer():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind(IP_ADDR)
    
    msg = bytes()
    for i in range(NB_TAB_PER_FRAME):
        tstamp  = i
        msg     += tstamp.to_bytes(4, "little")

        for r in range(NB_REGS_SPK):
            if r == int(i/32):
                msg += int(1<<(i%32)).to_bytes(4, "little")
            else:
                msg += int(0).to_bytes(4, "little")

    zmq_socket.send(msg)

producer()
import socket
import threading
import logging
import time
import getopt, sys

PORT = 4000 # Default server port

# Logging config
logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO, datefmt='%H:%M:%S')

# Tratamento dos argumentos da linha de comando
raw_args = sys.argv[1:]
unixOptions = "hp:"

try:
    args, values = getopt.getopt(raw_args, unixOptions)
except getopt.error as err:
    print(str(err))
    sys.exit(2)

SERVER = values[0]

for (current_arg, current_value) in args:
    if current_arg == '-p':
        PORT = int(current_value)

# TCP Socket  
try: 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
        tcp.connect((SERVER, PORT))
        logging.info('Connected to %s:%d', SERVER, PORT)
        data = bytes(65000)
        while True:
            tcp.send(data)
except KeyboardInterrupt:
    print('Client stopped')

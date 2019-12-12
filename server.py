import socket
import threading
import logging
import time
import getopt
import sys
import csv
import pandas as pd
import plotly.express as px

PORT = 4000 # Default server port
data_per_sec = 0
log_alive = 1

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

for (current_arg, current_value) in args:
    if current_arg == '-p':
        PORT = int(current_value)



# Logging thread
def thread_log():
    global data_per_sec, log_alive
    time_count = 0
    with open('server_log.csv', mode='w') as log_file:
        log_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        log_writer.writerow(['Time (sec)', 'TCP Traffic (Mbit/s)'])
        while log_alive:
            time.sleep(1)
            if data_per_sec:
                logging.info('%d bytes recebidos (%f Mb/s)', data_per_sec, data_per_sec*8/1000000)
            log_writer.writerow([time_count, data_per_sec*8/1000000])
            data_per_sec = 0
            time_count += 1
    df = pd.read_csv('server_log.csv')
    fig = px.line(df, x = 'Time (sec)', y = 'TCP Traffic (Mbit/s)')
    fig.show()

log = threading.Thread(target=thread_log)

# TCP Socket 
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
        tcp.bind(('', PORT))
        tcp.listen()
        logging.info('Server listening at port %d', PORT)
        log.start()
        while True:
            conn, addr = tcp.accept()
            with conn:
                logging.info('Client %s:%d connected', addr[0], addr[1])
                while True:
                    data = conn.recv(4096)
                    if not data: break
                    data_per_sec += sys.getsizeof(data)
                logging.info('Client %s:%d disconnected', addr[0], addr[1])
except KeyboardInterrupt:
    log_alive = 0
    print('Server stopped')
                    
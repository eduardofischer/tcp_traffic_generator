import socket
import threading
import logging
import time, datetime
import getopt
import sys, os
import csv
import pandas as pd
import plotly
import plotly.graph_objs as go

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
    i = 0
    data = []

    while os.path.exists("server_log%s.csv" % i):
        i += 1

    with open('server_log%s.csv' % i, 'w') as log_file:
        log_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        log_writer.writerow(['Time', 'TCP Traffic (Mbit/s)'])
        while log_alive:
            time.sleep(1)
            if data_per_sec:
                logging.info('%d bytes recebidos (%.2f Mb/s)', data_per_sec, data_per_sec*8/1000000)
            log_writer.writerow([datetime.datetime.now().isoformat(), data_per_sec*8/1000000])
            data_per_sec = 0
    for x in range(i+1):
        df = pd.read_csv('server_log%s.csv' % x)
        trace = go.Scatter(
            x = df['Time'].tolist(),
            y = df['TCP Traffic (Mbit/s)'].tolist(),
            mode = 'lines',
            name = 'Server %d' % x
        )
        data.append(trace)
        # fig = px.line(df, x = 'Time', y = 'TCP Traffic (Mbit/s)')
    fig = go.Figure(data=data)
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
                    
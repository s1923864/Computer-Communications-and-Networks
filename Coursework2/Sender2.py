import time
import numpy as np
import socket
import os
import sys


port = int(sys.argv[2])
host = sys.argv[1]
retry_timeout = int(sys.argv[4])
file_name =  sys.argv[3]
number_of_retransmission = 0


data_reader = open(file_name, 'rb')
send_data = data_reader.read()
send_data_length = len(send_data)
send_times = int(np.ceil(send_data_length / 1024))

Sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def make_packet(data, i, send_times):
    EOF = 0 if i < send_times - 1 else 1
    header = i.to_bytes(2,"big",signed=False)
    packet = header + bytes([EOF]) + data[i * 1024: (i+1) * 1024]
    return packet

start_time = time.time()
retry_packet = []


for i in range(send_times):

    packet = make_packet(send_data, i, send_times)
    Sender_socket.sendto(packet, (host, port))

    
    Ack_match = False
    is_ack_received = False
    Ack_number = -1
    timeout_times = 0
    while not Ack_match:
        try:
            Sender_socket.settimeout(retry_timeout / 1000)
            receive_data, address = Sender_socket.recvfrom(2)
            Ack_number = int.from_bytes(receive_data, "big", signed=False)
            is_ack_received = True
       
        except socket.timeout:
            is_ack_received = False
            timeout_times += 1
        if i == Ack_number and is_ack_received:
            Ack_match = True
        else:
            Sender_socket.sendto(packet, (host, port))
            number_of_retransmission += 1
            retry_packet.append(i)
        if(timeout_times == 50):
            break

end_time = time.time()

size = os.path.getsize(file_name)

print(number_of_retransmission, round((size / (1024 * (end_time - start_time))), 2))

Sender_socket.close()





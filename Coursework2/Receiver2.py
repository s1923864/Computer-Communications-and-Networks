import os
import sys
import time
import numpy as np
import socket


port = int(sys.argv[1])
ip = "127.0.0.1"
file_name = sys.argv[2] 

Receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

Receiver_socket.bind((ip, port))

Received_data_file = bytearray()

pre_num = 0


while True:
    receive_data_i, addr = Receiver_socket.recvfrom(1027)

    if receive_data_i[:2] == pre_num.to_bytes(2,"big",signed=False) :
        Received_data_file.extend(receive_data_i[3:])
      
        pre_num += 1
    back_flag = receive_data_i[:2]
    Receiver_socket.sendto(receive_data_i[:2], addr)
   
    if receive_data_i[2] == 1:
        break

with open(file_name, 'wb') as data_writer:
    data_writer.write(Received_data_file)
Receiver_socket.close()


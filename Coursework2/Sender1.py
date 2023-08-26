
import numpy as np
import sys
import os
import socket



port = int(sys.argv[2])
file_name = sys.argv[3]
ip = "127.0.0.1"
Sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


Reader = open(file_name, 'rb')


Data_size = len(Reader.read())
Number_of_Sending = np.ceil(Data_size / 1024).astype(int)
Reader.close()
Reader = open(file_name, 'rb')

for n in range(Number_of_Sending):
    if n < Number_of_Sending - 1:
        header = (n << 8).to_bytes(3, 'big', signed=False)
    else:
        header = ((n << 8) + 1).to_bytes(3 ,'big', signed=False)

    Data_to_send = header + Reader.read(1024)
    Sender_socket.sendto(Data_to_send, (ip, port))
    received_data, address = Sender_socket.recvfrom(1024)



Reader.close()
Sender_socket.close()
os._exit(0)
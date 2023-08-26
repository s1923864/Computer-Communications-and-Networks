import sys 
import socket
import os



port = int(sys.argv[1])
ip = "127.0.0.1"
file_name = sys.argv[2] 
data_file = bytearray()
Receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

Receiver_socket.bind((ip, port)) 


EOF = 0
while EOF==0 :
    
    data, address = Receiver_socket.recvfrom(1027)
 
    EOF = data[2]
    data_file += data[3:] 
    Seq_number = data[:2]
       
    Receiver_socket.sendto(Seq_number, address)
    
  
Receiver_socket.close()
  
with open(file_name, 'wb') as Write_buffer:
    Write_buffer.write(data_file)

Write_buffer.close()
os._exit(0)
import sys 
import socket
import os





sequence_number = 0

next_sequence_number = 0

file_name = sys.argv[2] 

ip = "127.0.0.1"

port = int(sys.argv[1])

Receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

Receiver_socket.bind((ip, port))

data_file = bytearray()


while True:
 
    received_data, address = Receiver_socket.recvfrom(1027) 
 
    sequence_number = int.from_bytes(received_data[:2],'big',signed=False)

    if sequence_number == next_sequence_number:

        next_sequence_number += 1
        data_file.extend(received_data[3:])
        

    pre_seq_num = 0 if next_sequence_number == 0 else next_sequence_number - 1


    packet = bytearray(pre_seq_num.to_bytes(2, 'big',signed=False))

 
    Receiver_socket.sendto(packet, address)


    while sequence_number + 1 != next_sequence_number :
       
        received_data, address = Receiver_socket.recvfrom(1027) 
     
        sequence_number = int.from_bytes(received_data[:2],'big',signed=False)
      
        if sequence_number == next_sequence_number:
            data_file.extend(received_data[3:])
            next_sequence_number = next_sequence_number + 1

        
        pre_seq_num = 0 if next_sequence_number == 0 else next_sequence_number - 1
    
        packet = bytearray(pre_seq_num.to_bytes(2, 'big',signed=False))
   
        Receiver_socket.sendto(packet, address)
  

    if(received_data[2] == 1):
      
        packet = bytearray(sequence_number.to_bytes(2, 'big',signed=False))
        Receiver_socket.sendto(packet, address)
        break



with open(file_name, 'wb') as Write_buffer:
    Write_buffer.write(data_file)


Write_buffer.close()

Receiver_socket.close()

os._exit(0)
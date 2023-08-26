import socket
import math
import sys







Receiver_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

file_name = sys.argv[2]

window_size= int(sys.argv[3])

lastack = -1

port = int(sys.argv[1])

ip = '127.0.0.1'

data_file = bytearray()

Receiver_socket.bind((ip,port))

expacted_ack = 0

window_buffer = [-1] * window_size 

received_data = []





while True:

    message, address = Receiver_socket.recvfrom(1027)

    received_ack = message[0]*256 + message[1]

    received_packet = message[3:]

    EOF = message[2]
     

    if EOF == 1: 

        lastack = received_ack


    if received_ack == expacted_ack: 

        if window_size == 1:

            Receiver_socket.sendto(received_ack.to_bytes(2, 'big',signed=False), address)

            expacted_ack+=1

            received_data.append(received_packet)
            
            if lastack != -1 and expacted_ack > lastack :
                
                for j in range(15):

                    Receiver_socket.sendto(received_ack.to_bytes(2, 'big',signed=False), address)

                break

            continue
        

        Receiver_socket.sendto(received_ack.to_bytes(2,'big',signed=False), address)

        try:

            window_buffer_index = window_buffer[1:].index(-1)

        except ValueError:

            window_buffer_index = window_size-1


        received_data.append(received_packet)

        received_data += window_buffer[1:window_buffer_index+1] 
        
        new_window_buffer = window_buffer[window_buffer_index+1:]

        new_window_buffer += ([-1] * (window_size-len(new_window_buffer)))

        expacted_ack =  window_buffer_index + received_ack + 1

        window_buffer = new_window_buffer
         
        if lastack != -1 and expacted_ack > lastack :
            
            for j in range(lastack-window_size,expacted_ack):

                for k in range(15):

                    Receiver_socket.sendto(j.to_bytes(2, 'big',signed=False), address)

            break

        continue


    else :
        
        Receiver_socket.sendto(received_ack.to_bytes(2, 'big',signed=False), address)
        
        if received_ack > expacted_ack: 

            window_buffer[received_ack - expacted_ack] = received_packet

        continue


Receiver_socket.close()


with open(file_name, 'wb') as Write_buffer:

    for h in received_data:

        data_file.extend(h)


    Write_buffer.write(data_file)



Write_buffer.close()



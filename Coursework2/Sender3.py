import select
import socket
import os
import sys
import math
import time






def receiving_ack(base):

    ack_num = base
 
    sender_socket.settimeout(time_out/1000)

    data, address = sender_socket.recvfrom(2)

    ack_num = int.from_bytes(data[:2], 'big', signed=False)

    if base < ack_num:
        return ack_num
   
    else:
        return receiving_ack(base)






def sending_packet(size_of_final_packet, seq_num, final_seq_num):

    EOF = 1 if final_seq_num == seq_num else 0
    
    size = 1024 if EOF == 0 else size_of_final_packet

    packet = bytearray(seq_num.to_bytes(2, byteorder='big', signed=False))

    packet.append(EOF)

    start_index = seq_num*1024

    end_index = start_index + size

    packet.extend(data_to_transmit[start_index:end_index])


    try: 

        sender_socket.sendto(packet, (ip, port))

    except socket.error:
        select.select([],[sender_socket],[])







ip = sys.argv[1]

port = int(sys.argv[2])

file_name = sys.argv[3]

time_out = int(sys.argv[4])

window_size = int(sys.argv[5])

sender_socket = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)

sender_socket.setblocking(False)


with open(file_name, 'rb') as Read_buffer:
    content = Read_buffer.read()
    data_to_transmit = bytearray(content)


Read_buffer.close()



final_sequence_number = math.ceil(float(len(data_to_transmit))/float(1024))

final_packet_size = len(data_to_transmit) - (final_sequence_number * 1024)

start_time = time.time()

EOF = 0

retransmissions = 0

send_base = 0

final_packet = len(data_to_transmit) % 1024

sequence_number = 0

file_to_send = False




try:

    send_base = -1

    sequence_number = 0

    while file_to_send==False :
        while(sequence_number <= final_sequence_number and sequence_number - send_base <= window_size) :  
            sending_packet(final_packet_size, sequence_number, final_sequence_number)
            sequence_number = sequence_number + 1
			
   
        try:
            send_base = receiving_ack(send_base)

        except socket.error as identified_error:
            retransmissions+=1
            sequence_number = send_base + 1			
            if final_sequence_number == send_base:
                file_to_send = True


except socket.error as identified_error:
    print("there is error for the socket!!!!!")



end_time = time.time()

transmit_time = end_time - start_time

transmission_rate = (len(data_to_transmit) / 1024)/transmit_time

print(round(transmission_rate, 2))

sender_socket.close()

os._exit(0)

import sys
import socket
from threading import Thread,Lock
import time
import os



class time_checker(object):

    def  __init__(self,timeout):

        self.timeout = timeout

        self.start_state = False

        self.stop_state = True

        self.running_state = False

        self.begining_time = 0


    def start_timer(self):

        self.start_state = True

        self.stop_state = False

        self.running_state = True

        if self.begining_time == 0:

            self.begining_time = time.time()


    def is_timer_running(self):

        self.start_state = True

        self.stop_state = False

        self.running_state = True 

        return self.running_state


    def stop_timer(self):

        self.start_state = False

        self.stop_state = True

        self.running_state = False

        self.begining_time = 0


    def is_time_out(self):

        return False if not self.is_timer_running() else (time.time() - self.begining_time) > (self.timeout/1000)
 


def receiving_ack(Socket):

    global next_seq_num

    global good_lock

    global All_acks

    global Send_base

    while True:

        pre_ack = True

        for i in All_acks :

            pre_ack = pre_ack and i

        if pre_ack :

            break

        data,address = Socket.recvfrom(1024)

        packet_num = int.from_bytes(data,'big',signed=False)

        good_lock.acquire()

        All_acks[packet_num] = True 

        good_lock.release()



def make_all_packets(FileName):
    
    transmitted_file = []

    k = 0

    with open(FileName,'rb') as packet_reader:

        transmitted_packet = packet_reader.read(1024)

        while transmitted_packet:

            data = k.to_bytes(2,'big',signed=False) + b'\x00' + transmitted_packet

            transmitted_file.append(data)

            transmitted_packet = packet_reader.read(1024)

            k+=1


    last_packet = list(transmitted_file[len(transmitted_file)-1])

    last_packet[2] = 1

    transmitted_file[len(transmitted_file)-1] = bytes(last_packet)

    packet_reader.close()

    return transmitted_file



def send_information(host ,port, Socket,Packets,window_size,timeout):

    global next_seq_num

    global good_lock

    global All_acks 

    global Send_base

    window = window_size

    All_acks = [False]*len(Packets) 
 
    receiving_ack_thread = Thread(target=receiving_ack,args=(Socket,))

    receiving_ack_thread.start()

    while True:

        good_lock.acquire()

        if Send_base >= len(Packets):

            good_lock.release()

            break


        while next_seq_num < Send_base + window:

            sending_packet_thread = Thread(target=send_all_packets,args=(host ,port, Socket,Packets[next_seq_num],next_seq_num,timeout))

            sending_packet_thread.start()

            next_seq_num += 1


        while not All_acks[Send_base]:

            good_lock.release()

            time.sleep(0.000008)

            good_lock.acquire()

       
        Send_base += 1

        window = len(Packets) -Send_base if len(Packets) -Send_base < window_size else window_size

        good_lock.release()



def send_all_packets( host,port,Socket,Packet,seq_num,timeout):

    global good_lock

    global All_acks

    timer = time_checker(timeout)

    Not_Exit = True

    while Not_Exit:

        Not_Exit = send_each_packet(host,port,timer,Socket,Packet,seq_num,timeout)



def send_each_packet(host,port,timer,Socket,Packet,seq_num,timeout) :
    
    global good_lock

    global All_acks

    if  timer.is_time_out() or not timer.is_timer_running(): 

        timer.stop_timer()   

        Socket.sendto(Packet, (host, port))

        timer.start_timer()

        return True


    elif not All_acks[seq_num]: 

        good_lock.acquire()

        good_lock.release()

        time.sleep(0.0008)

        return True


    else: 

        good_lock.acquire()

        good_lock.release()

        return False



window_size = int(sys.argv[5])

Sender_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

next_seq_num = 0

Send_base = 0

good_lock = Lock()

file_name = sys.argv[3]

AllPackets = make_all_packets(file_name)

port = int(sys.argv[2])

timeout = int(sys.argv[4])

host = sys.argv[1]

begin_time = time.time()

send_information(host,port,Sender_socket,AllPackets,window_size,timeout)

end_time = time.time()

size = os.path.getsize(sys.argv[3])

print(round((size / (1024 * (end_time - begin_time))), 2))

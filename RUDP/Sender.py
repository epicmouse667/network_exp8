import sys
import getopt
import math
import time
import base64

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=True, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.packets=[] # store the packets 
        self.win_offset=0 # N is offset ,buffer window:[N,N+4]
        self.win_len=5 # length of buffer window
        self.seqno=0 # the next number of package you want to send
        self.timeout=0.5 # timeout for connection
        self.data_max_len=1024 # max length of data part in the message
        self.sackMode=sackMode
    # Main sending loop.
    # def make_packet(self,msg_type,seqno,msg):
    #     body = "{}|{}|".format(msg_type,seqno).encode() + msg + "|".encode()
    #     checksum = Checksum.generate_checksum(body).encode()
    #     packet = body + checksum
    #     # print(packet)
    #     return packet
    def start(self):
        # divide the input files into partitions
        content = self.infile.read()
        if self.debug:
            print(f"type of content is {type(content)}")
        content_len=len(content)
        self.infile.close()
        packet_num=math.ceil(content_len/self.data_max_len)
        self.packet_num=packet_num+1
        self.sacks=[0 for i in range(self.packet_num)]
        packets=[]
        for i in range(self.packet_num):
            if i == self.packet_num-1:
                packet=self.make_packet("end",i, "")
            elif i == 0:
                packet=self.make_packet("start",i, content[i*self.data_max_len:(i+1)*self.data_max_len])
            else:
                packet=self.make_packet("data",i, content[i*self.data_max_len:(i+1)*self.data_max_len])
            packets.append(packet.encode())
        self.packets=packets
        if self.debug:
            print(f"packet_num={len(packets)}")
        self.stopwatch=[None for i in range(self.packet_num)]
        if self.sackMode: #selectively resend
             while True:
                while self.seqno<self.win_offset+self.win_len and self.seqno<self.packet_num:
                    if self.sacks[self.seqno]==0 :
                        self.stopwatch[self.seqno]=time.time()
                        self.send(self.packets[self.seqno])
                        if self.debug:
                            print(f"sacks = {self.sacks}")
                    self.seqno+=1
                for i in range(self.win_offset,self.seqno):
                    if time.time()-self.stopwatch[i]>self.timeout:
                        self.handle_timeout(i)
                        break
                response=self.receive(self.timeout)
                if response == None:
                    continue
                response=response.decode()
                if not Checksum.validate_checksum(response):
                    continue
                msg_type,ack,ack_data,checksum = self.split_packet(response)
                ack=ack.split(";")
                cum_ack=ack[0]
                self.sacks[int(cum_ack)-1]=0
                if len(ack[1])>0:
                    sack_num=[int(i) for i in ack[1].split(",")]
                    for i in sack_num:
                        if self.sacks[i] == 0:
                            self.sacks[i]=1
                if self.debug:
                    print(f"received {msg_type}|{cum_ack}|{ack_data}|{checksum}")
                if int(cum_ack)== self.packet_num:
                    break                
                self.handle_new_ack(int(cum_ack))
                   
        else :# gbn
            while True:
                while self.seqno<self.win_offset+self.win_len and self.seqno<self.packet_num:
                    self.stopwatch[self.seqno]=time.time()
                    self.send(self.packets[self.seqno])
                    self.seqno+=1
                for i in range(self.win_offset,self.seqno):
                    if time.time()-self.stopwatch[i]>self.timeout:
                        self.handle_timeout(i)
                        break
                response=self.receive(self.timeout)
                if response == None:
                    continue
                response=response.decode()
                if not Checksum.validate_checksum(response):
                    continue
                msg_type,ack,ack_data,checksum = self.split_packet(response)
                if self.debug:
                    print(f"received {msg_type}|{ack}|{ack_data}|{checksum}")
                ack = int(ack)
                if ack == self.packet_num:
                    break
                self.handle_new_ack(ack)

                
    def handle_timeout(self,seqno):
        if self.debug:
            print(f"seqno={seqno} timeout")
        self.seqno=seqno
    def handle_new_ack(self, ack):
        if self.debug:
            print(f"Sender.py: received ack={ack} when window offset ={self.win_offset}")
        self.win_offset = ack
        if self.debug:                                                                          
            print(f"now window offset is={self.win_offset}")

    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print (msg)


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print ("RUDP Receiver")
        print ("-p PORT | --port=PORT The listen port, defaults to 33122")
        print ("-t TIMEOUT | --timeout=TIMEOUT Receiver timeout in seconds")
        print ("-d | --debug Print debug messages")
        print ("-h | --help Print this usage message")
        print ("-k | --sack Enable selective acknowledgement mode")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()

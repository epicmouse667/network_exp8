import random

from tests.BasicTest import BasicTest

class SackRandomOrderTest(BasicTest):
    def __init__(self, forwarder, input_file):
        super(SackRandomOrderTest, self).__init__(forwarder, input_file, sackMode = True)

    def handle_packet(self):
        random.shuffle(self.forwarder.in_queue)#shuffle the in_queue packages in random order
        self.forwarder.out_queue = self.forwarder.in_queue
        self.forwarder.in_queue = []
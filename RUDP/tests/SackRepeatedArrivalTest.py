import random

from tests.BasicTest import BasicTest

class SackRepeatedArrivalTest(BasicTest):
    def __init__(self, forwarder, input_file):
        super(SackRepeatedArrivalTest, self).__init__(forwarder, input_file, sackMode = True)

    def handle_packet(self):
        for p in self.forwarder.in_queue:
            self.forwarder.out_queue.append(p)
            if random.choice([True, False]):
                self.forwarder.out_queue.append(p)# randomly repeat some packets
        self.forwarder.in_queue = []
import random

from tests.BasicTest import BasicTest

class RepeatedArrivalTest(BasicTest):
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            self.forwarder.out_queue.append(p)
            if random.choice([True, False]):
                self.forwarder.out_queue.append(p)# randomly repeat some packets
        self.forwarder.in_queue = []
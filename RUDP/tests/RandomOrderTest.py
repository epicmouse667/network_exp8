import random

from tests.BasicTest import BasicTest
class RandomOrderTest(BasicTest):
    def handle_packet(self):
        random.shuffle(self.forwarder.in_queue)#shuffle the in_queue packages in random order
        self.forwarder.out_queue = self.forwarder.in_queue
        self.forwarder.in_queue = []
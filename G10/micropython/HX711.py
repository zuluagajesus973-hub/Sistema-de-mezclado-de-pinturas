import time
from machine import Pin

class HX711:
    def __init__(self, dout_pin, pd_sck_pin):
        self.pd_sck = Pin(pd_sck_pin, Pin.OUT)
        self.dout = Pin(dout_pin, Pin.IN, pull=None)
        self.OFFSET = 0
        self.SCALE = 1

    def is_ready(self):
        return self.dout.value() == 0

    def read(self):
        while not self.is_ready():
            pass
        count = 0
        for i in range(24):
            self.pd_sck.value(1)
            count = count << 1
            self.pd_sck.value(0)
            if self.dout.value():
                count += 1
        self.pd_sck.value(1)
        count ^= 0x800000
        self.pd_sck.value(0)
        return count

    def read_average(self, times=10):
        sum = 0
        for _ in range(times):
            sum += self.read()
        return sum / times

    def get_data_mean(self, times=10):
        return self.read_average(times)

    def tare(self, times=15):
        sum = self.read_average(times)
        self.OFFSET = sum
        print("Tara establecida:", self.OFFSET)

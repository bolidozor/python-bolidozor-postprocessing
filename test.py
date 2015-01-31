#!/usr/bin/python

import timeit
import urllib2
import time

import bzpost


BASE_URL = "http://space.astro.cz/bolidozor/svakov/SVAKOV-R6/"


class Stopwatch(object):
    def start(self):
        self.iterations = 0
        self.start_time = time.time()
    
    def iteration(self):
        self.iterations += 1
        self.stop_time = time.time()
    
    def dump(self, out = None):
        total_time = self.stop_time - self.start_time
        iter_time = float(total_time) / float(self.iterations)
        print total_time, self.iterations, iter_time
    

s = Stopwatch()
s.start()
for i in range(500):
    f = urllib2.urlopen(BASE_URL)
    f.read()
    s.iteration()
s.dump()


c = bzpost.HTTPConnector(BASE_URL)
c.connect()
try:
    s.start()
    for i in range(500):
        c.request(BASE_URL)
        s.iteration()
    s.dump()
finally:
    c.close()


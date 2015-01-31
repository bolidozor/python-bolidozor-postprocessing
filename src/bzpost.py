#!/usr/bin/python
# -*- coding: utf-8 -*-
"""bzpost module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import urlparse
import httplib


__version__ = "0.1"


class HTTPConnector(object):
    def __init__(self, base_url, station_name = "<none>"):
        self.base_url = base_url
        self.station_name = station_name
        
        self.parsed_url = urlparse.urlparse(base_url)
        
        self.connection = None
    
    def connect(self):
        self.connection = httplib.HTTPConnection(self.parsed_url.netloc)

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def request(self, url, method = "GET"):
        self.connection.request(method, url, headers = {
            "Connection": "Keep-Alive",
        })
        response = self.connection.getresponse()
        return response.read()
    
    def get_snapshots(self, from_date, to_date = None):
        pass


def main():
    print __doc__


if __name__ == "__main__":
    main()


#!/usr/bin/python
# -*- coding: utf-8 -*-
"""bzpost module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import urlparse
import httplib
import datetime
import re


__version__ = "0.1"


def normalize_time(value, including = False):
    if isinstance(value, int):
        return datetime.fromtimestamp(value)
    elif isinstance(value, datetime.date):
        if including:
            return datetime.datetime(value.year, value.month, value.day, 24, 0, 0)
        else:
            return datetime.datetime(value.year, value.month, value.day, 0, 0, 0)
    return value


class HTTPConnector(object):
    YEAR_RE = re.compile(r"href\s*=\s*\"\s*(([0-9]+)\s*(\/)?)\s*\"")
    
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
    
    def _get_years(self, type = "snapshots"):
        url = urlparse.urljoin(self.base_url, type)
        if not url.endswith("/"):
            url += "/"
        response = self.request(url)
        
        print url
        print response
        
        for match in self.YEAR_RE.finditer(response):
            yield (
                urlparse.urljoin(url, match.group(1)),
                int(match.group(2)),
            )
    
    def get_snapshots(self, from_date, to_date = None):
        pass


class SnapshotEntry(object):
    def __init__(self, connector, file_name, url):
        self.connector = connector
        self.file_name = file_name
        self.url = url


def main():
    print __doc__


if __name__ == "__main__":
    main()


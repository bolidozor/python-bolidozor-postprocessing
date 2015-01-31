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


def normalize_date(value):
    if isinstance(value, int):
        return datetime.datetime.fromtimestamp(value).date()
    elif isinstance(value, datetime.datetime):
        return value.date()
    elif isinstance(value, datetime.date):
        return value
    raise TypeError("%r is of unexpected type." % (value, ))


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
        if response.status == 404:
            raise Exception()
        return response.read()
    
    def _get_directory(self, url, pattern, url_group = 1, value_group = 2, value_fn = None):
        response = self.request(url)
        
        if value_fn is None:
            #value_fn = lambda v: v
            value_fn = int
        
        count = 0
        
        for match in pattern.finditer(response):
            count += 1
            yield (
                urlparse.urljoin(url, match.group(url_group)),
                value_fn(match.group(value_group)),
            )

        if count == 0:
            print url
            print response
    
    def _get_years(self, type = "snapshots"):
        url = urlparse.urljoin(self.base_url, type)
        if not url.endswith("/"):
            url += "/"

        return self._get_directory(url, self.YEAR_RE)
    
    def _get_months(self, year, type = "snapshots"):
        url = urlparse.urljoin(
            self.base_url,
            "%s/%4d/" % (type, year, )
        )
        
        return self._get_directory(
            url,
            self.YEAR_RE,
            value_fn = lambda v: datetime.date(year, int(v), 1),
        )
    
    def _get_days(self, month, type = "snapshots"):
        month = normalize_date(month)
        
        url = urlparse.urljoin(
            self.base_url,
            "%s/%04d/%02d/" % (type, month.year, month.month, )
        )
        
        return self._get_directory(
            url,
            self.YEAR_RE,
            value_fn = lambda v: datetime.date(month.year, month.month, int(v)),
        )
    
    def _get_hours(self, day, type = "snapshots"):
        day = normalize_date(day)
        
        url = urlparse.urljoin(
            self.base_url,
            "%s/%04d/%02d/%02d/" % (type, day.year, day.month, day.day, )
        )
        
        return self._get_directory(
            url,
            self.YEAR_RE,
            value_fn = lambda v: datetime.datetime(day.year, day.month, day.day, int(v)),
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


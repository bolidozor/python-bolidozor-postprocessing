#!/usr/bin/python
# -*- coding: utf-8 -*-
"""bzpost module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import urlparse
import httplib
import datetime
from datetime import datetime as dt
import re


__version__ = "0.1"


def normalize_time(value, including = False):
    if isinstance(value, int):
        return datetime.fromtimestamp(value)
    elif isinstance(value, datetime.datetime):
        return value
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


def normalize_year(value):
    if isinstance(value, datetime.date):
        return value.year
    else:
        return int(value)


def normalize_month(value):
    value = normalize_date(value)
    return datetime.date(value.year, value.month, 1)


def normalize_day(value):
    return normalize_date(value)


class ConnectorException(Exception):
    pass


class HTTPConnector(object):
    YEAR_RE = re.compile(r"href\s*=\s*\"\s*(([0-9]+)\s*(\/)?)\s*\"")

    SNAPSHOT_RE = re.compile(
        r"href\s*=\s*\"\s*((\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{3})_(.*?)_snap\.fits)\s*(\/)?\s*\""
    )
    
    def __init__(self, base_url, station_name = "<none>"):
        self.base_url = base_url
        self.station_name = station_name
        
        self.parsed_url = urlparse.urlparse(base_url)
        
        self.connection = None
        
        self.existing_days = set()
        self.existing_months = set()
        self.existing_years = set()
        
        #self.missing_hours = set()
        self.missing_days = set()
        self.missing_months = set()
        self.missing_years = set()
    
    def connect(self):
        self.connection = httplib.HTTPConnection(self.parsed_url.netloc)

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def request(self, url, method = "GET", throw = True):
        self.connection.request(method, url, headers = {
            "Connection": "Keep-Alive",
        })
        response = self.connection.getresponse()
        content = response.read()

        #print url, response.status
        
        if throw:
            if response.status != 200:
                raise ConnectorException("Response status: %d" % (response.status, ))
            return content
        
        return response.status, content
    
    def _is_day_missing(self, day, type):
        day = normalize_date(day)
        
        if (day.year, type) in self.missing_years:
            return True

        if (normalize_month(day), type) in self.missing_months:
            return True
        
        return (day, type) in self.missing_days
    
    def _is_hour_missing(self, hour, type):
        if self._is_day_missing(hour):
            return True
        return False
    
    def _add_missing_day(self, day, type):
        day = normalize_day(day)
        self.missing_days.add((day, type))

    def _add_missing_month(self, month, type):
        month = normalize_month(month)
        self.missing_months.add((month, type)) 

    def _add_missing_year(self, year, type):
        year = normalize_year(year)
        self.missing_years.add((year, type))
    
    def _add_existing_day(self, day, type):
        day = normalize_day(day)
        self.existing_days.add((day, type))

    def _add_existing_month(self, month, type):
        month = normalize_month(month)
        self.existing_months.add((month, type)) 

    def _add_existing_year(self, year, type):
        year = normalize_year(year)
        self.existing_years.add((year, type))
    
    def _get_year_url(self, year, type = "snapshots"):
        return urlparse.urljoin(
            self.base_url,
            "%s/%4d/" % (type, year)
        )
    
    def _get_month_url(self, month, type = "snapshots"):
        return urlparse.urljoin(
            self._get_year_url(month.year, type),
            "%02d/" % (month.month, )
        )

    def _get_day_url(self, day, type = "snapshots"):
        return urlparse.urljoin(
            self._get_month_url(day, type),
            "%02d/" % (day.day, )
        )

    def _get_hour_url(self, hour, type = "snapshots"):
        return urlparse.urljoin(
            self._get_hour_url(hour, type),
            "%02d/" % (hour.hour, )
        )
    
    def _probe_hour(self, hour, type = "snapshots"):
        year = normalize_year(hour)
        
        if (year, type) in self.missing_years:
            return
        elif (year, type) not in self.existing_years:
            status, response = self.request(self._get_year_url(hour.year), throw = False)
            if status == 200:
                self._add_existing_year(hour.year, type)
            else:
                self._add_missing_year(hour.year, type)
                return
        
        month = normalize_month(hour)
        
        if (month, type) in self.missing_months:
            return
        elif (month, type) not in self.existing_months:
            status, response = self.request(self._get_month_url(hour), throw = False)
            if status == 200:
                self._add_existing_month(hour, type)
            else:
                self._add_missing_month(hour, type)
                return
        
        day = normalize_day(hour)
        
        if (day, type) in self.missing_days:
            return
        elif (day, type) not in self.existing_days:
            status, response = self.request(self._get_day_url(hour), throw = False)
            if status == 200:
                self._add_existing_day(hour, type)
            else:
                self._add_missing_day(hour, type)
                return
    
    def _get_directory(self, url, pattern, url_group = 1, value_group = 2, value_fn = None):
        response = self.request(url)
        
        if value_group is None:
            if value_fn is None:
                value_fn = lambda m, u: m.group(0)
        else:
            if value_fn is None:
                #value_fn = lambda v: v
                value_fn = int
        
        count = 0
        
        for match in pattern.finditer(response):
            count += 1
            match_url = urlparse.urljoin(url, match.group(url_group))
            if value_group is None:
                yield (
                    match_url,
                    value_fn(match, match_url),
                )
            else:
                yield (
                    match_url,
                    value_fn(match.group(value_group)),
                )

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
        
        if self._is_day_missing(day, type):
            return
        
        url = urlparse.urljoin(
            self.base_url,
            "%s/%04d/%02d/%02d/" % (type, day.year, day.month, day.day, )
        )
        
        try:
            for hour_url, hour in self._get_directory(
                url,
                self.YEAR_RE,
                value_fn =
                    lambda v: datetime.datetime(day.year, day.month, day.day, int(v))):
                yield hour_url, hour
        except ConnectorException:
            self._add_missing_day(day, type)
            raise
    
    def _get_hour(self, time):
        time = normalize_time(time)
        return datetime.datetime(
            time.year,
            time.month,
            time.day,
            time.hour,
        )

    def _get_snapshots_in_hour(self, hour):
        hour = normalize_time(hour)
        
        if self._is_day_missing(hour, "snapshots"):
            return
        
        url = urlparse.urljoin(
            self.base_url,
            "snapshots/%04d/%02d/%02d/%02d/" % (
                hour.year,
                hour.month,
                hour.day,
                hour.hour,
            )
        )
        
        value_fn = lambda m, u: SnapshotEntry(
            self,
            m.group(1),
            datetime.datetime(
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(5)),
                int(m.group(6)),
                int(m.group(7)),
            ),
            u,
        )

        try:
            for snapshot_url, snapshot in self._get_directory(
                url,
                self.SNAPSHOT_RE,
                value_group = None,
                value_fn = value_fn):
                yield snapshot
        except ConnectorException:
            self._probe_hour(hour)
            raise
    
    def _iter_hours(self, from_time, to_time):
        from_time = self._get_hour(from_time)
        to_time = self._get_hour(to_time)
        d = datetime.timedelta(hours = 1)
        current = from_time
        
        while current <= to_time:
            yield current
            current += d
    
    def get_snapshots(self, from_date, to_date = None):
        if to_date is None:
            to_date = datetime.datetime.now()
        
        from_date = normalize_time(from_date)
        to_date   = normalize_time(to_date)
        
        if from_date >= to_date:
            raise ValueError(
                "Starting date (%s) is equal or after the final date (%s)." % (
                    from_date.isoformat(),
                    to_date.isoformat(),
                )
            )
        
        for hour in self._iter_hours(from_date, to_date):
            try:
                for snapshot in self._get_snapshots_in_hour(hour):
                    yield snapshot
            except ConnectorException:
                continue


class SnapshotEntry(object):
    def __init__(self, connector, file_name, time, url):
        self.connector = connector
        self.file_name = file_name
        self.url = url
        self.time = time

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return "SnapshotEntry(%r, %r, %r, %r)" % (
            self.connector,
            self.file_name,
            self.time,
            self.url,
        )


def main():
    print __doc__


if __name__ == "__main__":
    main()


import sqlite3
import numpy as np
import pandas as pd
import datetime
import sys

def cached_property(f):
    """returns a cached property that is calculated by function f"""
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x

    return property(get)

class TickmateDatabase(object):
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)

    @cached_property
    def tracks(self):
        return pd.read_sql("select _id as id, name " +
                "from tracks order by \"order\"",
                self.conn, index_col='id')

    @cached_property
    def ticks(self):
        _ticks = pd.read_sql("select *, _track_id as track_id " +
                "from ticks order by \"year\", \"month\", \"day\"",
                self.conn, index_col='_id')
        _ticks['date'] = pd.to_datetime(
            _ticks.year.astype(str) + "/" +
            (_ticks.month + 1).astype(str) + "/" +
            _ticks.day.astype(str), coerce=True)
        _ticks['count'] = 1
        _ticks = _ticks.groupby(('track_id', 'date'))['count'].count()
        return _ticks

    @cached_property
    def date_range(self):
        return pd.date_range(self.ticks.reset_index().iloc[0].date,
                self.ticks.reset_index().iloc[-1].date)


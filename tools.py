#!/usr/bin/env python
"""
tools.py - Phenny Tools
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""
import collections, time

def deprecated(old): 
   def new(phenny, input, old=old): 
      self = phenny
      origin = type('Origin', (object,), {
         'sender': input.sender, 
         'nick': input.nick
      })()
      match = input.match
      args = [input.bytes, input.sender, '@@']

      old(self, origin, match, args)
   new.__module__ = old.__module__
   new.__name__ = old.__name__
   return new

class TimeTrackDict(collections.MutableMapping):
    """
    A dictionary that keeps track of the freshness of it's data. If data is 
    accessed and it's old, fire a callback.
    
    The callback should take 3 parameters: The TimeTrackDict, the key, and how 
    old the key is.
    """
    _data = None
    _times = None
    _call = None
    _expiry = None
    def __init__(self, callback, expiry, values=None):
        """TimeTrackDict(callable, number, [dictvals])
        * callback is the function to call.
        * expiry is how old is "too old", in seconds
        * values is the initial values. It takes the same data as dict().
        """
        self._call = callback
        self._expiry = expiry
        self._data = {}
        self._times = {}
        if values:
            self.update(dict(values))
    
    def __getitem__(self, key):
        v = self._data[key]
        age = time.time() - self._times[key]
        if age  > self._expiry:
            self._call(self, key, age)
        return v
    
    def __setitem__(self, key, value):
        self._times[key] = time.time()
        self._data[key] = value
    
    def __delitem__(self, key):
        del self._times[key]
        del self._data[key]
    
    def __iter__(self):
        for k in self._data:
            yield k
    
    def __len__(self):
        return len(self._data)

if __name__ == '__main__': 
   print __doc__.strip()

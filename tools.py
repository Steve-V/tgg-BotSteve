#!/usr/bin/env python
"""
tools.py - Phenny Tools
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""
import collections, time, threading, warnings, sys, traceback

def deprecated(old): 
   fname = "%s.%s" % (old.__module__, old.__name__)
   warnings.warn("%s is using deprecated form." % fname, category=DeprecationWarning)
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

def startdaemon(func, *p, **kw):
    """startdeamon(callable, ...) -> threading.Thread
    Creates a thread, based on function and arguments, starts it, and returns 
    it. Note that it will be a daemon thread.
    """
    t = threading.Thread(target=func, args=p, kwargs=kw)
    t.daemon = True
    t.start()
    return t

class TimeTrackDict(collections.MutableMapping):
    """
    A dictionary that keeps track of the freshness of it's data. If data is 
    accessed and it's old, fire a callback.
    
    The callback should take 3 parameters: The TimeTrackDict, the key, and how 
    old the key is.
    
    Other notes:
     * No knowledge of threading, locking, and related issues.
     * Will only notify about an expired key once.
     * Any errors thrown by callbacks are printed and swallowed.
    """
    _data   = None # The actual data dict
    _times  = None # The time when data was last updated
    _call   = None # The callback function
    _expiry = None # How long until data is expired
    _called = None # The set of keys that we've expired and notified.
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
        self._called = set()
        if values:
            self.update(dict(values))
    
    def _expire(self, key, age):
        """
        Handles multi-call prevention and then actually calls the callback.
        """
        if key in self._called: return
        self._called.add(key)
        try:
            self._call(self, key, age)
        except KeyboardInterrupt:
            raise
        except:
            print >> sys.stderr, "Error in TimeTrackDict callback, ignoring."
            traceback.print_exc()
    
    def checktimes(self):
        """ttd.checktimes()
        Force a scan for expired items.
        """
        t = time.time()
        for key, st in self._times.iteritems():
            age = t - st
            if age > self._expiry:
                self._expire(key, age)
    
    def __getitem__(self, key):
        v = self._data[key]
        age = time.time() - self._times[key]
        if age  > self._expiry:
            self._expire(key, age)
        return v
    
    def __setitem__(self, key, value):
        self._called.discard(key)
        self._times[key] = time.time()
        self._data[key] = value
    
    def __delitem__(self, key):
        self._called.discard(key)
        del self._times[key]
        del self._data[key]
    
    def __iter__(self):
        for k in self._data:
            yield k
    
    def __len__(self):
        return len(self._data)

if __name__ == '__main__': 
   print __doc__.strip()

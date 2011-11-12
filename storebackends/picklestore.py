"""
Implements a primitive pickle-based datastore. Loads on start, saves on exit.

+ Fast
+ Simple
+ No external server
+ Flexible
+ Very fast (all kept in memory)
- Administration requires using the python shell
- Can't edit live
- Susceptible data loss when it crashes
- Errors take out the whole module
"""
import collections
import os, pickle
#XXX: For some reason, pickle is gone in __del__()
from sys import stderr

def modulestore(mname):
    """modulestore(string) -> string
    Given a name, returns the full path of the pickle file for that module's 
    store.
    """
    return os.path.join(os.path.expanduser('~/.phenny'), mname+'.store')

class DataStore(collections.MutableMapping):
    """
    The pickle-based store. Uses an actual dict for the backend.
    """
    __slots__ = '_store', '_fn'
    def __init__(self, phenny, module, default):
        self._bot = phenny
        self._mname = module.__name__
        self._fn = modulestore(self._mname)
        if os.path.exists(self._fn):
            self._store = pickle.load(open(self._fn, 'rb'))
        else:
            self._store = default
        if self._store is None:
            self._store = {}
    
    def __flush__(self):
        print >> stderr, "Saving %s to %s..." % (self._mname, self._fn)
        pickle.dump(self._store, open(self._fn, 'wb')) #FIXME: Fails on __del__
    
    def __del__(self):
        # Full of fail. Can we use atexit somehow?
        self.__flush__()
    
    def __getitem__(self, key):
        return self._store[key]
    
    def __setitem__(self, key, value):
        self._store[key] = value
    
    def __delitem__(self, key):
        del self._store[key]
    
    def __len__(self):
        return len(self._store)
    
    def __iter__(self):
        for k in self._store:
            yield k
    

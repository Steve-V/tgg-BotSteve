# -*- coding: utf-8 -*-
"""
The JSON File store keeps each key in it's own file, with the data JSON encoded.

+ Simple
+ External, live administration
+ No data loss from crashing
- Slow (every call makes at least one file system operation, plus JSON overhead)
- Lots of files
* Administratable using normal Unix tools (human readable text)
"""
import collections
import os, json, urllib

def kenc(key):
    """kenc(string) -> str
    Perorms any encoding necessary for making a key filesystem safe
    """
    return urllib.quote(unicode(key), safe=',:=+').encode('utf-8')

def kdec(fn):
    """kdec(str) -> string
    Reverses kenc()
    """
    return urllib.unquote(fn.decode('utf-8'))

class DataStore(collections.MutableMapping):
    """
    A store based on files of JSON data.
    """
    def __init__(self, phenny, module, default):
        self._bot = phenny
        self._basename = os.path.join(os.path.expanduser('~/.phenny'), module.__name__)
        
        if not os.path.isdir(self._basename):
            os.mkdir(self._basename)
            self.update(default)
    
    def _getfile(self, key):
        return os.path.join(self._basename, kenc(key))
    
    def __getitem__(self, key):
        try:
            f = open(self._getfile(key), 'r')
        except IOError: #File does not exist
            raise KeyError
        else:
            with f:
                return json.load(f)
    
    def __setitem__(self, key, value):
        with open(self._getfile(key), 'w') as f:
            json.dump(value, f, indent=4)
            f.flush()
    
    def __delitem__(self, key):
        try:
            os.remove(self._getfile(key))
        except OSError: #File does not exist
            raise KeyError
    
    def __len__(self):
        return len(os.listdir(self._basename))
    
    def __iter__(self):
        for fn in os.listdir(self._basename):
            key = kdec(fn)
            yield key


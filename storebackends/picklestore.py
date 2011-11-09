"""
Implements a primitive pickle-based datastore. Loads on start, saves on exit.
"""
import collections
import os
from pickle import load as pload, dump as pdump, HIGHEST_PROTOCOL
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
	def __init__(self, phenny, module, default):
		self._bot = phenny
		self._mname = module.__name__
		self._fn = modulestore(self._mname)
		if os.path.exists(self._fn):
			self._store = pload(open(self._fn, 'rb'))
		else:
			self._store = default
	
	def __flush__(self):
		print >> stderr, "Saving %s to %s..." % (self._mname, self._fn)
		pdump(self._store, open(self._fn, 'wb'), protocol=HIGHEST_PROTOCOL)
	
	def __del__(self):
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
		for k,v in self._store:
			yield k,v
	

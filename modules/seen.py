#!/usr/bin/env python
"""
seen.py - Phenny Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import time
from tools import deprecated
from decimal import *
import os
import pickle

def setup(self): 
  fn = self.nick + '-' + self.config.host + '.seen.db'
  self.seen_filename = os.path.join(os.path.expanduser('~/.phenny'), fn)
  if not os.path.exists(self.seen_filename):
    try: f = open(self.seen_filename, 'w')
    except OSError: pass
    else: 
      f.write('')
      f.close()
  self.seen = pickle.load( open(self.seen_filename) )

@deprecated
def f_seen(self, origin, match, args): 
  """.seen <nick> - Reports when <nick> was last seen."""
  
  #pickle datastore to file
  pickle.dump(self.seen, open(self.seen_filename,'wb') )
  
  if origin.sender == '#talis': return
  nick = match.group(2).lower()
  
  #misc easter eggs
  if nick.lower() == "kyle":
    return self.msg(origin.sender, "He's about this tall?  Seen Kyle?")
  if nick.lower() == "botsteve":
    return self.msg(origin.sender, "I'm right here, actually.")
  
  #error check
  if not hasattr(self, 'seen'): 
      return self.msg(origin.sender, 'Database Error!')
  
  if self.seen.has_key(nick): 
      channel, storedTime = self.seen[nick]
      t = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(storedTime))
      currentTime = time.strftime('%H:%M:%S UTC', time.gmtime())
      rawTimeDifference_hours = (time.time() - storedTime) / 3600
      formattedTimeDiff = Decimal(str(rawTimeDifference_hours)).quantize(Decimal('1.00'))
      
      #requires python 2.7
      #timeDifference_hr = timeDifference_sec.total_seconds() / 3600
      

      msg = "I last saw %s %s hours ago at %s on %s.  Current time: %s" % (nick, formattedTimeDiff, t, channel, currentTime)
      self.msg(origin.sender, str(origin.nick) + ': ' + msg)
  
  #no record of user
  else: self.msg(origin.sender, "Sorry, I haven't seen %s around." % nick)
f_seen.rule = (['seen', 'lastseen'], r'(\S+)')
f_seen.thread = False

@deprecated
def f_note(self, origin, match, args): 
   def note(self, origin, match, args): 
      if not hasattr(self.bot, 'seen'): 
         self.bot.seen = {}
      if origin.sender.startswith('#'): 
         # if origin.sender == '#inamidst': return
         self.seen[origin.nick.lower()] = (origin.sender, time.time())

      # if not hasattr(self, 'chanspeak'): 
      #    self.chanspeak = {}
      # if (len(args) > 2) and args[2].startswith('#'): 
      #    self.chanspeak[args[2]] = args[0]

   try: note(self, origin, match, args)
   except Exception, e: print e
f_note.rule = r'(.*)'
f_note.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()

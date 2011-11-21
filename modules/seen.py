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

storage = {} # Default value
# storage is a persistant value, automagically loaded and saved by the bot.

#def setup(self): 
#    pass

#NICKTRACKER: If passed a known registered user, check agaisnt all names they've used and print the most recent ones.

def f_seen(phenny, input): 
    """.seen <nick> - Reports when <nick> was last seen."""
    global storage
    
    if input.sender == '#talis': return
    try:
        nick = input.group(2).lower()
    except AttributeError:
        self.say("No user provided!")
        return 
    
    #misc easter eggs
    if nick.lower() == "kyle":
        return self.say("He's about this tall?  Seen Kyle?")
    if nick.lower() == phenny.nick.lower():
        return self.say("I'm right here, actually.")
    
    nicks = [nick]
    if hasattr(phenny, 'nicktracker'):
        if input.canonnick:
            nicks += [input.canonnick.lower()]
        alts, maybes = phenny.nicktracker.getalts(nick)
        nicks += [n.lower() for n in alts+maybes]
    
    print "Nicks:", nicks
    
    seennicks = {}
    for nick in nicks:
        print "Nick:", nick
        try:
            # TODO: Filter time
            data = storage[nick]
            seennicks[data[0].lower()] = data
            print "Data", data
        except KeyError:
            pass
    
    print "Seen:", seennicks
    
    if seennicks:
        for nick, channel, storedTime in seennicks.values():
            t = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(storedTime))
            currentTime = time.strftime('%H:%M:%S UTC', time.gmtime())
            rawTimeDifference_hours = (time.time() - storedTime) / 3600
            formattedTimeDiff = Decimal(str(rawTimeDifference_hours)).quantize(Decimal('1.00'))
            
            #requires python 2.7
            #timeDifference_hr = timeDifference_sec.total_seconds() / 3600
            
            msg = "I last saw %s %s hours ago at %s on %s.  Current time: %s" % (nick, formattedTimeDiff, t, channel, currentTime)
            phenny.reply(msg)
    
    #no record of user
    else: 
        phenny.say("Sorry, I haven't seen %s around." % input.group(2))
f_seen.rule = (['seen', 'lastseen'], r'(\S+)')

def f_note(phenny, input): 
    global storage
    if input.sender.startswith('#'):
        storage[input.nick.lower()] = (input.nick, input.sender, time.time())
        if hasattr(phenny, 'nicktracker') and input.canonnick:
            storage[input.canonnick.lower()] = (input.nick, input.sender, time.time())
f_note.rule = r'(.*)'
f_note.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()

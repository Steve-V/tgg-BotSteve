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

SEEN_LIMIT = 1

#NICKTRACKER: If passed a known registered user, check agaisnt all names they've used and print the most recent ones.

def f_seen(phenny, input): 
    """.seen <nick> - Reports when <nick> was last seen."""
    global storage
    
    if input.sender == '#talis': return
    try:
        nick = input.group(2).lower()
    except AttributeError:
        phenny.say("No user provided!")
        return 
    
    #misc easter eggs
    if nick.lower() == "kyle":
        return phenny.say("He's about this tall?  Seen Kyle?")
    if nick.lower() == phenny.nick.lower():
        return phenny.say("I'm right here, actually.")
    
    lnick = nick.lower()
    if lnick in storage:
        print("lnick {} is in storage".format(lnick)) #debug
        storage['nick:'+lnick] = storage[lnick]
        del storage[lnick]
    else:
        print("lnick {} not in storage".format(lnick)) #debug
    
    #when you make a string into a set, it gets broken into individual characters
    
    nicks = set('nick:'+lnick)
    print("Nicks (Line 47): {}".format(nicks))
    
    if hasattr(phenny, 'nicktracker'):
        nicks.add('account:'+phenny.nicktracker.canonize(nick).lower())
        alts, maybes = phenny.nicktracker.getalts(nick)
        # |= is a nicks.update() operation
        nicks |= set('nick:'+n.lower() for n in alts+maybes)
    
    seennicks = {}
    print("Beginning nick check")
    print("Nicks (Line 58): {}".format(nicks) )
    for nick in nicks:
        try:
            print("Checking: {}".format(nick))
            data = storage[nick]
            if len(data) == 2:
                data = storage[nick] = [nick, data[0], data[1]]
            seennicks[data[0].lower()] = data
        except KeyError:
            print("Keyerror on: {}".format(nick))
            pass
    
    print("Ending nick check")
    seennicks = sorted(seennicks.values(), key=lambda i: -i[2])
    
    print("Seen Nicks: {}".format(seennicks))
    
    if seennicks:
        showtime = True
        for nick, channel, storedTime in seennicks[:SEEN_LIMIT]:
            t = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(storedTime))
            currentTime = time.strftime('%H:%M:%S UTC', time.gmtime())
            rawTimeDifference_hours = (time.time() - storedTime) / 3600
            formattedTimeDiff = Decimal(str(rawTimeDifference_hours)).quantize(Decimal('1.00'))
            
            #requires python 2.7
            #timeDifference_hr = timeDifference_sec.total_seconds() / 3600
            
            msg = "I last saw %s %s hours ago at %s on %s." % (nick, formattedTimeDiff, t, channel)
            if showtime:
                msg += "  Current time: %s" % currentTime
            showtime = False
            phenny.reply(msg)
        #if len(seennicks) > SEEN_LIMIT:
            #phenny.reply("(%i more)" % (len(seennicks) - SEEN_LIMIT))
    
    #no record of user
    else: 
        phenny.say("Sorry, I haven't seen %s around." % input.group(2))
f_seen.rule = (['seen', 'lastseen'], r'(\S+)')

def f_note(phenny, input): 
    global storage
    if input.sender.startswith('#'):
        lnick = input.nick.lower()
        if lnick in storage:
            del storage[lnick]
        storage['nick:'+lnick] = (input.nick, input.sender, time.time())
        print("Supposedly added nick: {}".format( storage['nick:'+lnick] ) ) #debug
        if hasattr(phenny, 'nicktracker') and input.canonnick:
            storage['account:'+input.canonnick.lower()] = (input.nick, input.sender, time.time()) #XXX: Make this a list?
f_note.rule = r'(.*)'
f_note.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()

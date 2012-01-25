#!/usr/bin/env python
"""
tell.py - Phenny Tell and Ask Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import os, re, time, random
import web
from tools import startdaemon

maximum = 4
lispchannels = frozenset([ '#lisp', '#scheme', '#opendarwin', '#macdev',
'#fink', '#jedit', '#dylan', '#emacs', '#xemacs', '#colloquy', '#adium',
'#growl', '#chicken', '#quicksilver', '#svn', '#slate', '#squeak', '#wiki',
'#nebula', '#myko', '#lisppaste', '#pearpc', '#fpc', '#hprog',
'#concatenative', '#slate-users', '#swhack', '#ud', '#t', '#compilers',
'#erights', '#esp', '#scsh', '#sisc', '#haskell', '#rhype', '#sicp', '#darcs',
'#hardcider', '#lisp-it', '#webkit', '#launchd', '#mudwalker', '#darwinports',
'#muse', '#chatkit', '#kowaleba', '#vectorprogramming', '#opensolaris',
'#oscar-cluster', '#ledger', '#cairo', '#idevgames', '#hug-bunny', '##parsers',
'#perl6', '#sdlperl', '#ksvg', '#rcirc', '#code4lib', '#linux-quebec',
'#programmering', '#maxima', '#robin', '##concurrency', '#paredit' ])

storage = {}

def setup(phenny):
    if hasattr(phenny, 'nicktracker'):
        pass
#        phenny.nicktracker.connect('have-account', do_have_account) # Can't get the correct context yet.

#NICKTRACKER: Store to the canonical, so that they get told from other nicks

def f_remind(phenny, input): 
    teller = input.nick
    
    # @@ Multiple comma-separated tellees? Cf. Terje, #swhack, 2006-04-15
    verb, tellee, msg = input.groups()
    
    #NICKTRACKER: Canonize the nicks
    if hasattr(phenny, 'nicktracker'):
        tellee = phenny.nicktracker.canonize(tellee)
        teller = input.canonnick or teller
        print("DEBUG: Teller = {}".format(teller) )
    verb = verb.encode('utf-8')
    tellee = tellee.encode('utf-8')
    msg = msg.encode('utf-8')
    
    tellee_original = tellee.rstrip('.,:;')
    tellee = tellee_original.lower()
    
    if tellee == phenny.nick.lower():
       phenny.say("Sorry, I'm supposed to ignore any voices I hear in my head.")
       return
    
    if len(tellee) > 20: 
        return phenny.reply('That nickname is too long.')
    
    timenow = time.strftime('%d %b %H:%MZ', time.gmtime())
    if not tellee in (teller.lower(), phenny.nick, 'me'): # @@
        # @@ <deltab> and year, if necessary
        warn = False
        
        tells = storage.get(tellee, [])
        tels.append((teller, verb, timenow, msg))
        storage[tellee] = tells
        print("DEBUG - Tellee in storage. Storage Type: {} Storage[{}]: {}".format(tellee, type(storage), tells) )
        # @@ Stephanie's augmentation
        response = "I'll pass that on when %s is around." % tellee_original
        # if warn: response += (" I'll have to use a pastebin, though, so " + 
        #                       "your message may get lost.")
        
        rand = random.random()
        if rand > 0.9999: response = "yeah, yeah"
        elif rand > 0.999: response = "yeah, sure, whatever"
        
        phenny.reply(response)
    elif teller.lower() == tellee: 
        phenny.say('You can %s yourself that.' % verb.lower() )
    else: 
        phenny.say("Hey, I'm not as stupid as themotkid you know!")
f_remind.rule = ( r'(?i)$nick', ['tell','ask'], r'(\S+) (.*)' )

def getReminders(phenny, key, tellee): 
    lines = []
    #NICKTRACKER: Check this nick, canonical nick, and alt nicks.
    lines.append("%s: I have the following messages for you:" % tellee)
    template = "At %s, %s asked me to %s %s %s"
    today = time.strftime('%d %b', time.gmtime())
    
    for (teller, verb, datetime, msg) in storage[key]: 
        if datetime.startswith(today): 
            datetime = datetime[len(today)+1:]
        lines.append(template % (datetime, teller, verb, tellee, msg))
    
    try: 
        del storage[key]
    except KeyError: 
        phenny.say('Er...')
    return lines

def do_messages(phenny, nicks):
    tellees = list(nicks)
    for nick in nicks:
        if hasattr(phenny, 'nicktracker'):
            alts, maybes = phenny.nicktracker.getalts(nick)
            tellees += [phenny.nicktracker.canonize(nick)] + alts + maybes
    ltellees = [t.lower() for t in tellees]
    
    reminders = []
    remkeys = list(reversed(sorted(storage.keys())))
    for remkey in remkeys: 
        if not remkey.endswith('*') or remkey.endswith(':'): 
            if remkey in ltellees:
                reminders.extend(getReminders(phenny, remkey, remkey))
        else:
            srk = remkey.rstrip('*:')
            for lt in ltellees:
                if lt.startswith(srk):
                    reminders.extend(getReminders(phenny, remkey, lt))
    
    for line in reminders[:maximum]: 
        phenny.say(line)
    
    if reminders[maximum:]: 
        phenny.say('Further messages sent privately')
        for line in reminders[maximum:]: 
            phenny.msg(tellee, line)

def message(phenny, input): 
    if not input.sender.startswith('#'): return
    do_messages(phenny, [input.nick])
message.rule = r'(.*)'
message.priority = 'low'

#NICKTRACKER: Listen to the have-account event and check tells then.
def do_have_account(nt, phenny, nick, account, status):
    if status > 0:
        n = [nick]
        if account:
            n += [account]
        do_messages(phenny, n)

if __name__ == '__main__': 
   print __doc__.strip()

#!/usr/bin/env python
"""
greet.py - Phenny User Greeting Module
Copyright 2011, James Bliss, astro73.com
Licensed under the Eiffel Forum License 2.

http://github.com/Steve-V/tgg-BotSteve
"""
import random

storage = {
    'batsteve' : {
        'chance' : 5,
        'greets' : ['Welcome back, boss.'],
        },
    'captainboden' : {
        'chance' : 100,
        'greets' : ['****Attention on deck!  Captain on the bridge!****'],
        },
    'mman454' : {
        'chance' : 10,
        'greets' : ['You mess with the Bull, you get the horns!'],
        },
    'masterofmonks' : {
        'chance' : 50,
        'greets' : ['Spatula.'],
        },
    'tmbomber' : {
        'chance' : 100,
        'greets' : ['Welcome back, Mr. Kidwell'],
        },
    'seroster' : {
        'chance' : 5,
        'greets' : ['All right, show us on the doll where Seroster touched you.'],
        },
    'speedrunnerG55' : {
        'chance' : 10,
        'greets' : ['At last!  My only friend!'],
        },
    'ponko' : {
        'chance' : 10,
        'greets' : ['Ponko is credit to team!'],
        },
    'lwq1996' : {
        'chance' : 5,
        'greets' : ['**whispers** Quick, hide!  Before he sees us!'],
        },
    'wannabe1987' : {
        'chance' : 10,
        'greets' : ['Cookies, Sandwiches, Skittles, Oh my!'],
        },
    'toastdude' : {
        'chance' : 33,
        'greets' : ['TOASTY!'],
        },
    'astro73|mal' : {
        'chance' : 100,
        'greets' : ['Master. *bows*', 'Sensei. *bows*'],
        },
    }

def join_greeter(phenny, input):
    """
    Greets users based on options in the datastore.
    """
    global storage
    
    print "%s joined %s" % (input.nick, input.sender)
    
    nick = str(input.nick)
    #NICKTRACKER: Canonize the nick
    try:
        ginfo = storage[nick.lower()]
    except KeyError:
        return
    else:
        if random.randint(1,100) <= int(ginfo['chance']):
            phenny.say(random.choice(ginfo['greets']))

join_greeter.event = 'JOIN'
join_greeter.rule = r'(.*)'
join_greeter.priority = 'low'


if __name__ == '__main__': 
   print __doc__.strip()

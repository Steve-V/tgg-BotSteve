#!/usr/bin/env python
"""
barks.py - The Geek Group Phenny Module
Phenny Copyright 2008, Sean B. Palmer, inamidst.com
This module is copyright 2011, Steven Vaught
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

''' Keep sqlite local to this module for now '''

import random, socket

def bark(phenny, input):
    '''Manage all the one-liner barks that BotSteve contains'''
    #figure out which bark in particular we want
    
    barks = {
        "tell" : "Sorry, .tell is not yet implemented.  Use BotSteve: tell",
        "stream" : "The Geek Group Live Web Stream can be found at: http://justin.tv/thegeekgroup ",
        "code" : "You can download my code at https://github.com/Steve-V/tgg-BotSteve ",
        "history" : "Channel history can be found at: http://irclog.perlgeek.de/#thegeekgroup/today",
        "log" : "Channel history can be found at: http://irclog.perlgeek.de/#thegeekgroup/today",
        "tggbug" : "Problems with the bot?  Tell BatSteve.",
        "bug" : "Problems with the bot?  Tell BatSteve.",
        "websiteproblem" : "Problems with the bot?  Tell BatSteve.",
        "errorreport" : "Problems with the bot?  Tell BatSteve.",
        "error" : "Problems with the bot?  Tell BatSteve.",
        "retort" : "Your mother's a whore."
    }
    
    
    if not input.group(1):
        return phenny.say("Error in bark module")
    else:
        command = input.group(1)

    try:
        output = barks[command]
    except:
        return
    
    phenny.reply(output)
        
bark.commands = ['tell', 'stream', 'code', 'git', 'log', 'history', 'bug', 'tggbug', 'errorreport', 'error']
bark.priority = 'medium'

if __name__ == '__main__': 
   print __doc__.strip()

#!/usr/bin/env python
"""
ping.py - Phenny Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import random

def hello(phenny, input): 
   greeting = random.choice(('Hi', 'Hey', 'Hello', 'Word up', 'Greetings', 'Yo', 'Cheers'))
   punctuation = random.choice(('', '!'))
   phenny.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey|greetings) $nickname\b'

def interjection(phenny, input): 
   phenny.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

def thanks(phenny, input):
  reply = random.choice( ("You're welcome, ", "No problem, ", "Happy to help, ") )
  phenny.say(reply + input.nick)
thanks.rule = r'(?i)(thx|thanks|thank you|ty|thanks,|thank you,) $nickname\b'
thanks.priority = 'high'
thanks.thread = False

if __name__ == '__main__': 
   print __doc__.strip()

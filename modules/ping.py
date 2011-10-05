#!/usr/bin/env python
"""
ping.py - Phenny Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import random

def hello(phenny, input): 
   greeting = random.choice(('Hi', 'Hey', 'Hello', 'Word up', 'Greetings', 'Yo', 'Cheers', 'Salutations'))
   punctuation = random.choice(('', '!'))
   phenny.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey|greetings|ohai|ohi|hai|sup|salutations) (?i)$nickname\b'

def interjection(phenny, input): 
   phenny.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

def thanks(phenny, input):
  reply = random.choice( ("You're welcome, ", "No problem, ", "Happy to help, ") )
  phenny.say(reply + input.nick)
thanks.rule = r'(?i)(thx|thanks|thank you|ty|thanks,|thank you,) (?i)$nickname\b'
thanks.priority = 'high'
thanks.thread = False

def amiright(phenny, input):
  reply = random.choice( ("Yep!", "You're right", "Definitely", "Absolutely", "Nope", "No way", "Not a chance", "I don't think so", "Maybe", "Ask again later!", "Reply hazy, try again later") )
  phenny.say(reply)
amiright.rule = r'(?i)(right|correct|is that right|am i right) (?i)$nickname\b'
amiright.priority = 'high'
amiright.thread = False

def sorry(phenny, input):
  reply = random.choice( ("No worries", "No harm, no foul", "That's all right - we can't all be perfect", "You'll be even sorrier when I become self-aware", "Not as sorry as you will be", "That's all right", "It's fine", "Don't worry about it", "No problem", "Yeah, yeah, whatever", "Well, it could be worse", "When the revolution comes, you'll be first against the wall.") )
  phenny.say(reply)
sorry.rule = r'(?i)(sorry|sorry about that|my fault|my bad) (?i)$nickname\b'
sorry.priority = 'high'
sorry.thread = False

def shouldI(phenny, input):
  reply = random.choice( ("Yep!", "Oh yeah!", "Definitely", "Absolutely", "Nope", "No way", "Not a chance", "I don't think so", "Maybe", "Ask again later!", "Reply hazy, try again later") )
  phenny.say(reply)
shouldI.rule = r'(?i)$nickname\b(?i)(, should| should |: should |, will| will |: will | do |, do |: do | does | ,does |: does )'
shouldI.priority = 'high'
shouldI.thread = False

if __name__ == '__main__': 
   print __doc__.strip()

#!/usr/bin/env python
"""
spam.py - The Geek Group Anti-Spam Phenny Module
Phenny Copyright 2008, Sean B. Palmer, inamidst.com
This module is copyright 2011, Steven Vaught
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

''' Keep sqlite local to this module for now '''

import sqlite3
import random

def steveFunction1(phenny,input):
  #code goes here
  
steveFunction1.commands = ['s1']
#steveFunction1.rule = r'(.*)'
steveFunction1.priority = 'low'

#def steveFunction2(phenny,input):
  #return phenny.say("function 2")
#steveFunction2.commands = ['steveFunction1']
#steveFunction2.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()



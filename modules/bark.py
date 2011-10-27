#!/usr/bin/env python
"""
tgg.py - The Geek Group Phenny Module
Phenny Copyright 2008, Sean B. Palmer, inamidst.com
This module is copyright 2011, Steven Vaught
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

''' Keep sqlite local to this module for now '''

import sqlite3


def bark(phenny, input):
  '''Get some bark from the database and print it'''
  
  #figure out which bark in particular we want
  if not input.group(1):
    return phenny.say("Error in bark module")
  else:
    command = input.group(1)
    commandTuple = (command,)
  
  #connect to the database
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  
  db_curr.execute( "SELECT * FROM barks WHERE command=?;", commandTuple )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    output = db_result[1]
    
    phenny.say("%s" % output )
bark.commands = ['minecraft', 'tell', 'stream', 'code', 'git', 'log', 'history', 'bug', 'tggbug', 'errorreport', 'error']
bark.priority = 'medium'


if __name__ == '__main__': 
  print __doc__.strip()





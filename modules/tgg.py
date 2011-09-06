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
import random

def fortune(phenny, input): 
  import subprocess
  subp = subprocess.Popen( ['fortune', '-s', 'computers'] , stdout=subprocess.PIPE)
  stdo = subp.communicate()[0]
  phenny.say( stdo )
fortune.commands = ['quote', 'fortune']
fortune.example = ".quote"
fortune.priority = 'low'

def minecraft(phenny, input):
  #phenny.say( "The minecraft server is currently down." )
  phenny.say( "The 'official' TGG minecraft server address is: gamerxreviews.net **** The server may or may not be down right now.  Try it and let us know." )
minecraft.commands = ['minecraft']
minecraft.example = ".minecraft"
minecraft.priority = 'low'

def tellPlaceholder(phenny, input):
  phenny.say("Sorry, .tell is not yet implemented.  Use BotSteve: tell ")
tellPlaceholder.commands = ['tell']
tellPlaceholder.example = ['Not yet implemented']
tellPlaceholder.priority = 'low'

def liveStream(phenny, input):
  phenny.say("The Geek Group Live Web Stream can be found at: http://justin.tv/thegeekgroup ")
liveStream.commands = ['stream']
liveStream.example = ['.stream']
liveStream.priority = 'medium'

def coinFlip(phenny, input):
  import random
  coinResult = random.choice(('Heads!', 'Tails!'))
  phenny.say(coinResult)
coinFlip.commands = ['coin']
coinFlip.example = ['.coin']
coinFlip.priority = 'medium'

def logFile(phenny, input):
  phenny.say("Channel history can be found at: http://irclog.perlgeek.de/thegeekgroup/today")
logFile.commands = ['history','log']
logFile.example = ['View the history with:  .history']
logFile.priority = 'medium'

def rollD20(phenny, input):
  import random
  diceResult = random.choice( range(1,21) )
  phenny.say( str(diceResult) )
rollD20.commands = ['d20']
rollD20.example = ['.d20']
rollD20.priority = 'medium'

def rollD6(phenny, input):
  import random
  diceResult = random.choice( range(1,7) )
  phenny.say( str(diceResult) )
rollD6.commands = ['dice','d6']
rollD6.example = ['.dice']
rollD6.priority = 'medium'

def join_greeter(phenny, input):
  """
  Greetings depend on new sqlite database.  Schema is simple:

  CREATE TABLE greetings (id INTEGER PRIMARY KEY, nickname, greeting, chance);

  By default, the datebase lives in the bot's root directory tgg-BotSteve/tgg.db

  Will eventually add auto-create and add code
  """

  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()

  nick = str(input.nick)
  t = (nick,)
  #db_query = "SELECT * FROM greetings WHERE nickname = '%s';" % nick
  db_curr.execute( "SELECT * FROM greetings WHERE nickname = ?;" , t )
  db_result = db_curr.fetchone()

  if (db_result):
    greet = db_result[2]
    chance = db_result[3]
    
    #chance is an integer from 1 to 100, from the database
    #if an integer chosen at random is below that, send the greet
    #if the random integer is lower than the person's chance value, greet
    import random
    if random.randint(1,100) <= int(chance):
      phenny.say(greet)
    

  db_conn.close()
  
join_greeter.event = 'JOIN'
join_greeter.rule = r'(.*)'
join_greeter.priority = 'low'

def insult_user(phenny, input):
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  nick = str(input.nick)
  t = (nick,)
  
  db_curr.execute( "SELECT * FROM insults;" )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    insult = random.choice(db_result)[1]
    phenny.say("Hey, " + str(nick) + ", " + str(insult) )
insult_user.commands = ['insult']
insult_user.priority = 'medium'

def give_cookie(phenny, input):
  #if it's the bot getting the cookie, or if the user is cookieing themselves
  #code here
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      return( phenny.say("For me?  Thank you!  *om nom nom*") )
    else:
      recepient = input.group(2)
  else:
    recepient = str(input.nick)
  #otherwise give specified user a cookie
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  #nick = str(input.nick)
  
  db_curr.execute( "SELECT * FROM cookie_flavors;" )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    flavor = random.choice(db_result)[1]
    
    if str(flavor)[0].lower() in ['a','e','i','o','u']:
      seperator = 'an'
    else:
      seperator = 'a'
    
    phenny.say("Here you go, %s, I baked you %s %s cookie!" % (recepient, seperator, str(flavor) ) )
give_cookie.commands = ['cookie']
give_cookie.priority = 'medium'

def give_food(phenny, input):
  #if it's the bot getting the cookie, or if the user is cookieing themselves
  #code here
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      return( phenny.say("For me?  Thank you!  *om nom nom*") )
    else:
      recepient = input.group(2)
  else:
    recepient = str(input.nick)
  #otherwise give specified user a cookie
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  #nick = str(input.nick)
  
  db_curr.execute( "SELECT * FROM cookie_flavors;" )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    flavor = random.choice(db_result)[1]
    
    if str(flavor)[0].lower() in ['a','e','i','o','u']:
      seperator = 'an'
    else:
      seperator = 'a'
    
    phenny.say("Here you go, %s, I baked you %s %s cookie!" % (recepient, seperator, str(flavor) ) )
give_food.commands = ['nom']
give_food.priority = 'medium'


def give_skittles(phenny, input):
  #if it's the bot getting the cookie, or if the user is cookieing themselves
  #code here
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      return( phenny.say("For me?  Thank you!  Rainbows taste delicious!") )
    else:
      recepient = input.group(2)
  else:
    recepient = str(input.nick)
  #otherwise give specified user a cookie
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  #nick = str(input.nick)
  
  db_curr.execute( "SELECT * FROM skittles_colors;" )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    flavor = random.choice(db_result)[1]
    
    phenny.say("Here you go, %s, I got you some %s skittles!" % (recepient, str(flavor) ) )
give_skittles.commands = ['skittles']
give_skittles.priority = 'medium'


def give_element(phenny, input):
  #if it's the bot getting the element, or if the user is elementing themselves
  #code here
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      return( phenny.say("Hmmm elements, the one thing i dont understand...") )
    else:
      recepient = input.group(2)
  else:
    recepient = str(input.nick)
  #otherwise give specified user an element
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  #nick = str(input.nick)
  
  db_curr.execute( "SELECT * FROM element_type;" )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    flavor = random.choice(db_result)[1]
    
    phenny.say("Here you go, %s, I'm giving you 20kg. of pure %s !" % (recepient, str(element) ) )
give_element.commands = ['element']
give_element.priority = 'medium'


def give_sandwhich(phenny, input):
  #if it's the bot getting the sandwhich, or if the user is sandwhiching themselfs
  #code here
  if input.group(2):
    if input.group(3).lower() == phenny.nick.lower():
	  return(phenny.say("For me?  Thank you!  **gloms down and does not leave a single crumb on the plate.**
    else:
	  recepient = input.group(2) 
	 #otherwise give specified user sandwhich
	 db_coon = sqlite3.connect("tgg.db")
	 db_curr = db_conn.cursor()
	 #nick = str(input.nick)
	 
	 db_curr.execute( "SELLECT * FROM sandwhich_type;" )
	 db_result = db_curr.fetchall()
	 
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    flavor = random.choice(db_result)[1]
	   
	phenny.say("Here you go, %s, I made you a %s sandwhich!" % (recepient, str(flavor) ) )
give_sandwhich.commands = ['sandwhich']
give_sandwhich.priority - 'medium'


def steveFunction1(phenny,input):
  if not input.group(1):
    return phenny.say("no input")
  else:
    return phenny.say(input.group(1))
steveFunction1.commands = ['steveFunction1','steveFunction2']
steveFunction1.priority = 'low'


if __name__ == '__main__': 
   print __doc__.strip()





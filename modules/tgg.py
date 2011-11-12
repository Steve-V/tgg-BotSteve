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
import random, socket

def fortune(phenny, input): 
  import subprocess
  import string
  subp = subprocess.Popen( ['fortune', '-s', 'computers'] , stdout=subprocess.PIPE)
  stdo = subp.communicate()[0]
  phenny.say( string.replace(stdo,"\n"," ") )
fortune.commands = ['quote', 'fortune']
fortune.example = ".quote"
fortune.priority = 'low'

def minecraft(phenny, input):
    s = socket.socket()
    try:
        s.connect(('gamerxreviews.net', 25565))
    except:
        phenny.say( "The 'official' TGG minecraft server address is: gamerxreviews.net **** THE SERVER IS DOWN ****" )
    else:
        phenny.say( "The 'official' TGG minecraft server address is: gamerxreviews.net (online)" )
minecraft.commands = ['minecraft']
minecraft.example = ".minecraft"
minecraft.priority = 'low'
minecraft.thread = True

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

def BotStevesCode(phenny, input):
  phenny.say("my code download can be found at https://github.com/Steve-V/tgg-BotSteve ")
BotStevesCode.commands = ['botsteves_code']
BotStevesCode.example = ['.botsteves_code']
BotStevesCode.priority = 'medium'

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

def bugReport(phenny, input):
  phenny.say( "To report website bugs, email:  helpdesk at thegeekgroup dot org" )
bugReport.commands = ['tggbug','bug','websiteproblem','errorreport','error']
bugReport.example = ['.tggbug']
bugReport.priority = 'medium'

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
  
  #see if there's something after the command...
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      #that is, if the bot should get the element itself
      return( phenny.say("Hmmm, elements, the one thing I don't understand...") )
    else:
      #otherwise, we need to figure out who and how much
      recepient = input.group(2)
  else:
    #if there's nothing after the command, give it to the person who triggered the command
    recepient = str(input.nick)
  #otherwise give specified user an element
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  #nick = str(input.nick)
   
  db_curr.execute( "SELECT * FROM element_type;" )
  db_result = db_curr.fetchall()

   
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    element = random.choice(db_result)[1]
    
    amount_digits = random.choice( range(2,501) )
    amount_units = random.choice( ["grams","kilograms","milligrams","bags","bushels","metric tons","board feet", "stere", "olympic-size swimming pools", "gigaliters", "fully loaded 747's", "troy ounces", "dime bags", "syringes", "backpacks", "gaylords", "handfuls"] )
    amount = str(amount_digits) + " " + str(amount_units)
    
    phenny.say("Here you go, %s, I'm giving you %s of pure %s !" % (recepient, amount, str(element) ) )
give_element.commands = ['element']
give_element.priority = 'medium'

def give_sandwich(phenny, input):
  #if it's the bot getting the sandwich, or if the user is sandwiching themselfs
  #code here
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      return(phenny.say("For me?  Thank you!  **gloms down the sandwich like pig he is and licks the plate clean.**"))
    else:
      recepient = input.group(2) 
  else:
    recepient = str(input.nick)
  #otherwise give specified user sandwich
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  #nick = str(input.nick)
  
  db_curr.execute( "SELECT * FROM sandwich_type;" )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    flavor = random.choice(db_result)[1]
    
  phenny.say("Here you go, %s, I made you a %s sandwich!" % (recepient, str(flavor) ) )
give_sandwich.commands = ['sandwich']
give_sandwich.priority = 'medium'

def give_shake(phenny, input):
  #if it's the bot getting the shake, or if the user is shakeing themselfs
  #code here
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      return(phenny.say("For me?  Thank you!  ** Slurp Slurp Slurp.** That was refreshing"))
    else:
      recepient = input.group(2) 
  else:
    recepient = str(input.nick)
  #otherwise give specified user shake
  db_conn = sqlite3.connect("tgg.db")
  db_curr = db_conn.cursor()
  #nick = str(input.nick)
  
  db_curr.execute( "SELECT * FROM shake_flavor;" )
  db_result = db_curr.fetchall()
  
  if (db_result):
    #first choose a db_result at random, then take element 1 of that result (the insult itself)
    flavor = random.choice(db_result)[1]
    
  phenny.say("Here you go, %s, I made you a %s shake!" % (recepient, str(flavor) ) )
give_shake.commands = ['shake']
give_shake.priority = 'medium'

def steveFunction1(phenny,input):
  if not input.group(1):
    return phenny.say("no input")
  else:
    return phenny.say(input.group(1))
steveFunction1.commands = ['steveFunction1','steveFunction2']
steveFunction1.priority = 'low'


def yuno(phenny, input):
  yunos = ["*Sharpening pencil, and it keeps breaking as i pull it out...* Pencil: Y U NO SHARPEN RIGHT??????????????","Fox News: Y U NO HAVE NEWS ABOUT FOXES??????????","Internet: Y U NO LET ME STUDY??????????","Asprin: Y U NO WORK????????","Cat: Y U NO SPEEK ENGRISH?????????","I txt u: Y U NO TXT BACK????????????????","Rebecca Black: Y U NO JUST CHOOSE SEAT????????????","College Degree: Y U NO GET ME JOB????????????","Weekend: Y U NO LAST LONGER???????????","Idea: Y U NO COM TO ME??????????????????","Little Kids: Y U NO SPELL RIGHT???????????","Obama: Y U NO USE RADOACTIVE TOILET???????????????","Fat people who don't wear shirts: Y U NO HAVE SHAME??????","Work: Y U NO FINISH YET???????????","It's Friday, Friday: Y U NO HAS EXCITED???????????","Daylight Savings: Y U NO SAVE TIME?????????","Soup: Y U NO STAY IN BOWL???????????????","Printer: Y U NO PRINT?????????????","Facebook Chat: Y U NO GO FAST????????????????","User: Y U NO HAVE LIFE??????????????????"]



  if (yunos):
    val = random.choice(yunos)
    phenny.say(val)
yuno.commands = ['yuno']
yuno.priority = 'medium'



def give_cake(phenny, input):
 
  if input.group(2):
    if input.group(2).lower() == phenny.nick.lower():
      return( phenny.say("For me?  Thank you!  *Looks at cake with a crazed look in his eyes*") )
    else:
      recepient = input.group(2)
  else:
    recepient = str(input.nick)
  
  flavors = ["almond","almond amaretto cream","apples and cinnamon","banana caramel","bananas foster","beurre noisette","black forest","blackberry sourcream","blueberry muffin","brownie","butterscotch walnut","cardamom and pistachio","carrot","cherry and almond","chocolate","chocolate chip muffin","chocolate espresso","chocolate mint","chocolate orange","chocolate raspberry","curry caramel","dulce de leche","egg nog","ginger and green tea","italian orange and vanilla","lemon","lemon curd and berries","lemon poppyseed","marble","mudslide","orange and ginger","peaches and cream","peanut butter and jelly","peanut butter cup","pear compote and ginger","pear spice","pecan pie","pineapple coconut","pumpkin and cinnamon","pumpkin chocolate chip","red velvet","Rum","smores","strawberry shortcake","tiramisu","white","white chocolate raspberry","yellow","yellow with chocolate buttercream"]
  
  if (flavors):
    val = random.choice(flavors)
    
    if str(val)[0] in ['a','e','i','o','u']:
      seperator = 'an'
    else:
      seperator = 'a'
    
    phenny.say("Here you go, %s, I baked you %s %s cake!" % (recepient, seperator, str(val) ) )
give_cake.commands = ['cake']
give_cake.priority = 'medium'



if __name__ == '__main__': 
   print __doc__.strip()


# HI TOASTDUDE

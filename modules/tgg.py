#!/usr/bin/env python
"""
tgg.py - The Geek Group Phenny Module
Phenny Copyright 2008, Sean B. Palmer, inamidst.com
This module is copyright 2011, Steven Vaught
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""


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
  phenny.say("The Geek Group Live Web Stream can be found at: http://www.ustream.tv/channel/the-geek-group-behind-the-scenes-live-feed ")
liveStream.commands = ['stream']
liveStream.example = ['Not yet implemented']
liveStream.priority = 'low'

def coinFlip(phenny, input):
  import random
  coinResult = random.choice(('Heads!', 'Tails!'))
  phenny.say(coinResult)
coinFlip.commands = ['coin']
coinFlip.example = ['.coin']
coinFlip.priority = 'low'

def logFile(phenny, input):
  phenny.say("Channel history can be found at: http://irclog.perlgeek.de/thegeekgroup/today")
logFile.commands = ['history','log']
logFile.example = ['View the history with:  .history']
logFile.priority = 'low'

def join_greeter(phenny, input):
  if (input.nick == "BatSteve"):
    phenny.say("Welcome back, boss")
  if (input.nick == "Bat-Mobile"):
		phenny.say("Welcome back, boss")
  if (input.nick == "CptBoden"):
    phenny.say("***Attention on deck!  Captain on the bridge!***")
  if (input.nick == "CaptainBoden"):
		phenny.say("***Attention on deck!  Captain on the bridge!***")
  if (input.nick == "Cpt_Boden"):
    phenny.say("***Attention on deck!  Captain on the bridge!***")
  if (input.nick == "Captain_"):
    phenny.say("***Attention on deck!  Captain on the bridge!***")
  if (input.nick == "Captain__"):
    phenny.say("***Attention on deck!  Captain on the bridge!***")
  if (input.nick == "Captain"):
    phenny.say("***Attention on deck!  Captain on the bridge!***")
  if (input.nick == "lis"):
    phenny.say("Hi Lis!  Nice to see you in IRC again!")
  if (input.nick == "TMB"):
    phenny.say("Good to see you again, Mr. Kidwell!")
  if (input.nick == "masterofmonks"):
    phenny.say("Hey monks - spatula!  Ha!  Beat you to it!")
  if (input.nick == "Seroster"):
    phenny.say("Oh balls, it's him again...")
  
join_greeter.event = 'JOIN'
join_greeter.rule = r'(.*)'
join_greeter.priority = 'low'


if __name__ == '__main__': 
   print __doc__.strip()





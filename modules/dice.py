#!/usr/bin/env python
"""
dice.py - The Geek Group Phenny Module
Phenny Copyright 2008, Sean B. Palmer, inamidst.com
This module is copyright 2011, Steven Vaught
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import random

def rolldice(phenny, input):
    import random
    
    
    #check if there is anything after dice
    if not input.group(2):
    #then roll a d6 and return
        return( phenny.reply( str( random.choice( range(1,7) ) ) ) )
    
    
    #if there is something else, then...
    #if there's a space, then we are using "dice 1 20" format
    args = input.group(2).lower()
    
    #handle negative modifiers
    if "-" in args:
        args = args.replace("-","+-")
    if "+" in args:
        # there's a static modifier
        (args,sep,modifier) = args.partition('+')
        modifier = modifier.strip()
        if modifier == "":
            modifier = 0
        try:
            modifier = int(modifier)
        except:
            return(phenny.reply("Can't understand that") )
        modifierExists = True
    else:
        modifier = 0
        modifierExists = False
    
    # regardless of modifier, do the following
    if " " in args:
      #then split the string by the space
      (dice,sep,sides) = args.partition(' ')
      dice = dice.strip()
      sides = sides.strip()
    #if there's a 'd' then we are using '1d20' format
    elif "d" in args:
      #then split the string by the d
      (dice,sep,sides) = args.partition('d')
      dice = dice.strip()
      sides = sides.strip()
    else:
      return( phenny.reply("Can't translate that! Use '.dice 1d20' or '.dice 1 20' format") )
    print("Dice: {}, Sides: {}, Mod: {}".format(dice,sides,modifier) )
    
    # stupid user checking
    try:
        dice = int(dice)
        sides = int(sides)
    except:
        return( phenny.reply("Can't translate that! (If you're using d notation, don't use spaces)") )
    
    #not enough dice
    if dice == "":
        dice = 1
    if dice < 1:
        dice = 0
    
    # not enough sides
    if sides == "":
        sides = 6
    if sides <= 1:
        return( phenny.reply("Non-Euclidean dice not supported!") )
    
    # too many dice or sides
    if dice > 10:
        dice = 10
    if sides > 1000:
        sides = 1000
        
    diceResult = []
    for eachDice in range(dice):
        diceResult.append( random.choice( range(1,sides+1) ) )
    
    #print(diceResult)
    total = sum(diceResult)
    if modifierExists:
        if modifier < 0:
            plusMinus = ""
        else:
            plusMinus = "+"
        seperator = " {}{} = ".format( plusMinus, str(modifier) )
        total += modifier
    else:
        seperator = " = "
    phenny.reply( "{}{} {}".format( str(diceResult), seperator, total ) )
rolldice.commands = ['dice']
rolldice.example = ['.dice']
rolldice.priority = 'medium'


if __name__ == '__main__': 
   print __doc__.strip()

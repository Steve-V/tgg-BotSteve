#!/usr/bin/env python
"""
rss.py - The Geek Group RSS Feedreader Phenny Module
Phenny Copyright 2008, Sean B. Palmer, inamidst.com
http://inamidst.com/phenny/

This module is copyright 2011, Steven Vaught
Licensed under the MIT License: http://www.opensource.org/licenses/mit-license.php

"""


#later we can make this use SQlite if we want
#import sqlite3
import time, threading, feedparser

def setup(phenny): 

  def monitor(phenny): 
    #set up the channel that messages will be transmitted to
    #FIXME
    #this should be read from a config file
    whichChannel = '#tgg-bots'
    #pull original feed
    oldFeed = feedparser.parse("http://thegeekgroup.org/bb/?xfeed=all&feedkey=60635da5-d00a-4f9e-a007-a9102251b1c1")
    import time
    time.sleep(20)
    
    while True: 
      
      #pull feed again
      #phenny.msg(whichChannel, "Pulling new feed")
      currentFeed = ''
      currentFeed = feedparser.parse("http://thegeekgroup.org/bb/?xfeed=all&feedkey=60635da5-d00a-4f9e-a007-a9102251b1c1")
      
      #compare feeds
      titlesOld = []
      titlesCurrent = []
      titlesChanged = []
      for items in oldFeed.entries:
        titlesOld.append(items.updated)
      for items in currentFeed.entries:
        titlesCurrent.append( (items.title,items.updated) )
      
      for title,time in titlesCurrent:
        if time not in titlesOld:
          titlesChanged.append(title)
      
      #build the output string
      outputString = 'There have been '
      outputString += str( len(titlesChanged) )
      outputString += " new posts on the Geek Group forums.  New posts made by: "
      for eachPost in titlesChanged:
        outputString += eachPost
        if eachPost != titlesChanged[-1]:
          outputString += "....."
      
      #print the string only if there's something to output
      if titlesChanged:
        phenny.msg(whichChannel, outputString)
        oldFeed = currentFeed #don't forget to update
      
      #debugging
      #else:
        #phenny.msg(whichChannel, "No new feeds")
      
      #phenny.msg(whichChannel, "sleeping...")
      import time
      time.sleep(250)
  
  targs = (phenny,)
  t = threading.Thread(target=monitor, args=targs)
  t.start()



if __name__ == '__main__': 
  print __doc__.strip()





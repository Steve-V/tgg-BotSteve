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
import time, threading, feedparser, gdata.youtube, gdata.youtube.service

def setup(phenny): 

  def monitor(phenny): 
    #set up the channel that messages will be transmitted to
    #FIXME
    #this should be read from a config file
    mainChannel = '#thegeekgroup'
    testChannel = '#tgg-bots'
    youtubeUserName = 'physicsduck'
    tggUserName = 'thegeekgroup'
    
    #pull original forum feed
    oldFeed = feedparser.parse("http://thegeekgroup.org/bb/?xfeed=all&feedkey=60635da5-d00a-4f9e-a007-a9102251b1c1")
    
    #pull physicsduck original youtube feed
    youtubeServe = gdata.youtube.service.YouTubeService()
    youtubeUri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % youtubeUserName
    oldYoutubeFeed = youtubeServe.GetYouTubeVideoFeed(youtubeUri)
    
    #pull thegeekgroup original youtube feed
    youtubeTggServe = gdata.youtube.service.YouTubeService()
    youtubeTggUri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % tggUserName
    oldTggYoutubeFeed = youtubeServe.GetYouTubeVideoFeed(youtubeTggUri)
    
    import time
    time.sleep(20)
    
    while True: 
      
      #pull forum feed again
      #phenny.msg(testChannel, "Pulling new video feeds")
      currentFeed = ''
      currentFeed = feedparser.parse("http://thegeekgroup.org/bb/?xfeed=all&feedkey=60635da5-d00a-4f9e-a007-a9102251b1c1")
      
      #compare forum feeds
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
      outputString = 'In the last hour, there have been '
      outputString += str( len(titlesChanged) )
      outputString += " new posts on the Geek Group forums.  New posts made by: "
      for eachPost in titlesChanged:
        outputString += eachPost
        if eachPost != titlesChanged[-1]:
          outputString += "....."
      
      #print the string only if there's something to output
      if titlesChanged:
        phenny.msg(mainChannel, outputString)
        oldFeed = currentFeed #don't forget to update
      
      #=======================
      
      #pull physicsduck feed again
      currentYoutubeFeed = youtubeServe.GetYouTubeVideoFeed(youtubeUri)
      
      #compare forum feeds
      youtubeURLsOld = []
      youtubeTitlesCurrent = []
      youtubeTitlesChanged = []
      
      for items in oldYoutubeFeed.entry:
        youtubeURLsOld.append( str( items.GetSwfUrl() ).split("?")[0] )
      for items in currentYoutubeFeed.entry:
        youtubeTitlesCurrent.append( (items.media.title.text, str( items.GetSwfUrl() ).split("?")[0] ) )
      
      for title,url in youtubeTitlesCurrent:
        if url not in youtubeURLsOld:
          youtubeTitlesChanged.append( [title, url] )
      
      #rebuild the output string
      if youtubeTitlesChanged:
        outputString = 'In the last hour, there have been '
        outputString += str( len(youtubeTitlesChanged) )
        outputString += " new YouTube videos posted by PhysicsDuck.  New videos: "
        #print the header
        phenny.msg(mainChannel, outputString)
        
        #print the videos
        for eachTitle, eachURL in youtubeTitlesChanged:
          formattedURL = eachURL.replace("http://www.youtube.com/v/","http://www.youtube.com/watch?v=")
          outputString = eachTitle
          outputString += " "
          outputString += formattedURL
          phenny.msg(mainChannel, outputString)
        
        #update to the new feed
        oldYoutubeFeed = currentYoutubeFeed
      
      #debugging
      else:
        pass
        #phenny.msg(testChannel, "No new feeds")
      
      #=======================
      
      #pull thegeekgroup feed again
      currentYoutubeTggFeed = youtubeTggServe.GetYouTubeVideoFeed(youtubeTggUri)
      
      #compare forum feeds
      youtubeTggURLsOld = []
      youtubeTggTitlesCurrent = []
      youtubeTggTitlesChanged = []
      
      for items in oldTggYoutubeFeed.entry:
        youtubeTggURLsOld.append( str( items.GetSwfUrl() ).split("?")[0] )
      for items in currentYoutubeTggFeed.entry:
        youtubeTggTitlesCurrent.append( (items.media.title.text, str( items.GetSwfUrl() ).split("?")[0] ) )
      
      for title,url in youtubeTggTitlesCurrent:
        if url not in youtubeTggURLsOld:
          youtubeTggTitlesChanged.append( [title, url] )
      
      #rebuild the output string
      if youtubeTggTitlesChanged:
        outputString = 'In the last hour, there have been '
        outputString += str( len(youtubeTggTitlesChanged) )
        outputString += " new YouTube videos posted by TheGeekGroup.  New videos: "
        #print the header
        phenny.msg(mainChannel, outputString)
        
        #print the videos
        for eachTitle, eachURL in youtubeTggTitlesChanged:
          formattedURL = eachURL.replace("http://www.youtube.com/v/","http://www.youtube.com/watch?v=")
          outputString = eachTitle
          outputString += " "
          outputString += formattedURL
          phenny.msg(mainChannel, outputString)
        
        #update to the new feed
        oldTggYoutubeFeed = currentYoutubeTggFeed
      
      #debugging
      else:
        pass
        #phenny.msg(testChannel, "No new feeds")
      
      #phenny.msg(testChannel, "sleeping...")
      import time
      time.sleep(3600)
  
  targs = (phenny,)
  t = threading.Thread(target=monitor, args=targs)
  t.start()



if __name__ == '__main__': 
  print __doc__.strip()





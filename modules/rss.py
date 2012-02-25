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
from decimal import *

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
        oldFeed = feedparser.parse("http://thegeekgroup.org/forums/feed")
        
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
            print("Pulling new video feeds: {}".format(testChannel)) #DEBUG
            currentFeed = ''
            currentFeed = feedparser.parse("http://thegeekgroup.org/forums/feed")
            
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
            outputString = 'In the last hour, there have been {} new posts on the Geek Group forums ( http://goo.gl/t0vze ).  Topic: '.format(str(len(titlesChanged)))
            
            for eachPost in titlesChanged:
                outputString += eachPost
                if eachPost != titlesChanged[-1]:
                    outputString += "....."
            
            #print the string only if there's something to output
            if titlesChanged:
                print("{}".format(outputString))
                #phenny.msg(mainChannel, outputString)
            else:
                print("No new RSS feeds")
                oldFeed = currentFeed #don't forget to update
            
            #=======================
            
            #set up the output string as blank
            outputString = ""
            
            #pull physicsduck feed again
            currentYoutubeFeed = youtubeServe.GetYouTubeVideoFeed(youtubeUri)
            
            #compare forum feeds
            youtubeURLsOld = []
            youtubeTitlesCurrent = []
            youtubeTitlesChanged = []
            
            for items in oldYoutubeFeed.entry:
                youtubeURLsOld.append( str( items.GetSwfUrl() ).split("?")[0] )
            for items in currentYoutubeFeed.entry:
                youtubeTitlesCurrent.append( (items.media.title.text, str( items.GetSwfUrl() ).split("?")[0], items.media.duration.seconds ) )
            
            for title,url,duration in youtubeTitlesCurrent:
                if url not in youtubeURLsOld:
                    youtubeTitlesChanged.append( [title, url, duration] )
            
            #rebuild the output string
            if youtubeTitlesChanged:
                outputString += 'In the last hour, there have been '
                outputString += str( len(youtubeTitlesChanged) )
                outputString += " new YouTube videos posted by PhysicsDuck.  New videos:   "
                #print the header
                #phenny.msg(mainChannel, outputString)
                
                #print the videos
                for eachTitle, eachURL, eachDuration in youtubeTitlesChanged:
                    formattedURL = eachURL.replace("http://www.youtube.com/v/","http://youtu.be/")
                    
                    unformattedTime = str(float(eachDuration) / 60.0)
                    decimalTime = Decimal(str(unformattedTime)).quantize(Decimal('1.00'))
                    formattedTime = "[" + str(decimalTime) + " min]"
                    print("Formatted Time (PhysicsDuck): {}".format(formattedTime)) #DEBUG
                    outputString += eachTitle
                    outputString += formattedTime
                    outputString += " "
                    outputString += formattedURL
                    
                    #don't display the string - preserved for historical purposes
                    #phenny.msg(mainChannel, outputString)
                
                #update to the new feed
                oldYoutubeFeed = currentYoutubeFeed
            
            #debugging
            else:
                #pass
                print("No new feeds from PhysicsDuck")
            
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
                youtubeTggTitlesCurrent.append( (items.media.title.text, str( items.GetSwfUrl() ).split("?")[0], items.media.duration.seconds  ) )
            
            for title,url,duration in youtubeTggTitlesCurrent:
                if url not in youtubeTggURLsOld:
                    youtubeTggTitlesChanged.append( [title, url, duration] )
            
            #rebuild the output string
            if youtubeTggTitlesChanged:
                #if there's something already in the output string from above
                if outputString:
                    outputString += " ||| "
                outputString += 'In the last hour, there have been '
                outputString += str( len(youtubeTggTitlesChanged) )
                outputString += " new YouTube videos posted by TheGeekGroup.  New videos: "
                #print the header
                #phenny.msg(mainChannel, outputString)
                
                #print the videos
                for eachTitle, eachURL, eachDuration in youtubeTggTitlesChanged:
                    formattedURL = eachURL.replace("http://www.youtube.com/v/","http://youtu.be/")
                    unformattedTime = str(float(eachDuration) / 60.0)
                    decimalTime = Decimal(str(unformattedTime)).quantize(Decimal('1.00'))
                    formattedTime = "[" + str(decimalTime) + " min]"
                    print("Formatted Time (TheGeekGroup): {}".format(formattedTime))
                    outputString += eachTitle
                    outputString += formattedTime
                    outputString += " "
                    outputString += formattedURL
                    
                    #don't display the string - preserved for historical purposes
                    #phenny.msg(mainChannel, outputString)
                
                #update to the new feed
                oldTggYoutubeFeed = currentYoutubeTggFeed
            
            #debugging
            else:
                #pass
                print("No new feeds from TheGeekGroup")
            
            #display the string, if there's anything to display
            if outputString:
                phenny.msg(mainChannel, outputString)
            
            #phenny.msg(testChannel, "sleeping...")
            import time
            time.sleep(3600)

    targs = (phenny,)
    t = threading.Thread(target=monitor, args=targs)
    t.daemon = True
    t.start()



if __name__ == '__main__': 
    print __doc__.strip()





#!/usr/bin/env python
"""
rss.py - The Geek Group RSS Feedreader Phenny Module
Phenny Copyright 2008, Sean B. Palmer, inamidst.com
http://inamidst.com/phenny/

This module is copyright 2011, Steven Vaught
Licensed under the MIT License: http://www.opensource.org/licenses/mit-license.php

"""


import time, threading, feedparser, gdata.youtube, gdata.youtube.service
from decimal import *

class rssWatcher:
    def __init__(self, watchTarget):
        # Get the URL that we're going to monitor
        self.target = watchTarget
        
        # Parse the feed for the first time, this will be the baseline
        self.feed = feedparser.parse(self.target)
    
    def changes(self):
        # We already have the old feed in self.feed, pull an updated copy
        newFeed = feedparser.parse(self.target)
    
        # Get some blank lists
        old = []
        current = []
        changed = []
        
        # Populate them
        for items in self.feed.entries:
            old.append(items.updated)
        for items in newFeed.entries:
            current.append( (items.title,items.updated, items.link) )
        
        # Extract the changed items and bitly the links
        for title,time,link in current:
            if time not in old:
                import bitly
                changed.append(title, link)
        
        # Return them
        if changed:
            return changed
        else:
            return False
    
    def updateFeed(self):
        self.feed = feedparser.parse(self.target)
    
    def getPrettyOutput(self):
        
        # See if anything has changed
        titlesChanged = self.changes()
        
        #build the output string
        if len(titlesChanged) == 1:
            noun = 'post'
        else:
            noun = 'posts'
            
        outputString = '{} new forum {}: '.format( str(len(titlesChanged)),noun )
        
        for eachPost, eachLink in titlesChanged:
            
            # First, figure out if this is the final post
            finalPost = False
            if eachPost == titlesChanged[-1]:
                finalPost = True
            
            # Get rid of the "Reply To: " header at the beginning
            if eachPost.startswith("Reply To:"):
                newPost = eachPost.replace("Reply To:","")
            else:
                newPost = eachPost

            # Tack it on to the end of the output
            outputString += newPost
            
            # If this is not the final post
            if not finalPost:
                outputString += "....."
        
        return outputString


class youtubeWatcher:
    def __init__(self, watchTarget):
        # Get the YouTube username that we're going to monitor
        self.target = watchTarget
        
        # Pull the list of videos for the first time, this will be the baseline
        self.yService = gdata.youtube.service.YouTubeService()
        
        self.yURI = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % self.target
        
        self.feed = self.yService.GetYouTubeVideoFeed(self.yURI)
        
    
    def changes(self):
        #pull youtube feed again, this is the updated one
        currentYoutubeFeed = self.yService.GetYouTubeVideoFeed(self.yURI)
        
        # Get some blank lists
        old = []
        current = []
        changed = []
        
        # Populate them
        for items in self.feed.entry:
            old.append( str( items.GetSwfUrl() ).split("?")[0] )
        for items in currentYoutubeFeed.entry:
            current.append( (items.media.title.text, str( items.GetSwfUrl() ).split("?")[0], items.media.duration.seconds ) )
        
        # Extract the changed information
        for title,url,duration in current:
            if url not in old:
                changed.append( [title, url, duration] )
        
        # Return it
        if changed:
            return changed
        else:
            return False
    
    def updateFeed(self):
        self.feed = self.yService.GetYouTubeVideoFeed(self.yURI)
    
    def getPrettyOutput(self):
        
        # See if anything has changed
        titlesChanged = self.changes()
        
        #build the output string
        if len(titlesChanged) == 1:
            noun = 'video'
        else:
            noun = 'videos'

        outputString = '{} has posted {} new {}: '.format(self.target, str(len(titlesChanged)), noun)
        
        for eachTitle, eachURL, eachDuration in titlesChanged:
            formattedURL = eachURL.replace("http://www.youtube.com/v/","http://youtu.be/")
            
            unformattedTime = str(float(eachDuration) / 60.0)
            decimalTime = Decimal(str(unformattedTime)).quantize(Decimal('1.00'))
            formattedTime = "[" + str(decimalTime) + " min]"
            outputString += eachTitle
            outputString += formattedTime
            outputString += " "
            outputString += formattedURL
        
        # Output
        return outputString

def setup(phenny): 

    def monitor(phenny): 
        #set up the channel that messages will be transmitted to
        #FIXME
        #this should be read from a config file
        mainChannel = '#thegeekgroup'
        testChannel = '#tgg-bots'
        
        forum = rssWatcher("http://thegeekgroup.org/forums/feed")
        ytPhysicsduck = youtubeWatcher("physicsduck")
        ytThegeekgroup = youtubeWatcher("thegeekgroup")
        
        import time
        time.sleep(20)
        
        
        while True:
            #print("Executing feed check at: {}".format(time.strftime('%d %b %H:%MZ', time.gmtime() ) ) ) 
            
            if forum.changes():
                print( forum.getPrettyOutput() )
                phenny.msg(mainChannel, forum.getPrettyOutput())
                forum.updateFeed()
            
            if ytPhysicsduck.changes():
                print( ytPhysicsduck.getPrettyOutput() )
                phenny.msg(mainChannel, ytPhysicsduck.getPrettyOutput() )
                ytPhysicsduck.updateFeed()
            
            if ytThegeekgroup.changes(): 
                print( ytThegeekgroup.getPrettyOutput() )
                phenny.msg(mainChannel, ytThegeekgroup.getPrettyOutput() )
                ytThegeekgroup.updateFeed()
            
            #print("Feed check complete at: {}".format(time.strftime('%d %b %H:%MZ', time.gmtime() ) ) )
            time.sleep(60)

    targs = (phenny,)
    t = threading.Thread(target=monitor, args=targs)
    t.daemon = True
    t.start()



if __name__ == '__main__': 
    print __doc__.strip()





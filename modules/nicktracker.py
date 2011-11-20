#!/usr/bin/env python
"""
nicktracker.py - Phenny Nick Tracking Service Module
Copyright 2011, James Bliss, astro73.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""
import time, bot

storage = {} # Default value
# storage is a persistant value, automagically loaded and saved by the bot.

class CommandInput(bot.CommandInput):
    def __new__(cls, bot, text, origin, bytes, match, event, args):
        self = super(CommandInput, cls).__new__(cls, bot, text, origin, bytes, match, event, args)
        self.canonnick = bot.nicktracker.canonize(origin.nick)
        if hasattr(bot, 'nicktracker'):
            self.admin = self.canonnick in bot.config.admins
            self.owner = self.canonnick == bot.config.owner
        return self
        
class NickTracker(object):
    """
    The API for modules to access the nick database.
    """
    def __init__(self, phenny):
        self.phenny = phenny
    
    def canonize(self, nick):
        """nt.canonize(str) -> str
        Returns the canonical nick for the given nick, or the same if there isn't one.
        """
        return nick

def setup(phenny): 
    phenny.nicktracker = NickTracker(phenny)
    phenny.extendclass('CommandInput', CommandInput)

################
# NICKSERV ACC #
################

def nickserv_acc(phenny, input): 
    if input.sender != 'NickServ': return
    print "ACC:", repr(input)
nickserv_acc.rule = r'(.*) ACC ([0123])(?: \((.*)\))?'
nickserv_acc.event = 'NOTICE'
nickserv_acc.priority = 'low'


#################
# NICKSERV INFO #
#################

tmp_info = None

def nickserv_info_begin(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    print "INFO Begin:", repr(input)
    tmp_info = {
        '__nick__': input.group(1),
        '__user__': input.group(2),
        }
nickserv_info_begin.rule = r'Information on \x02(.*?)\x02 \(account \x02(.*?)\x02\)'
nickserv_info_begin.event = 'NOTICE'
nickserv_info_begin.priority = 'low'
nickserv_info_begin.thread = False

def nickserv_info_body(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    if tmp_info is None: return
    print "INFO Body:", repr(input)
    tmp_info[input.group(1)] = input.group(2)
nickserv_info_body.rule = r'(.+?) *: +(.+)'
nickserv_info_body.event = 'NOTICE'
nickserv_info_body.priority = 'low'
nickserv_info_body.thread = False

def nickserv_info_finish(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    if tmp_info is None: return
    print "INFO Finish:", repr(input)
    print "INFO:", repr(tmp_info)
    tmp_info = None
nickserv_info_finish.rule = r'\*\*\* \x02End of Info\x02 \*\*\*'
nickserv_info_finish.event = 'NOTICE'
nickserv_info_finish.priority = 'low'
nickserv_info_finish.thread = True

#####################
# NICKSERV TAXONOMY #
#####################

tmp_taxo = None

def nickserv_taxonomy_begin(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    print "TAXONOMY Begin:", repr(input)
    tmp_taxo = {
        '__user__': input.group(1),
        }
nickserv_taxonomy_begin.rule = r'Taxonomy for \x02(.*)\x02:'
nickserv_taxonomy_begin.event = 'NOTICE'
nickserv_taxonomy_begin.priority = 'low'
nickserv_taxonomy_begin.thread = False

def nickserv_taxonomy_body(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    if tmp_taxo is None: return
    print "TAXONOMY Body:", repr(input)
    tmp_taxo[input.group(1)] = input.group(2)
nickserv_taxonomy_body.rule = r'(.+?) *: +(.+)'
nickserv_taxonomy_body.event = 'NOTICE'
nickserv_taxonomy_body.priority = 'low'
nickserv_taxonomy_body.thread = False

def nickserv_taxonomy_finish(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    if tmp_taxo is None: return
    print "TAXONOMY Finish:", repr(input)
    assert tmp_taxo['__user__'] == input.group(1)
    print "TAXONOMY:", repr(tmp_taxo)
    tmp_taxo = None
nickserv_taxonomy_finish.rule = r'End of \x02(.*?)\x02 taxonomy.'
nickserv_taxonomy_finish.event = 'NOTICE'
nickserv_taxonomy_finish.priority = 'low'
nickserv_taxonomy_finish.thread = True

############
# TRIGGERS #
############

def query_acc(phenny, nick):
    phenny.msg('Nickserv', 'ACC %s' % nick)

def query_info(phenny, nick):
    phenny.msg('Nickserv', 'INFO %s' % nick)

def query_taxonomy(phenny, nick):
    phenny.msg('Nickserv', 'TAXONOMY %s' % nick)

def cmd_acc(phenny, input):
    query_acc(phenny, input.nick)
cmd_acc.commands = ['acc']

def cmd_info(phenny, input):
    query_info(phenny, input.nick)
cmd_info.commands = ['ninfo']

def cmd_taxonomy(phenny, input):
    query_taxonomy(phenny, input.nick)
cmd_taxonomy.commands = ['taxo']

if __name__ == '__main__': 
   print __doc__.strip()

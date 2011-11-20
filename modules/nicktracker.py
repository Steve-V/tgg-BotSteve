#!/usr/bin/env python
"""
nicktracker.py - Phenny Nick Tracking Service Module
Copyright 2011, James Bliss, astro73.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""
import time, bot, re, datetime, threading

storage = {} # Default value
# storage is a persistant value, automagically loaded and saved by the bot.

OFFLINE, LOGGEDOUT, RECOGNIZED, LOGGEDIN = range(4)

def checkreserved(phenny, nick):
    # The server we're connected to
    if nick.endswith('.freenode.net'): #FIXME: Don't hardcode this
        return True
    # Services
    elif nick.lower().endswith('serv'):
        return True
    # And Ourself
    elif nick.lower() == phenny.nick:
        return True
    else:
        return False

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
        self.nicks = {}
        self.accounts = {}
    
    def canonize(self, nick):
        """nt.canonize(str) -> str
        Returns the canonical nick for the given nick, or the same if there isn't one.
        """
        global storage
        
        if checkreserved(self.phenny, nick):
            return nick
        try:
            data = self.nicks[nick]
        except KeyError:
            query_acc(self.phenny, nick)
            return nick
        else:
            if data['account']:
                if data['account'] not in storage:
                    # If we have the account, but not the info, query it.
                    query_info(self.phenny, nick)
            else:
                if data['status'] != OFFLINE or data['detail'] == 'offline':
                    query_info(self.phenny, nick)
            if data['status'] in (RECOGNIZED, LOGGEDIN):
                if data['account']:
                    return data['account']
                else:
                    return nick
            else:
                return nick
    
    def _updatelive(self, account, nick, status, detail=None):
        # Update nick index
        try:
            data = self.nicks[nick]
        except KeyError:
            self.nicks[nick] = data = {
                'account': account,
                'nick': nick,
                'status': status,
                'detail': detail,
                }
        else:
            if status is None:
                # From _updateinfo
                if data['status'] in (RECOGNIZED, LOGGEDIN):
                    data['account'] = account
            else:
                data['status'] = status
                data['detail'] = detail
        
        # Update account index
        if account is None:
            account = data['account']
        if status in (RECOGNIZED, LOGGEDIN):
            self.accounts.setdefault(account, []).append(nick)
        else:
            try:
                self.accounts[account].remove(nick)
            except KeyError, ValueError:
                pass
    
    def _updateinfo(self, data):
        global storage
        storage[data.account] = data.items
        if data.nick is not None:
            self._updatelive(data.account, data.nick, None)
    
    def _updatetaxo(self, data):
        global storage
        d = storage[data.account]
        d['Metadata'] = data.items
        storage[data.account] = d

def setup(phenny): 
    phenny.nicktracker = NickTracker(phenny)
    phenny.extendclass('CommandInput', CommandInput)
    t = threading.Thread(target=processlist, args=(phenny,))
    t.daemon = True
    t.start()

nicks_to_process = set()

def processlist(phenny):
    while True:
        try:
            nick = nicks_to_process.pop()
        except KeyError:
            pass
        else:
            query_acc(phenny, nick)
        time.sleep(10)

###################
# QUERY FUNCTIONS #
###################

def query_acc(phenny, nick):
    if checkreserved(phenny, nick):
        return
    nicks_to_process.discard(nick)
    phenny.msg('Nickserv', 'ACC %s' % nick)

def query_info(phenny, nick):
    if checkreserved(phenny, nick):
        return
    if nick.lower() not in info_queried_nicks: # Prevent repeated queries
        info_queried_nicks.add(nick.lower())
        phenny.msg('Nickserv', 'INFO %s' % nick)

def query_taxonomy(phenny, nick):
    if checkreserved(phenny, nick):
        return
    phenny.msg('Nickserv', 'TAXONOMY %s' % nick)

############
# TRIGGERS #
############

def trigger_join(phenny, input):
    print "Join:", repr(input)
    if checkreserved(phenny, input.nick): return
    acc_retry = True
    query_acc(phenny, input.nick)
trigger_join.rule = r'(.*)'
trigger_join.event = 'JOIN'
trigger_join.priority = 'low'

def trigger_list(phenny, input):
    print "List:", repr(input)
    
    for nick in input.split(' '):
        if nick[0] in '@+':
            nick = nick[1:]
        if checkreserved(phenny, nick):
            continue
        nicks_to_process.add(nick)
    
    print "List:", nicks_to_process
trigger_list.rule = r'(.*)'
trigger_list.event = '353'
trigger_list.priority = 'low'

def trigger_part(phenny, input):
    nicks_to_process.discard(input.nick)
trigger_part.rule = r'(.*)'
trigger_part.event = 'PART'
trigger_part.priority = 'low'

#################
# TEST COMMANDS #
#################

def cmd_acc(phenny, input):
    query_acc(phenny, input.group(2) or input.nick)
cmd_acc.commands = ['acc']

def cmd_info(phenny, input):
    query_info(phenny, input.group(2) or input.nick)
cmd_info.commands = ['ninfo']

def cmd_taxonomy(phenny, input):
    query_taxonomy(phenny, input.group(2) or input.nick)
cmd_taxonomy.commands = ['taxo']

################
# DATA HELPERS #
################

class DataHolder(object):
    def __init__(self, account, nick=None):
        self.account = account
        self.nick = nick
        self.items = {}
    
    def __repr__(self):
        n = ""
        if self.nick is not None:
            n = "n=%r " % self.nick
        return "<DataHolder u=%r %s%r>" % (self.account, n, self.items)

DATE = re.compile(r"(.+) (\d+) (\d+):(\d+):(\d+) (\d+) \(.*\)")
def parsedate(d):
    m = DATE.match(d)
    if m is None:
        raise ValueError
    
    month, day, hour, minute, second, year = m.groups()
    
    year = int(year)
    month = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(month)
    day = int(day)
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return time.mktime(dt.timetuple())

################
# NICKSERV ACC #
################

acc_retry = False

def nickserv_acc(phenny, input): 
    global acc_retry
    if input.sender != 'NickServ': return
    
    print "ACC:", repr(input)
    
    nick = input.group(1)
    status = int(input.group(2))
    detail = input.group(3) # None, 'offline', or 'not registered'
    
    if nick == '*': return # Special nick
    
    phenny.nicktracker._updatelive(None, nick, status, detail)
    if status in (RECOGNIZED, LOGGEDIN):
        query_info(phenny, nick)
    elif acc_retry:
        acc_retry = False
        time.sleep(60) #Based on the length of NickServ's enforcement.
        query_acc(phenny, nick)
nickserv_acc.rule = r'(.*) ACC ([0123])(?: \((.*)\))?'
nickserv_acc.event = 'NOTICE'
nickserv_acc.priority = 'low'


#################
# NICKSERV INFO #
#################

tmp_info = None
info_queried_nicks = set()

def nickserv_info_begin(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    
    print "INFO Begin:", repr(input)
    
    if input.group(2):
        nick, account = input.groups()
    else:
        nick = account = input.groups()
    tmp_info = DataHolder(account, nick)
nickserv_info_begin.rule = r'Information on \x02(.*?)\x02(?: \(account \x02(.*?)\x02\))?:'
nickserv_info_begin.event = 'NOTICE'
nickserv_info_begin.priority = 'low'
nickserv_info_begin.thread = False

def nickserv_info_body(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    if tmp_info is None: return
    
    print "INFO Body:", repr(input)
    
    k, v = input.group(1,2)
    if k == 'Metadata':
        mk, mv = v.split('=')
        mk = mk.strip()
        mv = mv.strip()
        if 'Metadata' in tmp_info.items:
            tmp_info.items['Metadata'][mk] = mv
        else:
            tmp_info.items['Metadata'] = {mk:mv}
    elif k in ('User reg.', 'Registered'):
        tmp_info.items[k] = parsedate(v)
    elif k == 'Last seen':
        if v != 'now':
            try:
                v = parsedate(v)
            except ValueError:
                return # Private set
        tmp_info.items[k] = v
    elif k == 'Flags':
        tmp_info.items[k] = [f.strip() for f in v.split(',')]
    else:
        tmp_info.items[k] = v
nickserv_info_body.rule = r'(.+?) *: +(.+)'
nickserv_info_body.event = 'NOTICE'
nickserv_info_body.priority = 'low'
nickserv_info_body.thread = False

def nickserv_info_protection(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    if tmp_info is None: return
    
    print "INFO Protection:", repr(input)
    assert tmp_info.account == input.group(1)
    tmp_info.items['__protection__'] = True
nickserv_info_protection.rule = r'(.+?) has enabled nick protection'
nickserv_info_protection.event = 'NOTICE'
nickserv_info_protection.priority = 'low'
nickserv_info_protection.thread = False

def nickserv_info_finish(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    if tmp_info is None: return
    
    print "INFO Finish:", repr(input)
    print "INFO:", repr(tmp_info)
    
    info_queried_nicks.remove(tmp_info.nick.lower())
    phenny.nicktracker._updateinfo(tmp_info)
    
    tmp_info = None
nickserv_info_finish.rule = r'\*\*\* \x02End of Info\x02 \*\*\*'
nickserv_info_finish.event = 'NOTICE'
nickserv_info_finish.priority = 'low'
nickserv_info_finish.thread = True

#####################
# NICKSERV TAXONOMY #
#####################

# Note: This isn't strictly required, but it's good to be complete.

tmp_taxo = None

def nickserv_taxonomy_begin(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    
    print "TAXONOMY Begin:", repr(input)
    
    tmp_taxo = DataHolder(input.group(1))
nickserv_taxonomy_begin.rule = r'Taxonomy for \x02(.*)\x02:'
nickserv_taxonomy_begin.event = 'NOTICE'
nickserv_taxonomy_begin.priority = 'low'
nickserv_taxonomy_begin.thread = False

def nickserv_taxonomy_body(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    if tmp_taxo is None: return
    
    print "TAXONOMY Body:", repr(input)
    
    tmp_taxo.items[input.group(1)] = input.group(2)
nickserv_taxonomy_body.rule = r'(.+?) *: +(.+)'
nickserv_taxonomy_body.event = 'NOTICE'
nickserv_taxonomy_body.priority = 'low'
nickserv_taxonomy_body.thread = False

def nickserv_taxonomy_finish(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    if tmp_taxo is None: return
    
    print "TAXONOMY Finish:", repr(input)
    print "TAXONOMY:", repr(tmp_taxo)
    
    assert tmp_taxo.account == input.group(1)
    
    phenny.nicktracker._updatetaxo(tmp_taxo)
    tmp_taxo = None
nickserv_taxonomy_finish.rule = r'End of \x02(.*?)\x02 taxonomy.'
nickserv_taxonomy_finish.event = 'NOTICE'
nickserv_taxonomy_finish.priority = 'low'
nickserv_taxonomy_finish.thread = True

if __name__ == '__main__': 
   print __doc__.strip()

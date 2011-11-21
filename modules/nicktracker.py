#!/usr/bin/env python
"""
nicktracker.py - Phenny Nick Tracking Service Module
Copyright 2011, James Bliss, astro73.com
Licensed under the Eiffel Forum License 2.
"""
#TODO: Users of identified nicks start with a '~'. How can we use this?
#TODO: Add a daemon to update nicks, accounts, and registrations, even those offline.
from __future__ import absolute_import
import time, bot, re, datetime, event
from tools import TimeTrackDict, startdaemon
storage = {} # This is used to store the data from INFO

# Default expiry time, also configurable.
DATA_EXPIRY_TIME = 30*60 # 30 minutes

ACC_OFFLINE, ACC_LOGGEDOUT, ACC_RECOGNIZED, ACC_LOGGEDIN = range(4)
ACCD_OFFLINE, ACCD_UNREGISTERED = 'offline', 'not registered'

UNREGISTERED, OFFLINE, LOGGEDOUT, RECOGNIZED, LOGGEDIN = range(-2, 3)
# Note: Status > 0 means they're sufficiently recognzied for us.

ACC_MAP = {
    (ACC_OFFLINE, ACCD_OFFLINE) : OFFLINE,
    (ACC_OFFLINE, ACCD_UNREGISTERED) : UNREGISTERED,
    (ACC_LOGGEDOUT, None) : LOGGEDOUT,
    (ACC_RECOGNIZED, None) : RECOGNIZED,
    (ACC_LOGGEDIN, None) : LOGGEDIN,
    }

STATUS_TEXT = {
    UNREGISTERED: 'UNREGISTERED',
    OFFLINE: 'OFFLINE',
    LOGGEDOUT: 'LOGGEDOUT',
    RECOGNIZED: 'RECOGNIZED',
    LOGGEDIN: 'LOGGEDIN',
    }

def checkreserved(phenny, nick):
    """
    Just checks the nick against a set of nicks that we shouldn't query.
    
    This is things like servers, services, and ourselves.
    """
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
    """
    Overrides CommandInput so that we use the canonical nick for access.
    """
    def __new__(cls, bot, text, origin, bytes, match, event, args):
        self = super(CommandInput, cls).__new__(cls, bot, text, origin, bytes, match, event, args)
        self.canonnick = None
        if hasattr(bot, 'nicktracker'):
            account, status = bot.nicktracker.getaccount(origin.nick)
            if account and status > 0:
                self.canonnick = account
                self.admin = self.canonnick.lower() in [a.lower() for a in bot.config.admins]
                self.owner = self.canonnick.lower() == bot.config.owner.lower()
        return self

class NickTracker(event.EventSource):
    """
    The API for modules to access the nick database.
    
    Events defined:
     * have-account: nick, account, status
       This is called whenever the account/status information is updated and we 
       have the account.
    """
    # This is used to store the nick<->accounts mapping
    nicks = None # A dict: {nick.lower() : {'nick': nick, 'account': account, 'status': UNREGISTERED..LOGGEDIN }, ...}
    accounts = None # A dict: { account.lower() : set(nick.lower(), ...), ...}
    
    def __init__(self, phenny):
        super(NickTracker, self).__init__()
        self.phenny = phenny
        expiry = DATA_EXPIRY_TIME
        if hasattr(phenny.config, 'nicktracker'):
            expiry = phenny.config.nicktracker.get('expiry', expiry)
        self.nicks = TimeTrackDict(self._expire_nick, expiry)
        self.accounts = TimeTrackDict(self._expire_account, expiry)
    
    def getaccount(self, nick):
        """nt.getaccount(str) -> str|None, int|None
        Returns the canonical nick (account name) and status for the given nick.
        """
        global storage
        
        if checkreserved(self.phenny, nick):
            # If it's a reserved nick, just return it
            return nick, LOGGEDIN
        
        try:
            data = self.nicks[nick.lower()]
        except KeyError:
            # If we don't have that data, query for it so we can use it in the future.
            query_acc(self.phenny, nick)
            return nick, None
        else:
            # If the account information isn't available, query for it.
            if data['account']:
                if data['account'].lower() not in storage:
                    # If we have the account, but not the info, query it.
                    query_info(self.phenny, nick)
            else:
                if data['status'] != UNREGISTERED:
                    query_info(self.phenny, nick)
            
            # Actually do the canonization
            if data['status'] > 0:
                # The user is considered identified enough.
                return data['account'], data['status']
            else:
                # Not considered identified
                return None, data['status']
    
    def canonize(self, nick):
        """nt.canonize(str) -> str
        Returns the canonical nick for the given nick, or the same if there isn't one.
        """
        rv = self.getaccount(nick)[0]
        if rv is None:
            return nick
        else:
            return rv
    
    def getalts(self, nick):
        """nt.getalts(str) -> [str], [str]
        Returns the other nicks to the given user. The first list is the nicks 
        that are known to be that user. The second list is the nicks that we 
        haven't seen, but are registered to them.
        """
        account, status = self.getaccount(nick)
        if account is None or status <= 0:
            return [], []
        return list(self.accounts[account.lower()]), []
    
    def _changenick(self, old, new):
        """
        Update information to reflect the nick change.
        """
        if old.lower() not in self.nicks:
            # Not a nick we're currently tracking. Should only happen when entering.
            return
        # Update nick->account
        account = self.nicks[new.lower()] = self.nicks[old.lower()]
        del self.nicks[old.lower()]
        if account['account']:
            account = account['account'].lower()
            # Update account->nick
            self.accounts[account].add(new.lower())
            self.accounts[account].discard(old.lower())
    
    def _updatelive(self, account, nick, status):
        """
        Update nick/account mapping
        """
        # Update nick->account
        try:
            data = self.nicks[nick.lower()]
        except KeyError:
            self.nicks[nick.lower()] = data = {
                'nick': nick,
                'account': account,
                'status': status,
                }
        else:
            if data['account'] and account and data['account'].lower() != account.lower():
                # If we're changing accounts, make sure the nick gets removed from the old one
                try:
                    self.accounts[data['account'].lower()].discard(nick.lower())
                except KeyError:
                    pass
            
            if status is None:
                # Called by _updateinfo
                if data['status'] > 0:
                    data['account'] = account
            else:
                # Called by nickserv_acc
                data['status'] = status
        
        # Update account->nicks
        if account is None:
            account = data['account']
        if account is None:
            if data['status'] > 0:
                query_info(self.phenny, nick)
            return
        if status > 0:
            print "Add nick: %r %r" % (account, nick)
            self.accounts.setdefault(account.lower(), set()).add(nick.lower())
        else:
            try:
                self.accounts[account.lower()].discard(nick.lower())
            except KeyError:
                pass
        
        if data['status'] > 0 and data['account']:
            self.emit('have-account', nick, data['account'], status)
    
    def _removeaccount(self, account):
        laccount = account.lower()
        if laccount not in self._accounts:
            return
        nicks = self.accounts[laccount]
        del self.accounts[laccount]
        nicks.add(laccount)
        for nick in nicks:
            if nick not in self.nicks: continue
            self.nicks[nick]['account'] = None
            self.nicks[nick]['status'] = UNREGISTERED
            nicks_to_process.add(nick)
    
    def _updateinfo(self, data):
        """
        Update the data from an INFO query.
        """
        global storage
        storage[data.account.lower()] = data.items
        
        if data.nick is not None:
            # Update the nick/account mapping with the account/nick data
            self._updatelive(data.account, data.nick, None)
    
    def _updatetaxo(self, data):
        """
        Update the data from an TAXONOMY query.
        """
        global storage
        d = storage[data.account.lower()]
        d['Metadata'] = data.items
        storage[data.account.lower()] = d
    
    def _expire_nick(self, ttd, key, age):
        print "Expire: Nick: %r" % key
        startdaemon(query_acc, self.phenny, key)
    
    def _expire_account(self, ttd, key, age):
        print "Expire: Account: %r" % key
        # We should be querying the nicks on this one
        startdaemon(query_info, self.phenny, key)

def setup(phenny): 
    phenny.nicktracker = NickTracker(phenny)
    phenny.extendclass('CommandInput', CommandInput)
    startdaemon(processlist, phenny)

# The nick process queue. So that we don't flood nickserv when we connect, we do initial loads gradually over time.
nicks_to_process = set()
def processlist(phenny):
    while True:
        try:
            nick = nicks_to_process.pop()
        except KeyError:
            pass
        else:
            query_acc(phenny, nick)
        time.sleep(5) # The guideline is one message every 2 seconds, and irc.py enforces 3.

############
# TRIGGERS #
############
# Stuff we do when things happen

def trigger_nick(phenny, input):
    """
    When someone changes nicks, update the information
    """
    old = input.nick
    new = unicode(input)
    print "Nick: %s -> %s" % (old, new)
    # Update the database
    phenny.nicktracker._changenick(old, new)
    
    # Update the processing queue
    try:
        nicks_to_process.remove(old.lower())
    except KeyError:
        pass
    else:
        nicks_to_process.add(new.lower())
trigger_nick.rule = r'(.*)'
trigger_nick.event = 'NICK'
trigger_nick.priority = 'low'

nick_host = {}

def trigger_join(phenny, input):
    """
    When someone joins our channel, query them
    """
    global nick_host
    print "Join:", repr(input)
    nick_host[input.nick] = (input.origin.user, input.origin.host)
    if checkreserved(phenny, input.nick): return
    query_acc(phenny, input.nick, retry=True)
trigger_join.rule = r'(.*)'
trigger_join.event = 'JOIN'
trigger_join.priority = 'low'

def trigger_list(phenny, input):
    """
    When we join a channel, schedule queries for existing members
    """
    print "List:", repr(input)
    
    for nick in input.split(' '):
        if nick[0] in '@+':
            nick = nick[1:]
        if checkreserved(phenny, nick):
            continue
        nicks_to_process.add(nick.lower())
    
    print "List:", nicks_to_process
trigger_list.rule = r'(.*)'
trigger_list.event = '353'
trigger_list.priority = 'low'

def trigger_part(phenny, input):
    """
    If somebody leaves, do a status update.
    """
    nicks_to_process.add(input.nick.lower())
trigger_part.rule = r'(.*)'
trigger_part.event = 'PART'
trigger_part.priority = 'low'

def trigger_quit(phenny, input):
    """
    If somebody leaves, do a status update.
    """
    nicks_to_process.add(input.nick.lower())
trigger_part.rule = r'(.*)'
trigger_part.event = 'QUIT'
trigger_part.priority = 'low'

#################
# TEST COMMANDS #
#################

def cmd_nickhost(phenny, input):
    from pprint import pprint
    pprint(nick_host)
cmd_nickhost.commands = ['nickhost']

def cmd_acc(phenny, input):
    query_acc(phenny, input.group(2) or input.nick)
cmd_acc.commands = ['acc']

def cmd_info(phenny, input):
    query_info(phenny, input.group(2) or input.nick)
cmd_info.commands = ['ninfo']

def cmd_taxonomy(phenny, input):
    query_taxonomy(phenny, input.group(2) or input.nick)
cmd_taxonomy.commands = ['taxo']

def cmd_canon(phenny, input):
    print "Canon: %r" % input
    nick = input.group(2) or input.nick
    phenny.reply(phenny.nicktracker.canonize(nick))
cmd_canon.commands = ['canon']

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
    
    def __unicode__(self):
        if self.nick is None:
            return u"(%s): %r" % (self.account, self.items)
        else:
            return u"%s (%s): %r" % (self.nick, self.account, self.items)
    
    def __str__(self):
        return str(unicode(self))

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

acc_retry = set()
acc_queried_nicks = set()

def query_acc(phenny, nick, retry=False, noacct=False):
    if nick == '*': return # Special nick that causes less-than-useful output
    # Don't query ourselves, NickServ, or servers
    if checkreserved(phenny, nick):
        return
    lnick = nick.lower()
    if lnick in acc_queried_nicks: return
    nicks_to_process.discard(lnick) # Remove this nick from the processing queue
    acc_queried_nicks.add(lnick)
    if retry:
        acc_retry.add(lnick)
    if noacct:
        phenny.msg('Nickserv', 'ACC %s' % nick)
    else:
        phenny.msg('Nickserv', 'ACC %s *' % nick)

def nickserv_acc(phenny, input): 
    global acc_retry
    if input.sender != 'NickServ': return
    nick = input.group(1)
    lnick = nick.lower()
    account = input.group(2)
    status = ACC_MAP[(int(input.group(3)), input.group(4))]
    
    acc_queried_nicks.discard(lnick)
    if account == '*':
        if status == OFFLINE:
            account = None
        elif status == UNREGISTERED:
            # Possible that it's actually LOGGEDOUT
            query_acc(phenny, nick, noacct=True) # We don't need to repass retry because we're not removing it.
            return
    
    print "ACC: %s (%s): %s" % (nick, account, STATUS_TEXT.get(status, status))
    
    phenny.nicktracker._updatelive(account, nick, status)
    if status > 0:
        query_info(phenny, nick)
        acc_retry.discard(lnick)
    elif lnick in acc_retry:
        acc_retry.remove(lnick)
        time.sleep(60) #Based on the length of NickServ's enforcement.
        query_acc(phenny, nick)
nickserv_acc.rule = r'([^ ]*)(?: -> ([^ ]*))? ACC ([0123])(?: \((.*)\))?'
nickserv_acc.event = 'NOTICE'
nickserv_acc.priority = 'low'
nickserv_acc.thread = True


#################
# NICKSERV INFO #
#################

tmp_info = None
info_queried_nicks = set()

def query_info(phenny, nick):
    # Don't query ourselves, NickServ, or servers
    if checkreserved(phenny, nick):
        return
    if nick.lower() not in info_queried_nicks: # Prevent repeated queries
        info_queried_nicks.add(nick.lower())
        phenny.msg('Nickserv', 'INFO %s' % nick)

def nickserv_info_begin(phenny, input): 
    global tmp_info
    if input.sender != 'NickServ': return
    
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
    
    print "INFO:", tmp_info
    
    info_queried_nicks.remove(tmp_info.nick.lower())
    phenny.nicktracker._updateinfo(tmp_info)
    
    tmp_info = None
nickserv_info_finish.rule = r'\*\*\* \x02End of Info\x02 \*\*\*'
nickserv_info_finish.event = 'NOTICE'
nickserv_info_finish.priority = 'low'
nickserv_info_finish.thread = True

def nickserv_info_notregistered(phenny, input):
    if input.sender != 'NickServ': return
    
    nick = input.group(1)
    print "INFO: Not Registered:", nick
    info_queried_nicks.remove(nick.lower())
    phenny.nicktracker._removeaccount(nick)
nickserv_info_notregistered.rule = r'\x02(.*)\x02 is not registered\.'
nickserv_info_notregistered.event = 'NOTICE'
nickserv_info_notregistered.priority = 'low'
nickserv_info_notregistered.thread = True

def nickserv_info_marked(phenny, input):
    if input.sender != 'NickServ': return
    
    nick, setter, date, reason = input.groups()
    print "INFO: Marked: %s (%s): by %s on %s" % (nick, reason, setter, date)
    info_queried_nicks.remove(nick.lower())
    phenny.nicktracker._removeaccount(nick)
nickserv_info_marked.rule = r"\x02(.+)\x02 is not registered anymore, but was marked by (.+) on (.+) \((.+)\)\."
nickserv_info_marked.event = 'NOTICE'
nickserv_info_marked.priority = 'low'
nickserv_info_marked.thread = True


#####################
# NICKSERV TAXONOMY #
#####################

# Note: This isn't strictly required, but it's good to be complete.

tmp_taxo = None

def query_taxonomy(phenny, nick):
    if checkreserved(phenny, nick):
        return
    phenny.msg('Nickserv', 'TAXONOMY %s' % nick)

def nickserv_taxonomy_begin(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    
    tmp_taxo = DataHolder(input.group(1))
nickserv_taxonomy_begin.rule = r'Taxonomy for \x02(.*)\x02:'
nickserv_taxonomy_begin.event = 'NOTICE'
nickserv_taxonomy_begin.priority = 'low'
nickserv_taxonomy_begin.thread = False

def nickserv_taxonomy_body(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    if tmp_taxo is None: return
    
    tmp_taxo.items[input.group(1)] = input.group(2)
nickserv_taxonomy_body.rule = r'(.+?) *: +(.+)'
nickserv_taxonomy_body.event = 'NOTICE'
nickserv_taxonomy_body.priority = 'low'
nickserv_taxonomy_body.thread = False

def nickserv_taxonomy_finish(phenny, input): 
    global tmp_taxo
    if input.sender != 'NickServ': return
    if tmp_taxo is None: return
    
    print "TAXONOMY:", tmp_taxo
    
    assert tmp_taxo.account == input.group(1)
    
    phenny.nicktracker._updatetaxo(tmp_taxo)
    tmp_taxo = None
nickserv_taxonomy_finish.rule = r'End of \x02(.*?)\x02 taxonomy.'
nickserv_taxonomy_finish.event = 'NOTICE'
nickserv_taxonomy_finish.priority = 'low'
nickserv_taxonomy_finish.thread = True

if __name__ == '__main__': 
   print __doc__.strip()

#!/usr/bin/env python
"""
admin.py - Phenny Admin Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.
mod.py - Channel Module
Author: Alek Rollyson, http://opensource.osu.edu/
Jenni (about): http://inamidst.com/phenny/

Beefed up by Alek Rollyson. added functions for op, deop, voice, devoice
Uses NickServ ACC to verify that a nick is identified with services, as well
as m5's admin list as a double verification system. Should eliminate the possibility
of nick spoofing. May only work with freenode, hasn't been tested on other networks.

Forked by Michael S. Yanovich, http://opensource.osu.edu/~yanovich/
http://inamidst.com/phenny/
"""

import re, time, sched

auth_list = []
admins = []

def join(phenny, input): 
  """Join the specified channel. This is an admin-only command."""
  # Can only be done in privmsg by an admin
  if input.sender.startswith('#'): return
  if input.admin: 
    channel, key = input.group(1), input.group(2)
    if not key: 
      phenny.write(['JOIN'], channel)
    else: phenny.write(['JOIN', channel, key])
join.rule = r'\.join (#\S+)(?: *(\S+))?'
join.priority = 'low'
join.example = '.join #example or .join #example key'

def part(phenny, input): 
  """Part the specified channel. This is an admin-only command."""
  # Can only be done in privmsg by an admin
  if input.sender.startswith('#'): return
  if input.admin:
    phenny.write(['PART', input.group(2)])
part.commands = ['part']
part.priority = 'low'
part.example = '.part #example'

def quit(phenny, input): 
  """Quit from the server. This is an owner-only command."""
  # Can only be done in privmsg by the owner
  if input.sender.startswith('#'): return
  if input.owner: 
    phenny.write(['QUIT'])
    __import__('sys').exit(0)
quit.commands = ['quit']
quit.priority = 'low'

def msg(phenny, input): 
  # Can only be done in privmsg by an admin
  if input.sender.startswith('#'): return
  a, b = input.group(2), input.group(3)
  if (not a) or (not b): return
  if input.admin: 
    phenny.msg(a, b)
msg.rule = (['msg'], r'(#?\S+) (.+)')
msg.priority = 'low'

def me(phenny, input): 
  # Can only be done in privmsg by an admin
  if input.sender.startswith('#'): return
  if input.admin: 
    msg = '\x01ACTION %s\x01' % input.group(3)
    phenny.msg(input.group(2), msg)
me.rule = (['me', 'ME', 'Me', 'mE'], r'(#?\S+) (.*)')
me.priority = 'low'

def op(phenny, input):
  """
  Command to op users in a room. If no nick is given,
  phenny will op the nick who sent the command
  """
  if not input.admin or not input.sender.startswith('#'):
    return
  nick = input.group(2)
  verify = auth_check(phenny, input.nick, nick)
  if verify:
    channel = input.sender
    if not nick:
      nick = input.nick
    phenny.write(['MODE', channel, "+o", nick])
op.rule = (['op'], r'(\S+)?')
op.priority = 'low'

def deop(phenny, input):
  """
  Command to deop users in a room. If no nick is given,
  phenny will deop the nick who sent the command
  """
  if not input.admin or not input.sender.startswith('#'):
    return
  nick = input.group(2)
  verify = auth_check(phenny, input.nick, nick)
  if verify:
    channel = input.sender
    if not nick:
      nick = input.nick
    phenny.write(['MODE', channel, "-o", nick])
deop.rule = (['deop'], r'(\S+)?')
deop.priority = 'low'

def voice(phenny, input):
  """
  Command to voice users in a room. If no nick is given,
  phenny will voice the nick who sent the command
  """
  if not input.admin:
    return phenny.say("Not an admin!")
  if not input.sender.startswith('#'):
    return phenny.say("Command must be given in channel!")
  nick = input.group(2)
  verify = auth_check(phenny, input.nick, nick)
  if verify:
    channel = input.sender
    if not nick:
      nick = input.nick
    phenny.write(['MODE', channel, "+v", nick])
  else:
    phenny.say("Nick not verified")
voice.rule = (['voice'], r'(\S+)?')
voice.priority = 'low'

def devoice(phenny, input):
  """
  Command to devoice users in a room. If no nick is given,
  phenny will devoice the nick who sent the command
  """
  if not input.admin or not input.sender.startswith('#'):
    return
  nick = input.group(2)
  verify = auth_check(phenny, input.nick, nick)
  if verify:
    channel = input.sender
    if not nick:
      nick = input.nick
    phenny.write(['MODE', channel, "-v", nick])
devoice.rule = (['devoice'], r'(\S+)?')
devoice.priority = 'low'

def auth_request(phenny, input):
  """
  This will scan every message in a room for nicks in phenny's
  admin list.  If one is found, it will send an ACC request
  to NickServ.  May only work with Freenode.
  """
  admins = phenny.config.admins
  pattern = '(' + '|'.join([re.escape(x) for x in admins]) + ')'
  matches = re.findall(pattern, input)
  for x in matches:
    phenny.msg('NickServ', 'ACC ' + x)
auth_request.rule = r'.*'
auth_request.priority = 'high'

def auth_verify(phenny, input):
  """
  This will wait for notices from NickServ and scan for ACC
  responses.  This verifies with NickServ that nicks in the room
  are identified with NickServ so that they cannot be spoofed.
  May only work with freenode.
  """
  global auth_list
  nick = input.group(1)
  level = input.group(3)
  if input.nick != 'NickServ':
    return
  elif level == '3':
    if nick in auth_list:
      return
    else:
      auth_list.append(nick)
  else:
    if nick not in auth_list:
      return
    else:
      auth_list.remove(nick)
auth_verify.event = 'NOTICE'
auth_verify.rule = r'(\S+) (ACC) ([0-3])'
auth_verify.priority = 'high'

def auth_check(phenny, nick, target=None):
  """
  Checks if nick is on the auth list and returns true if so
  """
  global auth_list
  if target == phenny.config.nick:
    return 0
  elif nick in auth_list:
    return 1

def deauth(nick):
  """
  Remove pepole from the deauth list.
  """
  global auth_list
  if nick in auth_list:
    a = auth_list.index(nick)
    del(auth_list[a])

def deauth_quit(phenny, input):
  deauth(input.nick)
deauth_quit.event = 'QUIT'
deauth_quit.rule = '.*'

def deauth_part(phenny, input):
  deauth(input.nick)
deauth_part.event = 'PART'
deauth_part.rule = '.*'

def deauth_nick(phenny, input):
  deauth(input.nick)
deauth_nick.event = 'NICK'
deauth_nick.rule = '.*'

def kick(phenny, input):
  if not input.admin: return
  text = input.group().split()
  argc = len(text)
  if argc < 2: return
  opt = text[1]
  nick = opt
  channel = input.sender
  reasonidx = 2
  if opt.startswith('#'):
    if argc < 3: return
    nick = text[2]
    channel = opt
    reasonidx = 3
  reason = ' '.join(text[reasonidx:])
  if nick != phenny.config.nick:
    phenny.write(['KICK', channel, nick, reason])
kick.commands = ['kick']
kick.priority = 'high'

def configureHostMask (mask):
  if mask == '*!*@*': return mask
  if re.match('^[^.@!/]+$', mask) is not None: return '%s!*@*' % mask
  if re.match('^[^@!]+$', mask) is not None: return '*!*@%s' % mask

  m = re.match('^([^!@]+)@$', mask)
  if m is not None: return '*!%s@*' % m.group(1)

  m = re.match('^([^!@]+)@([^@!]+)$', mask)
  if m is not None: return '*!%s@%s' % (m.group(1), m.group(2))

  m = re.match('^([^!@]+)!(^[!@]+)@?$', mask)
  if m is not None: return '%s!%s@*' % (m.group(1), m.group(2))
  return ''

def ban (phenny, input):
  """
  This give admins the ability to ban a user.
  The bot must be a Channel Operator for this command to work.
  """
  if not input.admin: return
  text = input.group().split()
  argc = len(text)
  if argc < 2: return
  opt = text[1]
  banmask = opt
  channel = input.sender
  if opt.startswith('#'):
    if argc < 3: return
    channel = opt
    banmask = text[2]
  banmask = configureHostMask(banmask)
  if banmask == '': return
  phenny.write(['MODE', channel, '+b', banmask])
ban.commands = ['ban']
ban.priority = 'high'

def unban (phenny, input):
  """
  This give admins the ability to unban a user.
  The bot must be a Channel Operator for this command to work.
  """
  if not input.admin: return
  text = input.group().split()
  argc = len(text)
  if argc < 2: return
  opt = text[1]
  banmask = opt
  channel = input.sender
  if opt.startswith('#'):
    if argc < 3: return
    channel = opt
    banmask = text[2]
  banmask = configureHostMask(banmask)
  if banmask == '': return
  phenny.write(['MODE', channel, '-b', banmask])
unban.commands = ['unban']
unban.priority = 'high'

def quiet (phenny, input):
  """
  This gives admins the ability to quiet a user.
  The bot must be a Channel Operator for this command to work
  """
  if not input.admin: return
  text = input.group().split()
  argc = len(text)
  if argc < 2: return
  opt = text[1]
  quietmask = opt
  channel = input.sender
  if opt.startswith('#'):
    if argc < 3: return
    quietmask = text[2]
    channel = opt
  quietmask = configureHostMask(quietmask)
  if quietmask == '': return
  phenny.write(['MODE', channel, '+q', quietmask])
quiet.commands = ['quiet']
quiet.priority = 'high'

def unquiet (phenny, input):
  """
  This gives admins the ability to unquiet a user.
  The bot must be a Channel Operator for this command to work
  """
  if not input.admin: return
  text = input.group().split()
  argc = len(text)
  if argc < 2: return
  opt = text[1]
  quietmask = opt
  channel = input.sender
  if opt.startswith('#'):
    if argc < 3: return
    quietmask = text[2]
    channel = opt
  quietmask = configureHostMask(quietmask)
  if quietmask == '': return
  phenny.write(['MODE', channel, '-q', quietmask])
unquiet.commands = ['unquiet']
unquiet.priority = 'high'

def kickban (phenny, input):
  """
  This gives admins the ability to kickban a user.
  The bot must be a Channel Operator for this command to work
  .kickban [#chan] user1 user!*@* get out of here
  """
  if not input.admin: return
  text = input.group().split()
  argc = len(text)
  if argc < 4: return
  opt = text[1]
  nick = opt
  mask = text[2]
  reasonidx = 3
  if opt.startswith('#'):
    if argc < 5: return
    channel = opt
    nick = text[2]
    mask = text[3]
    reasonidx = 4
  reason = ' '.join(text[reasonidx:])
  mask = configureHostMask(mask)
  if mask == '': return
  phenny.write(['MODE', channel, '+b', mask])
  phenny.write(['KICK', channel, nick, ' :', reason])
kickban.commands = ['kickban', 'kb']
kickban.priority = 'high'

def topic(phenny, input):
  """
  This gives admins the ability to change the topic.
  Note: One does *NOT* have to be an OP, one just has to be on the list of
  admins.
  """
  if not input.admin:
    return
  text = input.group().split()
  topic = ' '.join(text[1:])
  if topic == '':
    return
  channel = input.sender
  phenny.write(['PRIVMSG', 'ChanServ'], 'TOPIC %s %s' % (input.sender, topic))
  return
topic.commands = ['topic']
topic.priority = 'low'

#def defend_ground (phenny, input):
    #"""
    #This function monitors all kicks across all channels phenny is in. If she
    #detects that she is the one kicked she'll automatically join that channel.

    #WARNING: This may not needed and could cause problems if phenny becomes 
    #annoying. Please use this with caution.
    #"""
    #channel = input.sender
    #text = input.group()
    #phenny.write(['JOIN'], channel)                
#defend_ground.event = 'KICK'
#defend_ground.rule = '.*'
#defend_ground.priority = 'low'

if __name__ == '__main__': 
  print __doc__.strip()

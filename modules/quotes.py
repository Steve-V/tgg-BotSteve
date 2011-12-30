#!/usr/bin/env python
"""
quotedb.py - Phenny QuoteDB Module
Copyright 2011, NeWtoz, newtoz.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import sqlite3 as lite
dbfile = "quotes.db"

def quote_main(phenny, input):
        #remove the .quote from the input and any whitespace
        input = str(input).replace(".quote","",1).strip()
        db_conn = lite.connect(dbfile)
        db_curr = db_conn.cursor()
        #if there is no input, spit out a random quote
        if (input=='') or (input=='.quote'):
                db_curr.execute("SELECT * from quotes order by random() limit 1;")
                stuff = db_curr.fetchone()
                phenny.say ( str(stuff[1]) + ' (id: ' + str(stuff[0]) + ')' )
        #if there is an input, check to see if it is an actual number, if so 
        # find quote with that id
        elif input.isdigit():
                db_curr.execute('SELECT quote from quotes where id=(?)', [input])
                stuff = db_curr.fetchone()
                #if id doesn't exist, respond correctly, if it does, spit out quote  
                if stuff is None:
                        phenny.say("Quote not found")
                else:
                        phenny.say ( str(stuff[0]) + ' (id: ' + input + ')' )
	#if input is not blank or not a number, search by string
        else:
		db_curr.execute('SELECT * from quotes where quote like (?)', ['%'+input+'%'])
		if (db_curr.fetchone()) is None:
			phenny.say ("No matches found.")
		else:
			for row in db_curr:
				phenny.say( str(row[1]) + " (id: " + str(row[0]) + ")" )
        db_curr.close()
quote_main.commands = ['quote']
quote_main.priority = 'medium'

def quoteadd(phenny, input):
        #remove the .addquote from the input and any whitespace
	input = str(input).replace(".addquote","",1).strip()
        db_conn = lite.connect(dbfile)
        db_curr = db_conn.cursor()
	#insert quote into the database
        db_curr.execute('INSERT into quotes ("quote") values (?)', [input])
	db_conn.commit()
	#find the id that was created from the previous INSERT
	lastid = str(db_curr.lastrowid)
        db_curr.close()
	phenny.say ("Quote added. (id: " + lastid + ")")
quoteadd.commands = ['addquote']
quoteadd.priority = 'medium'

#This whole section could be commented out if it's prefered that everyone
# shouldn't have access to delete quotes. If that is the case, this could be 
# coded with the admin interface in mind.
def quoterm(phenny, input):
        #remove the .rmquote from the input and any whitespace
	#sometimes this doesn't remove the .rmquote, but does whitespace
        input = str(input).replace(".rmquote","",1).strip()
        #check to see if there is any input
	if (input=='.rmquote') or (input==''):
		phenny.say("No id given")
        #if there is an input, check to see if it is an actual number, if so 
        # remove quote with that id
	elif input.isdigit():
		db_conn = lite.connect(dbfile)
        	db_curr = db_conn.cursor()
                db_curr.execute('SELECT quote from quotes where id=(?)', [input])
                stuff = db_curr.fetchone()
                #if id doesn't exist, respond correctly, if it does, delete quote  
                if stuff is None:
                        phenny.say("Quote not found")
                else:
        		db_curr.execute('delete from quotes where id = (?)', [input])
        		db_conn.commit()
        		db_curr.close()
			phenny.say ("Deleted quote " + input + ".")
        #if input is not blank or not a number, we can't use it
	else:
		phenny.say ( "Input not reconized" )
quoterm.commands = ['rmquote']
quoterm.priority = 'medium'

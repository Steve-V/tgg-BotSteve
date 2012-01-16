#!/usr/bin/python2
"""
tfw.py - the fucking weather module
author: mutantmonkey <mutantmonkey@gmail.com>
"""

from urllib import quote as urlquote
from urllib2 import urlopen, HTTPError
import lxml.html

def tfw(phenny, input, fahrenheit=False, celsius=False):
	""".tfw <city/zip> - Show the fucking weather at the specified location."""

	zipcode = input.group(2)
	if not zipcode or zipcode == 'tgg':
		# default to Grand Rapids, Michigan
		zipcode = "49504"
		#NICKTRACKER: Save a default
    
    #NICKTRACKER: Save this in user settings.
	if fahrenheit:
		celsius_param = ""
	else:
		celsius_param = "&CELSIUS=yes"

	try:
		req = urlopen("http://thefuckingweather.com/?zipcode=%s%s" % (urlquote(zipcode), celsius_param))
	except HTTPError:
		phenny.say("THE INTERNET IS FUCKING BROKEN. Please try again later.")
		return

	doc = lxml.html.parse(req)

	location = doc.getroot().find_class('small')[0].text_content()

	try:
		weather = doc.getroot().get_element_by_id('content')
	except KeyError:
		phenny.say("Unknown location")
		return

	main = weather.find_class('large')

	# temperature is everything up to first <br />
	tempt = ""
	for c in main[0].text:
		if c.isdigit():
			tempt += c
	temp = int(tempt)
	#deg = unichr(176).encode('latin-1')
			
	# add units and convert if necessary
	if fahrenheit:
		temp = "%d degrees F?!" % (temp)
	elif celsius:
		temp = "%d degrees C?!" % (temp)
	else:
		tempev = (temp + 273.15) * 8.617343e-5 * 1000
		temp = "%f meV?!" % tempev
	
	# parse comment (broken by <br />, so we have do it this way)
	comments = main[0].xpath('text()')
	if len(comments) > 2:
		comment = "%s %s" % (comments[1], comments[2])
	else :
		comment = comments[1]

	# remark is in its own div, so we have it easy
	remark = weather.get_element_by_id('remark').text_content()

	response = "%s %s IN %s!  '%s'" % (temp, comment, location, remark)
	phenny.say(response)
tfw.rule = (['tfwMEV'], r'(.*)')

def tfwf(phenny, input):
	""".tfw <city/zip> - The fucking weather, in fucking degrees Fahrenheit."""
	return tfw(phenny, input, fahrenheit=True)
tfwf.rule = (['tfw'], r'(.*)')

def tfwc(phenny, input):
	""".tfwc <city/zip> - The fucking weather, in fucking degrees celsius."""
	return tfw(phenny, input, celsius=True)
tfwc.rule = (['tfwc'], r'(.*)')

if __name__ == '__main__':
	print __doc__.strip()


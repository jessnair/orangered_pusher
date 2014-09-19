#!/usr/bin/env python

import ConfigParser
import httplib2
import urllib2
import simplejson as json
from threading import Timer
import urllib
from urllib import urlencode
import time

def loadCfg(settings):
	config = ConfigParser.ConfigParser()
	config.read(settings)
	return config

def loginReddit(u,p):
	http = httplib2.Http()
	url = 'https://www.reddit.com/api/login'
	body = {'user': u, 'passwd': p}
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	try:
		response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))
		return response
	except Exception, e:
		print "Login barfed"
		pass

def getMe(cookie):
	http = httplib2.Http()
	headers = {'Cookie': cookie['set-cookie']}
	url = 'https://www.reddit.com/api/me.json'
	try:
		content = http.request(url, 'GET', headers=headers)
		parseMe(content,cookie)

	except Exception, e:
		print "Reading barfed"
		pass

def parseMe(d,c):
	data_json = json.loads(d[1])
	data = data_json['data']

	if data['has_mail'] or data['has_mod_mail']:
		getMessages(c)

def getMessages(cookie):
	http = httplib2.Http()
	headers = {'Cookie': cookie['set-cookie']}
	url = 'https://www.reddit.com/message/unread.json?limit=1'
	try:
		resp, content = http.request(url, 'GET', headers=headers)
		parseMessage(content)
	except Exception, e:
		print e
		pass

def parseMessage(d):
	data_json = json.loads(d)
	data = data_json['data']['children'][0]['data']
	global lastmsg

	# print data['name'] #debug
	if lastmsg != data['name']:
		print "New Message!"
		sendPushalot()
		lastmsg = data['name']

def sendPushalot():
	print "Push it... Push it real good."
	http = httplib2.Http()
	url = 'https://pushalot.com/api/sendmessage'
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	body = {
		'AuthorizationToken': authtoken,
		'Title': ptitle+' ('+user+')',
		'Body': pbody,
		'Image': pimg,
		'TimeTolive': pttl
	}
	try:
		response = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))
	except Exception, e:
		pass

def sendPushbullet():
	print "Sending pushbullet"


if __name__ == '__main__':
	settings  = loadCfg('settings.cfg')
	user 	  = settings.get('reddit','username')
	passwd	  = settings.get('reddit', 'password')
	paenabled = settings.get('pushalot', 'enabled')
	authtoken = settings.get('pushalot','token')
	ptitle    = settings.get('pushalot', 'title')
	pbody     = settings.get('pushalot', 'body')
	pttl	  = settings.get('pushalot', 'ttl')
	pimg	  = settings.get('pushalot', 'image')
	pbenabled = settings.get('pushbullet', 'enabled')
	pbtoken   = settings.get('pushbullet', 'token')
	pbiden    = settings.get('pushbullet', 'iden')

	cookie = loginReddit(user, passwd)
	lastmsg = 'none';

	#Crude way to run forever. Maybe there's a better way.
	while True:
		if cookie == 0 or cookie['status'] != '200':
			print "Problem logging in. Trying again."
			time.sleep(200)
			cookie = loginReddit(user, passwd)
			pass
		elif cookie['status'] == '200':
			print "Reading mail..."
			getMe(cookie)
			time.sleep(300)
		pass
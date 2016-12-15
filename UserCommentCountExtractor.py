#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree

def main(args):
	
	mincomments = 5
	users = extractUsers(mincomments)
	extractComments()

def extractComments(users):	
	comments = open("../Comments.xml", 'r')
	for comment in comments:
		comment = comment.rstrip('\n')
		if "row Id" not in comment:
			continue
		doc = xml.etree.ElementTree.fromstring(comment)
		rowID = doc.get('Id')
		postID = doc.get('PostId')
		score = doc.get('Score')
		text = doc.get('Text').encode('utf8').replace('\r\n','').replace('\n','')
		creationDate = doc.get('CreationDate')
		if 'UserId' in doc.keys():
			userID = doc.get('UserId')
		elif 'UserDisplayName' in doc.keys():
			userID = doc.get('UserDisplayName').encode('utf8')
		else:
			continue
		if userID in users:
			parsedComments.write(str(rowID) + "\t" + str(postID) + "\t" + str(score) + "\t" + str(text) + "\t" + str(creationDate) + "\t" + str(userID) + "\n")
	parsedComments.close()

def extractUsers(minCommentCount):
	comments = open("../Comments.xml", 'r')
	users = {}
		for comment in comments:
		comment = comment.rstrip('\n')
		if "row Id" not in comment:
			continue
		doc = xml.etree.ElementTree.fromstring(comment)
		rowID = doc.get('Id')
		postID = doc.get('PostId')
		score = doc.get('Score')
		text = doc.get('Text').encode('utf8')
		creationDate = doc.get('CreationDate')
		if 'UserId' in doc.keys():
			userID = doc.get('UserId')
			
		elif 'UserDisplayName' in doc.keys():
			userID = doc.get('UserDisplayName').encode('utf8')
		else:
			continue
		if userID in users:
			users[userID] = users[userID] + 1
		else:
			users[userID] = 1

	usercomments = open("../usercomments.txt", 'a')
	for user in users:
		if users[user] > mincomments:
			usercomments.write(str(user) + "\t" + str(users[user]) + "\n")
	usercomments.close()
	return set(users.keys())



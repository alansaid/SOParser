# -*- coding: utf-8 -*-

import xml.etree.ElementTree
comments = open("../Comments.xml", 'r')
usersFile = open("../usercomments.txt", 'r')
users = set()

parsedComments = open("../parsedcomments.tsv", "a")

for user in usersFile:
	[user, count] = user.split('\t')
	# print user
	users.add(user)




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

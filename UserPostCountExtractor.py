#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import json


def main():
    minposts = 50
    years = [2013] #, 2014]
    # users = extractUsers(minposts, years)
    extractComments(years)

def extractComments(years):
    users = set()
    usersFile = open('../userposts.txt')
    questiontitles = {}
    questiontags = {}
    for userline in usersFile:
        [user, number] = userline.strip().split('\t')
        users.add(user)
    for year in years:
        print "Parsing year: " + str(year)
        months = [str(year) + "-" + str(item).zfill(2) for item in range(1,4)]
        for month in months:
            print month
            postsFile = open("data/"+ str(month) + "-titles-tags.tsv","a")
            posts = open("../" + str(month) + ".Posts.xml", 'r')
            for post in posts:
                post = post.rstrip('\n')
                if "row Id" not in post:
                    continue
                doc = xml.etree.ElementTree.fromstring(post)
                ownerUserID = doc.get('OwnerUserId')
                if ownerUserID not in users:
                    continue
                creationDate = doc.get('CreationDate')
                rowID = doc.get('Id')
                postTypeId = doc.get('PostTypeId')
                score = doc.get('Score')
                text = doc.get('Body').encode('utf8').replace('\r\n','').replace('\n','')
                parent = doc.get('ParentId')
                if 'Title' in doc.keys():
                    title = doc.get('Title').encode('utf8')
                else:
                    title = ''
                if 'Tags' in doc.keys():
                    tags = doc.get('Tags').encode('utf8').replace("><", ",").replace("<","").replace(">","")
                else:
                    tags = ''
                if postTypeId == "1":
                    questiontags[rowID] = tags
                    questiontitles[rowID] = title
                elif parent in questiontitles.keys() and parent in questiontags.keys() :
                    tags = questiontags[parent]
                    title = questiontitles[parent]
                else:
                    continue
                # line = rowID + '\t' + ownerUserID + '\t' + creationDate + '\t' + title + '\t' + text + '\t' + tags + '\n'
                line = rowID + '\t' + ownerUserID + '\t' + creationDate + '\t' + score + "\t" + title + '\t' + tags + '\n'
                postsFile.write(line)
            postsFile.close()
    with open("questiontitles.json", 'w') as f:
        f.write(json.dumps(questiontitles))
    with open("questiontags.json", 'w') as f:
        f.write(json.dumps(questiontags))


def extractUsers(minPostCount, years):
    users = {}
    for year in years:
        print "Parsing year: " +str(year)
        posts = open("../"+str(year)+"-Posts.xml", 'r')
        for post in posts:
            post = post.rstrip('\n')
            if "row Id" not in post:
                continue
            doc = xml.etree.ElementTree.fromstring(post)
            creationDate = doc.get('CreationDate')
            if int(creationDate[:4]) not in years:
                continue
            # rowID = doc.get('Id')
            # postTypeId = doc.get('PostTypeId')
            # acceptedAnswerId = doc.get('AcceptedAnswerId')
            # score = doc.get('Score')
            # viewCount = doc.get('ViewCount')
            # text = doc.get('Body').encode('utf8')
            ownerUserID = doc.get('OwnerUserId')
            # lastEditorUserID = doc.get('LastEditorUserId')
            # lastEditorDisplayName = doc.get('LastEditorDisplayName')
            # lastEditDate = doc.get('LastEditDate')
            # lastActivityDate = doc.get('LastActivityDate')
            # title = doc.get('Title').encode('utf8')
            # tags = doc.get('Tags').encode('utf8')
            # answerCount = doc.get('AnswerCount')
            # commentCount = doc.get('CommentCount')
            # favoriteCount = doc.get('FavoriteCount')
            # communityOwnedDate = doc.get('CommunityOwnedDate')
            if ownerUserID in users:
                users[ownerUserID] = users[ownerUserID] + 1
            else:
                users[ownerUserID] = 1

    userPosts = open("../userposts.txt", 'a')
    for user in users:
        if users[user] > minPostCount:
            userPosts.write(str(user) + "\t" + str(users[user]) + "\n")
    userPosts.close()
    return set(users.keys())

if __name__ == '__main__':
    main()


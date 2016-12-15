#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree


def main():
    minposts = 10
    year = 2014
    # users = extractUsers(minposts, year)
    extractComments()

def extractComments():
    users = set()
    usersFile = open('../userposts.txt')
    for userline in usersFile:
        [user, number] = userline.strip().split('\t')
        users.add(user)


    posts = open("../2014-posts.xml", 'r')
    postsFile = open('../2014-filtered-posts.tsv','a')
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
        # acceptedAnswerId = doc.get('AcceptedAnswerId')
        score = doc.get('Score')
        # viewCount = doc.get('ViewCount')
        text = doc.get('Body').encode('utf8').replace('\r\n','').replace('\n','')
        # lastEditorUserID = doc.get('LastEditorUserId')
        # lastEditorDisplayName = doc.get('LastEditorDisplayName')
        # lastEditDate = doc.get('LastEditDate')
        # lastActivityDate = doc.get('LastActivityDate')
        if 'Title' in doc:
            title = doc.get('Title').encode('utf8')
        else:
            title = ''
        if 'Tags' in doc:
            tags = doc.get('Tags').encode('utf8')
        else:
            tags = ''
        # answerCount = doc.get('AnswerCount')
        # commentCount = doc.get('CommentCount')
        # favoriteCount = doc.get('FavoriteCount')
        # communityOwnedDate = doc.get('CommunityOwnedDate')
        line = rowID + '\t' + creationDate + '\t' + postTypeId + '\t' + score + '\t' + title + '\t' + text + '\t' + tags + '\n'
        postsFile.write(line)

def extractUsers(minPostCount, year):
    posts = open("../2014-posts.xml", 'r')
    users = {}
    for post in posts:
        post = post.rstrip('\n')
        if "row Id" not in post:
            continue
        doc = xml.etree.ElementTree.fromstring(post)
        creationDate = doc.get('CreationDate')
        if str(year) not in creationDate:
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


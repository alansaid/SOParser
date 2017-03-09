#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import json, re, cgi, os, pickle


def main():
    minposts = 50
    years = [2013, 2014]
    # users = extractUsers(minposts, years)
    extractComments(years)

def extractComments(years):
    users = set()
    usersFile = open('../userposts.txt', 'r')
    for userline in usersFile:
        [user, number] = userline.strip().split('\t')
        users.add(user)
    usersFile.close()

    for year in years:
        print "Parsing year: " + str(year)
        months = range(1,13)

        for month in months:
            yearmonth = str(year) + "-" + str(month).zfill(2)
            print(yearmonth)
            if month == 1:
                lastmonth = str(year-1) + "-12"
            else:
                lastmonth = str(year) + "-" + str(month-1).zfill(2)
            lastmonthsquestiontitlesfile = "data/" + lastmonth + "-questiontitles.json"
            lastmonthsquestiontagsfile = "data/" + lastmonth + "-questiontags.json"
            if os.path.isfile(lastmonthsquestiontitlesfile):
                print("loading last month's dictionaries")
                questiontitles = {}
                questiontags = {}
                with open(lastmonthsquestiontitlesfile, 'r') as f:
                    questiontitles = pickle.load(f)
                with open(lastmonthsquestiontagsfile, 'r') as f:
                    questiontags = pickle.load(f)
            else:
                print("creating new dictionaries")
                questiontitles = {}
                questiontags = {}

            monthusers = set()
            parsedpostsfile = open("data/"+ yearmonth + "-titles-tags.tsv","a")
            rawpostsfile = open("../" + yearmonth + ".Posts.xml", 'r')
            for post in rawpostsfile:
                post = post.rstrip('\n')
                if "row Id" not in post:
                    continue
                doc = xml.etree.ElementTree.fromstring(post)
                ownerUserID = doc.get('OwnerUserId')
                if ownerUserID not in users:
                    continue
                monthusers.add(ownerUserID)
                creationDate = doc.get('CreationDate')
                rowID = doc.get('Id')
                postTypeId = doc.get('PostTypeId')
                score = doc.get('Score')
                text = doc.get('Body').encode('utf8').replace('\r\n','').replace('\n','')
                tagremove = re.compile(r'(<!--.*?-->|<[^>]*>)')
                text = cgi.escape(tagremove.sub('', re.sub('<code>[^>]+</code>', '', text)))

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
                line = rowID + '\t' + ownerUserID + '\t' + creationDate + '\t' + score + "\t" + title + '\t' + tags + '\t' + text + "\n"
                parsedpostsfile.write(line)
            parsedpostsfile.close()
            rawpostsfile.close()

            with open("data/"+ yearmonth + "-titles-users.txt", 'w') as f:
                f.write("\n".join(monthusers))
            with open("data/" + yearmonth + "-questiontitles.dict", 'w') as f:
                pickle.dump(questiontitles, f, 'w')
            with open("data/" + yearmonth + "-questiontags.dict", 'w') as f:
                pickle.dump(questiontags, f, 'w')




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


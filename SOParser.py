#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import re, cgi, os, pickle, logging, time
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def main():
    minposts = 50

    years = [2013, 2014]
    extractUsers(minposts, years)
    extractComments(years)

def extractComments(years):
    users = set()
    usersFile = open('rawdata/userposts.txt', 'r')
    for userline in usersFile:
        [user, number] = userline.strip().split('\t')
        users.add(user)
    usersFile.close()

    for year in years:
        print "Parsing year: " + str(year)
        months = range(1,13)

        for month in months:
            start = time.time()
            yearmonth = str(year) + "-" + str(month).zfill(2)
            print(yearmonth)
            if month == 1:
                lastmonth = str(year-1) + "-12"
            else:
                lastmonth = str(year) + "-" + str(month-1).zfill(2)
            lastmonthsquestiontitlesfile = "data/" + lastmonth + "-questiontitles.dict"
            lastmonthsquestiontagsfile = "data/" + lastmonth + "-questiontags.dict"
            if os.path.isfile(lastmonthsquestiontitlesfile):
                logging.info('loading title dictionary: %s', lastmonthsquestiontitlesfile)
                logging.info('loading tag dictionary: %s', lastmonthsquestiontagsfile)
                questiontitles = {}
                questiontags = {}
                with open(lastmonthsquestiontitlesfile, 'r') as f:
                    questiontitles = pickle.load(f)
                    logging.info("Elements in questiontitles: %s", len(questiontitles))
                with open(lastmonthsquestiontagsfile, 'r') as f:
                    questiontags = pickle.load(f)
                    logging.info("Elements in questiontags: %s", len(questiontags))
            else:
                logging.info("creating new dictionaries")
                questiontitles = {}
                questiontags = {}

            monthusers = set()
            parsedpostsfile = open("data/"+ yearmonth + "-titles-tags-text.tsv","a")
            rawpostsfile = open("rawdata/" + yearmonth + ".Posts.xml", 'r')
            for post in rawpostsfile:
                post = post.rstrip('\n')
                if "row Id" not in post:
                    continue
                doc = xml.etree.ElementTree.fromstring(post)
                rowID = doc.get('Id')
                logging.debug('Parsing doc: %s', rowID)
                ownerUserID = doc.get('OwnerUserId')
                if ownerUserID not in users:
                    continue
                monthusers.add(ownerUserID)
                creationDate = doc.get('CreationDate')
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
                else:
                    try:
                        tags = questiontags[parent]
                        title = questiontitles[parent]
                    except KeyError:
                        continue
                line = rowID + '\t' + ownerUserID + '\t' + creationDate + '\t' + score + "\t" + title + '\t' + tags + '\t' + text + "\n"
                parsedpostsfile.write(line)
            parsedpostsfile.close()
            rawpostsfile.close()

            with open("data/"+ yearmonth + "-titles-users.txt", 'w') as f:
                f.write("\n".join(monthusers))
            with open("data/" + yearmonth + "-questiontitles.dict", 'w') as f:
                pickle.dump(questiontitles, f, pickle.HIGHEST_PROTOCOL)
            with open("data/" + yearmonth + "-questiontags.dict", 'w') as f:
                pickle.dump(questiontags, f, pickle.HIGHEST_PROTOCOL)
            end = time.time() - start
            logging.info("Elapsed time (s): %s", end)



def extractUsers(minPostCount, years):
    users = {}
    for year in years:
        print "Parsing year: " +str(year)
        posts = open("rawdata/"+str(year)+"-Posts.xml", 'r')
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

    userPosts = open("rawdata/userposts.txt", 'a')
    for user in users:
        if users[user] > minPostCount:
            userPosts.write(str(user) + "\t" + str(users[user]) + "\n")
    userPosts.close()
    return set(users.keys())

if __name__ == '__main__':
    main()


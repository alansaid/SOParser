from gensim import corpora, models
import cPickle, numpy, logging
from collections import OrderedDict
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

def main():
    global topicthreshold
    dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09',
             '2013-10', '2013-11', '2013-12',
             '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09',
             '2014-10', '2014-11', '2014-12']
    dates = ['2013-01', '2013-02']  # , '2013-03', '2013-03']
    numtopics = 40
    vocabsize = 2000
    topicthreshold = 0.0

    summarizeTopicsPerUser(dates)



def summarizeTopicsPerUser(dates):
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    usersfile = "data/allusers.txt"
    users = set(open(usersfile).read().split())

    document_users = {}
    document_scores = {}
    topics = {}
    values = {}
    for date in dates:
        date = str(date)
        print(date)

        tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict.pdict"
        with open(tokenized_dictfile, 'r') as f:
            tokenized_dict = cPickle.load(f)
        documentfile = open("data/" + date + "-titles-tags-text.tsv")
        topicfile = open("topics/" + date + "-topicusers.txt", 'w')
        lda = models.LdaMulticore.load("ldamodels/" + date + "-lda.model")

        for doc in documentfile:
            [docid, userid, creationdate, score, title, tags, text] = doc.rstrip("\n").split("\t")
            document_users[docid] = userid
            document_scores[docid] = score
            sentence = tokenized_dict[docid]
            bow = dictionary.doc2bow(sentence)
            documenttopics = lda[bow]
            for (topicid, topicvalue) in documenttopics:
                try:
                    topics[topicid]
                except KeyError:
                    topics[topicid] = {}
                    topics[topicid][userid] = []
                try:
                    topics[topicid][userid]
                except KeyError:
                    topics[topicid][userid] = []
                topics[topicid][userid].append(topicvalue)
        logging.info("Done with document loop")
        topicfile = open("topics/" + date + "-topicusers.txt", 'w')
        for topicid in topics.keys():
            thistopic = {}
            line = ""
            # for userid in topics[topicid].keys():
            for userid in users:
                # values[topicid]
                try:
                    thistopic[userid] = numpy.average(topics[topicid][userid])
                except KeyError:
                    thistopic[userid] = 0
                line += "\t" + str(thistopic[userid])
            line += "\n"
            # values[topicid] = OrderedDict(sorted(thistopic.items()))
            # line =  str(topicid) + "\t" + str(len(values[topicid]))
            topicfile.write(line)
        topicfile.close()


def writecpicklefile(content, filename):
    with open(filename, 'wb') as f:
        cPickle.dump(content, f, cPickle.HIGHEST_PROTOCOL)



def lookupTopics(dates):
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    document_users = {}
    document_scores = {}
    for date in dates:
        date = str(date)
        print(date)

        tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict.pdict"
        with open(tokenized_dictfile, 'r') as f:
            tokenized_dict = cPickle.load(f)

        usertopics = {}
        userdoctopics = {}
        usertopicscores = {}
        documentfile = open("data/" + date + "-titles-tags-text.tsv")
        topicfile = open("topics/" + date + "-topics.txt", 'w')
        lda = models.LdaMulticore.load("ldamodels/" + date + "-lda.model")

        for doc in documentfile:
            [docid, userid, creationdate, score, title, tags, text] = doc.rstrip("\n").split("\t")
            document_users[docid] = userid
            document_scores[docid] = score
            sentence = tokenized_dict[docid]
            bow = dictionary.doc2bow(sentence)
            documenttopics = lda[bow]
            for (topicid, topicvalue) in documenttopics:
                if topicvalue >= topicthreshold:
                    try:
                        userdoctopics[userid]
                    except KeyError:
                        userdoctopics[userid] = {}
                        userdoctopics[userid][topicid] = []
                        usertopicscores[userid] = {}
                        usertopicscores[userid][topicid] = []
                    try:
                        userdoctopics[userid][topicid]
                    except KeyError:
                        userdoctopics[userid][topicid] = []
                        usertopicscores[userid][topicid] = []
                    userdoctopics[userid][topicid].append(topicvalue)
                    usertopicscores[userid][topicid].append(int(score))
        for userid in userdoctopics.keys():
            usertopics[userid] = {}
            for topicid in userdoctopics[userid].keys():
                meantopicvalue = numpy.mean(userdoctopics[userid][topicid])
                meantopicscore = numpy.mean(usertopicscores[userid][topicid])
                numdocs = len(userdoctopics[userid][topicid])
                if meantopicvalue < topicthreshold:
                    continue
                usertopics[userid][topicid] = meantopicvalue
                topicterms = lda.get_topic_terms(topicid, topn=5)
                topicwords = ""
                for term in topicterms:
                    topicwords += dictionary.get(term[0]).ljust(15) + "\t"
                # resultline = str(userid)+"\t"+str(topicid)+"\t"+ str(meantopicvalue) + "\t" + str(numdocs) + "\t" + str(meantopicscore) + "\t" + str(topicwords) + "\n"
                resultline = str(topicid) + "\t" + str(userid) + "\t" + str(meantopicvalue) + "\n"
                topicfile.write(resultline)
        topicfile.close()


if __name__ == '__main__':
    main()

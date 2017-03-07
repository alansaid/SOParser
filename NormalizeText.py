from __future__ import print_function
from gensim import utils, corpora, models
from gensim.parsing.preprocessing import STOPWORDS
import logging, json, os, re
from pprint import pprint
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy


def main():
    dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12',
             '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']

    # filterUsers(dates)
    createGlobalDictionary(dates)
    memoryBasedTokenization(dates)
    performTFIDF(dates)
    performLDA(dates)

    # performHDP(date)
    # lookupHDPTopics(date, ids)
    # lookupTopics(dates)



def filterUsers(dates):
    users = set()
    for date in dates:
        musers = set()
        for line in open("data/" + str(date) + "-title-users.txt", "r"):
            musers.add(line.strip("\n"))
        if len(users) == 0:
            users = musers
        else:
            users = set.intersection(users, musers)
    ufile = open("data/title-users.txt", "w")
    for user in users:
        ufile.write(user + "\n")
    ufile.close()



def lookupTopics(dates):
    tokenized_dict = json.load(file("models/global-tokenized_dict.json"))
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    users = set()
    for user in open("data/title-users.txt"):
        users.add(user.strip("\n"))
    document_users = {}
    document_scores = {}
    for date in dates:
        print(date)
        usertopics = {}
        userdoctopics = {}
        usertopicscores = {}
        documentfile = open("data/" + str(date) + "-titles-tags.tsv")
        topicfile = open(str(date) + "-topics.txt", 'a')
        lda = models.LdaModel.load("models/" + date + "-lda.model")

        for doc in documentfile:
            [docid, userid, creationdate, score, title, tags] = doc.rstrip("\n").split("\t")

            if userid not in users:
                continue

            document_users[docid] = userid
            document_scores[docid] = score

            sentence = tokenized_dict[docid]
            bow = dictionary.doc2bow(sentence)
            documenttopics = lda[bow]

            # topics_by_value = sorted(documenttopics, key=lambda tup: tup[1], reverse=True)
            # topicfile.write(docid + "\t" + userid + "\t" + score + "\t" + json.dumps(topics_by_value) + "\n")

            for (topicid, topicvalue) in documenttopics:
                if userid not in userdoctopics:
                    userdoctopics[userid] = {}
                    userdoctopics[userid][topicid] = []

                    usertopicscores[userid] = {}
                    usertopicscores[userid][topicid] = []

                if topicid not in userdoctopics[userid]:
                    userdoctopics[userid][topicid] = []
                    usertopicscores[userid][topicid] = []
                topicthreshold = 0.1
                if topicvalue >= topicthreshold:
                    userdoctopics[userid][topicid].append(topicvalue)
                    usertopicscores[userid][topicid].append(int(score))
        # topicfile.close()
        for userid in userdoctopics.keys():
            usertopics[userid] = {}
            for topicid in userdoctopics[userid].keys():
                meantopicvalue = numpy.mean(userdoctopics[userid][topicid])
                meantopicscore = numpy.mean(usertopicscores[userid][topicid])
                numdocs = len(userdoctopics[userid][topicid])
                if meantopicvalue < 0.1:
                    continue
                usertopics[userid][topicid] = meantopicvalue
                topicterms = lda.get_topic_terms(topicid, topn=5)
                topicline = ""
                for term in topicterms:
                    topicline += dictionary.get(term[0]).ljust(15) + "\t"
                resultline = str(userid)+"\t"+str(topicid)+"\t"+ str(meantopicvalue) + "\t" + numdocs + "\t" + topicline + "\t" + str(meantopicscore) + "\n"
                topicfile.write(resultline)
        topicfile.close()


def readFile(date):
    original_sentences = {}
    for line in open("data/" + date + "-posts.tsv"):
        [id, postDate, type, score, title, text, tags] = line.split('\t')
        original_sentences[id] = text
    return original_sentences

def lookupHDPTopics(date, docIDs):
    tokenized_dict = json.load(file("models/global-tokenized_dict.json"))
    original_sentences = readFile(date)
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    hdp = models.HdpModel.load("models/"+date+"-hdp.model")
    for docID in docIDs:
        sentence = tokenized_dict[str(docID)]
        bow = dictionary.doc2bow(sentence)
        pprint(sentence)
        pprint(original_sentences[str(docID)])

        print(hdp[bow])

    print(hdp.show_topics(num_topics=-1, num_words=5, formatted=True))

def lookupLDATopics(date, docIDs, numTopics):
    tokenized_dict = json.load(file("models/global-tokenized_dict.json"))
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    lda = models.LdaModel.load("models/"+date+"-lda.model")
    for docID in docIDs:
        sentence = tokenized_dict[str(docID)]
        bow = dictionary.doc2bow(sentence)
        topics = lda[bow]
        topics_by_value = sorted(topics, key=lambda tup: tup[1], reverse=True)
        return topics_by_value[:numTopics]

def performTFIDF(dates):
    for date in dates:
        corpus = corpora.MmCorpus("models/" + date + "-tokenized.mm")
        tfidf = models.TfidfModel(corpus)
        tfidf.save("models/"+date+"-tfidf.model")
        tfidf_corpus = tfidf[corpus]
        corpora.MmCorpus.save_corpus("models/"+date+"-tfidf.mm", tfidf_corpus)

def performLDA(dates):
    for date in dates:
        print("performing lda on " + str(date))
        dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
        corpus = corpora.MmCorpus("models/" + date + "-tfidf.mm")
        lda = models.LdaMulticore(corpus, id2word=dictionary, num_topics=20, workers=3)
        # lda = models.LdaModel(corpus, alpha='auto', id2word=dictionary, num_topics=20)
        lda_corpus = lda[corpus]
        corpora.MmCorpus.serialize('models/' + date + '-lda.mm', lda_corpus)
        lda.save('models/' + date + '-lda.model')

def performHDP(date):
    print("performing hdp")
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    corpus = corpora.MmCorpus("models/" + date + "-tfidf.mm")
    hdp = models.HdpModel(corpus, id2word=dictionary)
    hdp_corpus = hdp[corpus]
    corpora.MmCorpus.serialize('models/' + date + '-hdp.mm', hdp_corpus)
    hdp.save('models/' + date + '-hdp.model')

def createGlobalDictionary(dates):
    stoplist = STOPWORDS
    tokenized_dict = {}
    original_dict = {}
    for date in dates:
        print("parsing month: " + date)
        linecounter = 0
        for line in open("data/" + date + "-titles-tags.tsv"):
            linecounter+=1
            [id, userid, postDate, score, text, tags] = line.split('\t')
            text = text + " " + tags
            stemmer = PorterStemmer()
            tokenized_line = [stemmer.stem(word.lower()) for word in word_tokenize(text.decode('utf-8'), language='english') if word not in stoplist and len(word) > 3 and re.match('^[\w-]+$', word) is not None]
            tokenized_dict[id] = tokenized_line
            original_dict[id] = text
            # print("line: " + str(linecounter) + "\r",)

    with open("models/global-tokenized_dict.json", 'w') as f: f.write(json.dumps(tokenized_dict))
    with open("models/global-original_dict.json", 'w') as f: f.write(json.dumps(original_dict))
    dictionary = corpora.Dictionary(tokenized_dict.values())
    dictionary.filter_extremes(no_below=200, no_above=0.8, keep_n=1000)
    dictionary.compactify()
    dictionary.save('models/global-dictionary.dict')
    print("Number of terms in dictionary: " + str(len(dictionary.keys())))

def memoryBasedTokenization(dates):
    stoplist = set(stopwords.words("english"))

    stemmed_or_tokenized_file = "models/global-tokenized_dict.json"
    if os.path.isfile(stemmed_or_tokenized_file):
        stemmed_or_tokenized_dict = json.load(file(stemmed_or_tokenized_file))
    else:
        stemmed_or_tokenized_dict = {}
    original_file = "models/global-original_dict.json"
    if os.path.isfile(original_file):
        original_dict = json.load(file(original_file))
    else:
        original_dict = {}

    for date in dates:
        print("parsing month: " + date)
        for line in open("data/" + date + "-titles-tags.tsv"):
            # [id, postDate, type, score, title, text, tags] = line.split('\t')
            [id, userid, postDate, score, text, tags] = line.rstrip('\n').split('\t')
            text = text + " " + tags
            # stemmed_or_tokenized_line = utils.lemmatize(text.lower(), stopwords=stoplist)
            stemmer = PorterStemmer()
            stemmed_or_tokenized_line = [stemmer.stem(word.lower()) for word in word_tokenize(text.decode('utf-8'), language='english') if word not in stoplist and len(word) > 3]
            stemmed_or_tokenized_dict[id] = stemmed_or_tokenized_line
            original_dict[id] = text
        # dictionary = corpora.Dictionary(stemmed_or_tokenized_dict.values())
        dictionary = corpora.Dictionary.load('models/global-dictionary.dict')
        corpus = [dictionary.doc2bow(sentence) for sentence in stemmed_or_tokenized_dict.values()]
        corpora.MmCorpus.serialize('models/' + date + '-tokenized.mm', corpus)  # store to disk, for later use

    with open("models/global-tokenized_dict.json", 'w') as f:
        f.write(json.dumps(stemmed_or_tokenized_dict))
    with open("models/global-original_dict.json", 'w') as f:
        f.write(json.dumps(original_dict))
    # dictionary = corpora.Dictionary(stemmed_or_tokenized_dict.values())
    # dictionary.compactify()
    # dictionary.save('models/global-dictionary.dict')



if __name__ == '__main__':
    main()

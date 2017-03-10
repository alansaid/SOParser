from __future__ import print_function
from gensim import utils, corpora, models
from gensim.parsing.preprocessing import STOPWORDS
import logging, os, re, numpy, pickle
from pprint import pprint
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



def main():
    dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12',
             '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']

    dates = ['2013-01', '2013-02']
    # filterUsers(dates)
    createDictionariesFromFiles(dates)
    createMonthCorpuses(dates)
    performTFIDF(dates)
    performLDA(dates)


    lookupTopics(dates)


# run this to only get users that exist in all months
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
    ufile = open("data/all-month-users.txt", "w")
    for user in users:
        ufile.write(user + "\n")
    ufile.close()



def lookupTopics(dates):
    tokenized_dictfile = "models/global-tokenized_dict.pdict"
    tokenized_dict = {}
    with open(tokenized_dictfile, 'r') as f:
        tokenized_dict = pickle.load(f)
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    # users = set()
    # for user in open("data/all-month-users.txt"):
    #     users.add(user.strip("\n"))
    document_users = {}
    document_scores = {}
    for date in dates:
        print(date)
        usertopics = {}
        userdoctopics = {}
        usertopicscores = {}
        documentfile = open("data/" + str(date) + "-titles-tags-text.tsv")
        topicfile = open(str(date) + "-topics.txt", 'a')
        lda = models.LdaModel.load("models/" + date + "-lda.model")

        for doc in documentfile:
            [docid, userid, creationdate, score, title, tags, text] = doc.rstrip("\n").split("\t")

            # if userid not in users:
            #     continue

            document_users[docid] = userid
            document_scores[docid] = score

            sentence = tokenized_dict[docid]
            bow = dictionary.doc2bow(sentence)
            documenttopics = lda[bow]

            for (topicid, topicvalue) in documenttopics:
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
                topicthreshold = 0.1
                if topicvalue >= topicthreshold:
                    userdoctopics[userid][topicid].append(topicvalue)
                    usertopicscores[userid][topicid].append(int(score))
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
                topicwords = ""
                for term in topicterms:
                    topicwords += dictionary.get(term[0]).ljust(15) + "\t"
                resultline = str(userid)+"\t"+str(topicid)+"\t"+ str(meantopicvalue) + "\t" + str(numdocs) + "\t" + str(meantopicscore) + "\t" + str(topicwords) + "\n"
                topicfile.write(resultline)
        topicfile.close()


def readFile(date):
    original_sentences = {}
    for line in open("data/" + date + "-posts.tsv"):
        [id, postDate, type, score, title, text, tags] = line.split('\t')
        original_sentences[id] = text
    return original_sentences


def lookupLDATopics(date, docIDs, numTopics):
    tokenized_dictfile = "models/global-tokenized_dict.pdict"
    with open(tokenized_dictfile, 'r') as f:
        tokenized_dict = pickle.load(f)
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

def tokenizeandstemline(text):
    stoplist = STOPWORDS
    stemmer = PorterStemmer()
    tokenized_line = [stemmer.stem(word.lower()) for word in word_tokenize(text.decode('utf-8'), language='english') if word not in stoplist and len(word) > 3 and re.match('^[\w-]+$', word) is not None]
    return tokenized_line

def writepicklefile(content, filename):
    with open(filename, 'w') as f:
        pickle.dump(content, f, pickle.HIGHEST_PROTOCOL)

def createDictionariesFromFiles(dates):
    global_tokenized_dict = {}
    global_original_dict = {}
    for date in dates:
        print("parsing month: " + date)
        monthly_tokenized_dict = {}
        monthly_original_dict = {}
        docids = {}
        for line in open("data/" + date + "-titles-tags-text.tsv"):
            [id, userid, postDate, score, title, tags, text] = line.split('\t')

            docids[id] = (userid, score)

            text = title + " " + tags + " " + text
            tokenized_line = tokenizeandstemline(text)

            global_tokenized_dict[id] = tokenized_line
            global_original_dict[id] = text

            monthly_tokenized_dict[id] = tokenized_line
            monthly_original_dict[id] = text
        monthly_docids_dictfile = "models/"+date+"-docids.pdict"
        writepicklefile(docids, monthly_docids_dictfile)
        monthly_tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict.pdict"
        writepicklefile(monthly_tokenized_dict, monthly_tokenized_dictfile)
        monthly_original_dictfile = "models/"+date+"-monthly-original_dict.pdict"
        writepicklefile(monthly_original_dict, monthly_original_dictfile)

    global_tokenized_dictfile = "models/global-tokenized_dict.pdict"
    writepicklefile(global_tokenized_dict, global_tokenized_dictfile)
    global_original_dictfile = "models/global-original_dict.pdict"
    writepicklefile(global_original_dict, global_original_dictfile)

    dictionary = corpora.Dictionary(global_tokenized_dict.values())
    dictionary.filter_extremes(no_below=200, no_above=0.8, keep_n=1000)
    dictionary.compactify()
    dictionary.save('models/global-dictionary.dict')
    logging.info("Dictionary size: %s", len(dictionary))

def createMonthCorpuses(dates):
    for date in dates:
        logging.info("Parsing date: %s", date)
        print("parsing month: " + date)
        monthly_dict_file = "models/" + date + "-monthly-tokenized_dict.pdict"
        with open(monthly_dict_file, 'r') as f:
            tokenized_dict = pickle.load(f)
        dictionary = corpora.Dictionary.load('models/global-dictionary.dict')
        corpus = [dictionary.doc2bow(sentence) for sentence in tokenized_dict.values()]
        corpora.MmCorpus.serialize('models/' + date + '-tokenized.mm', corpus)


if __name__ == '__main__':
    main()

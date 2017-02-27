from gensim import utils, corpora, models
from gensim.parsing.preprocessing import STOPWORDS
import logging, json, os
from pprint import pprint
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# import nltk


# class MyCorpus(object):
#     def __iter__(self):
#         for line in open(file):
#             dictionary = corpora.Dictionary.load('models/global-dictionary.dict')
#             # stoplist = set(nltk.corpus.stopwords.words("english"))
#             stoplist = STOPWORDS
#             yield dictionary.doc2bow(utils.lemmatize(line.split('\t')[5].lower(), stopwords=stoplist))
#

# pick 5 users, track topics over

def main():
    dates = ['2013-03']#, '2013-02']

    # createGlobalDictionary()
    # memoryBasedTokenization(dates)
    # performTFIDF(dates)
    performLDA(dates)
    # topics = lookupLDATopics(date, ids, 5)

    # performHDP(date)
    # lookupHDPTopics(date, ids)
    # lookupTopics(dates)


def lookupTopics(dates):
    tokenized_dict = json.load(file("models/global-tokenized_dict.json"))
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")

    users = set()
    for user in open('2013-02-users.txt'):
        users.add(user)
    document_users = {}
    document_scores = {}
    for date in dates:
        documentfile = open("data/10k-" + str(date) + "-posts.tsv")
        topicfile = open(str(date) + "-topics.txt", 'a')
        lda = models.LdaModel.load("models/" + date + "-lda.model")
        for doc in documentfile:
            # line = rowID + '\t' + ownerUserID + '\t' + creationDate + '\t' + postTypeId  + '\t' + text + '\t' + score + '\n'
            [docid, userid, creationdate, type, text, score] = doc.rstrip("\n").split("\t")

            # if dates[0] in creationdate:
            #     users.add(userid)
            # elif dates[0] not in creationdate and userid not in users:
            #     continue
            if userid not in users:
                continue
            document_users[docid] = userid
            document_scores[docid] = score

            sentence = tokenized_dict[docid]
            bow = dictionary.doc2bow(sentence)
            topics = lda[bow]
            topics_by_value = sorted(topics, key=lambda tup: tup[1], reverse=True)
            topicfile.write(docid + "\t" + userid + "\t" + score + "\t" + json.dumps(topics_by_value) + "\n")
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

    print hdp.show_topics(num_topics=-1, num_words=5, formatted=True)

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
        print "performing lda"
        dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
        corpus = corpora.MmCorpus("models/" + date + "-tfidf.mm")
        lda = models.LdaMulticore(corpus, id2word=dictionary, num_topics=20, workers=3)
        # lda = models.LdaModel(corpus, alpha='auto', id2word=dictionary, num_topics=20)
        lda_corpus = lda[corpus]
        corpora.MmCorpus.serialize('models/' + date + '-lda.mm', lda_corpus)
        lda.save('models/' + date + '-lda.model')

def performHDP(date):
    print "performing lda"
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    corpus = corpora.MmCorpus("models/" + date + "-tfidf.mm")
    hdp = models.HdpModel(corpus, id2word=dictionary)
    hdp_corpus = hdp[corpus]
    corpora.MmCorpus.serialize('models/' + date + '-hdp.mm', hdp_corpus)
    hdp.save('models/' + date + '-hdp.model')

def createGlobalDictionary():
    years = [2013] #, 2014]
    # stoplist = set(nltk.corpus.stopwords.words("english"))
    stoplist = STOPWORDS
    tokenized_dict = {}
    original_dict = {}
    for year in years:
        # months = [str(year) + "-" + str(item).zfill(2) for item in range(1, 13)]
        months = ['2013-00']
        for month in months:
            print "parsing month: " + month
            for line in open("data/" + month + "-posts.tsv"):
                [id, postDate, type, score, userid, text, tags] = line.split('\t')
                tokenized_line = utils.lemmatize(text.lower(), stopwords=stoplist)
                tokenized_dict[id] = tokenized_line
                original_dict[id] = text

    with open("models/global-tokenized_dict.json", 'w') as f: f.write(json.dumps(tokenized_dict))
    with open("models/global-original_dict.json", 'w') as f: f.write(json.dumps(original_dict))
    dictionary = corpora.Dictionary(tokenized_dict.values())
    dictionary.compactify()
    dictionary.save('models/global-dictionary.dict')

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
        print "parsing month: " + date
        for line in open("data/" + date + "-posts.tsv"):
            # [id, postDate, type, score, title, text, tags] = line.split('\t')
            [id, userid, postDate, type, text, score] = line.rstrip('\n').split('\t')
            # stemmed_or_tokenized_line = utils.lemmatize(text.lower(), stopwords=stoplist)
            stemmer = PorterStemmer()
            stemmed_or_tokenized_line = [stemmer.stem(word) for word in word_tokenize(text.decode('utf-8'), language='english') if word not in stoplist]
            stemmed_or_tokenized_dict[id] = stemmed_or_tokenized_line
            original_dict[id] = text
        dictionary = corpora.Dictionary(stemmed_or_tokenized_dict.values())
        corpus = [dictionary.doc2bow(sentence) for sentence in stemmed_or_tokenized_dict.values()]
        corpora.MmCorpus.serialize('models/' + date + '-tokenized.mm', corpus)  # store to disk, for later use

    with open("models/global-tokenized_dict.json", 'w') as f:
        f.write(json.dumps(stemmed_or_tokenized_dict))
    with open("models/global-original_dict.json", 'w') as f:
        f.write(json.dumps(original_dict))
    dictionary = corpora.Dictionary(stemmed_or_tokenized_dict.values())
    dictionary.compactify()
    dictionary.save('models/global-dictionary.dict')


# def fileBasedLemmatization(date, file):
#     corpus = MyCorpus() # doesn't load the corpus into memory!
#     corpora.MmCorpus.serialize('models/'+date+'-corpus.mm', corpus)


if __name__ == '__main__':
    main()

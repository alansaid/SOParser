from gensim import corpora, models
import logging, numpy, cPickle
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)



def main():
    global topicthreshold
    dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12',
             '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']
    # dates = ['2013-01', '2013-02']
    topics = 40
    topicthreshold = 0.3

    # countWords(dates, topics)
    docPerTopic(dates)


def docPerTopic(dates):
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    doctopics = {}
    topicfile = open("stats/docpertopic.tsv", 'w')
    for date in dates:

        date = str(date)
        print(date)

        tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict.pdict"
        with open(tokenized_dictfile, 'rb') as f:
            tokenized_dict = cPickle.load(f)

        documentfile = open("data/" + date + "-titles-tags-text.tsv")
        lda = models.LdaMulticore.load("ldamodels/" + date + "-lda.model")

        for doc in documentfile:
            [docid, userid, creationdate, score, title, tags, text] = doc.rstrip("\n").split("\t")


            sentence = tokenized_dict[docid]
            bow = dictionary.doc2bow(sentence)
            documenttopics = lda[bow]
            for (topicid, topicvalue) in documenttopics:
                if topicvalue < topicthreshold:
                    continue
                try:
                    doctopics[topicid]
                except KeyError:
                    doctopics[topicid] = {}
                    doctopics[topicid][date] = 0
                try:
                    doctopics[topicid][date]
                except KeyError:
                    doctopics[topicid][date] = 0
                doctopics[topicid][date]+=1

    print doctopics
    for topicid in doctopics.keys():
        line = str(topicid)
        for date in doctopics[topicid].keys():
            line += "\t" +str(doctopics[topicid][date])
        line += "\n"
        topicfile.write(line)
    topicfile.close()




def countWords(dates, numtopics):
    wordfile = open("stats/wordcounts.tsv", "w")
    words = {} #each word counted once per doc
    totalwords = {} #each word counted n times per n mentions in doc
    uniquewords = {} #the number of unique terms from the doctionary used in one month
    vocabcount = {}
    doclength = {}
    for date in dates:
        words[date] = 0
        uniquewords[date]  = set()
        totalwords[date] = 0
        tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict.pdict"
        with open(tokenized_dictfile, 'rb') as f:
            tokenized_dict = cPickle.load(f)
        dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
        lda = models.LdaMulticore.load("ldamodels/" + date + "-lda.model")

        countedwordtopics = []
        logging.info("Parsing date: %s", str(date))
        [countedwordtopics.append(0) for i in range(numtopics)]
        for docID in tokenized_dict.keys():
            doc = tokenized_dict[docID]
            bow = dictionary.doc2bow(doc)
            wordcount = len(bow)
            words[date] += wordcount
            totalwords[date] += sum([tup[1] for tup in bow])
            uwords = [tup[0] for tup in bow]
            uniquewords[date] = uniquewords[date].union(uwords)
            doclength[docID] = sum([tup[1] for tup in bow])
            for tup in bow:
                word = tup[0]
                count = tup[1]
                try:
                    vocabcount[word]
                except KeyError:
                    vocabcount[word] = 0
                vocabcount[word] = vocabcount[word] + count
        line = str(date) + "\t" + str(words[date]) + "\t" + str(totalwords[date]) + "\t" + str(len(uniquewords[date])) + "\n"
        wordfile.write(line)
    wordfile.close()

    # for word in vocabcount:
    #     print str(word) + "\t" + str(vocabcount[word])
    docfile = open("stats/doclength.tsv", 'w')
    [docfile.write(str(doc) +"\t" + str(doclength[doc])+"\n") for doc in doclength]
    docfile.close()

if __name__ == '__main__':
    main()

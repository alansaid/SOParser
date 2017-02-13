from gensim import utils, corpora, models
import logging, json
from pprint import pprint
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
import nltk


class MyCorpus(object):
    def __iter__(self):
        for line in open(file):
            dictionary = corpora.Dictionary.load('models/global-dictionary.dict')
            yield dictionary.doc2bow(utils.lemmatize(line.split('\t')[5].lower(), stopwords=stoplist))


def main():
    date = '2013-00'
    file = 'data/'+date+'-posts.tsv'
    ids = [14109483] #, 14108285]

    createGlobalDictionary()
    # memoryBasedLemmatization(date, file)
    # performTFIDF(date)
    # performLDA(date)

    # lookupLDATopics(date, ids)


def readFile(date):
    original_sentences = {}
    for line in open("data/" + date + "-posts.tsv"):
        [id, postDate, type, score, title, text, tags] = line.split('\t')
        original_sentences[id] = text
    return original_sentences


def lookupLDATopics(date, docIDs):
    lemmatized_dict = json.load(file("models/" + date + "-lemmatized_dict.json"))
    original_sentences = readFile(date)
    dictionary = corpora.Dictionary.load("models/" + date + "-dictionary.dict")
    lda = models.LdaModel.load("models/"+date+"-lda.model")
    for docID in docIDs:
        # print lemmatized_dict[str(docID)]
        sentence = lemmatized_dict[str(docID)]
        bow = dictionary.doc2bow(sentence)
        pprint(sentence)
        pprint(original_sentences[str(docID)])

        print(lda[bow])



def performTFIDF(date):
    corpus = corpora.MmCorpus("models/" + date + "-lemmatized.mm")
    tfidf = models.TfidfModel(corpus)
    tfidf.save("models/"+date+"-tfidf.model")
    tfidf_corpus = tfidf[corpus]
    corpora.MmCorpus.save_corpus("models/"+date+"-tfidf.mm", tfidf_corpus)

def performLDA(date):
    dictionary = corpora.Dictionary.load("models/" + date + "-dictionary.dict")
    corpus = corpora.MmCorpus("models/" + date + "-tfidf.mm")
    lda = models.LdaModel(corpus, alpha='auto', id2word=dictionary, num_topics=20)
    lda_corpus = lda[corpus]
    corpora.MmCorpus.serialize('models/' + date + '-lda.mm', lda_corpus)
    lda.save('models/' + date + '-lda.model')

def createGlobalDictionary():
    years = [2013, 2014]
    stoplist = set(nltk.corpus.stopwords.words("english"))
    lemmatized_dict = {}
    original_dict = {}
    for year in years:
        months = [str(year) + "-" + str(item).zfill(2) for item in range(1, 13)]
        for month in months:
            print "parsing month: " + month
            for line in open("data/" + month + "-posts.tsv"):
                [id, postDate, type, score, title, text, tags] = line.split('\t')
                lemmatized_line = utils.lemmatize(text.lower(), stopwords=stoplist)
                lemmatized_dict[id] = lemmatized_line
                original_dict[id] = text

    with open("models/global-lemmatized_dict.json", 'w') as f: f.write(json.dumps(lemmatized_dict))
    with open("models/global-original_dict.json", 'w') as f: f.write(json.dumps(original_dict))
    dictionary = corpora.Dictionary(lemmatized_dict.values())
    dictionary.compactify()
    dictionary.save('models/global-dictionary.dict')


def fileBasedLemmatization(date, file):
    corpus = MyCorpus() # doesn't load the corpus into memory!
    corpora.MmCorpus.serialize('models/'+date+'-corpus.mm', corpus)


def memoryBasedLemmatization(date, file):
    stoplist = set(nltk.corpus.stopwords.words("english"))
    lemmatized_dict = {}
    for line in open(file):
        [id, postDate, type, score, title, text, tags] = line.split('\t')
        lemmatized_line = utils.lemmatize(text.lower(), stopwords=stoplist)
    dictionary = corpora.Dictionary.load('models/global-dictionary.dict')
    corpus = [dictionary.doc2bow(sentence) for sentence in lemmatized_dict.values()]
    corpora.MmCorpus.serialize('models/'+date+'-lemmatized.mm', corpus)  # store to disk, for later use


if __name__ == '__main__':
    main()

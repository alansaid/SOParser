from gensim import utils, corpora
from six import iteritems
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
import nltk


class MyCorpus(object):
    def __iter__(self):
        for line in open(file):
            yield dictionary.doc2bow(utils.lemmatize(line.split('\t')[5].lower(), stopwords=stoplist))
            # yield dictionary.doc2bow(line.split('\t')[5].lower().split())

            # assume there's one document per line, tokens separated by whitespace
            # yield dictionary.doc2bow(line.lower().split())

# dictionary = corpora.Dictionary
# file = ''
# stoplist = set()

def main():
    global file, stoplist, dictionary
    date = '2013-00'
    file = 'data/'+date+'-posts.tsv'
    stoplist = set(nltk.corpus.stopwords.words("english"))
    # fileBasedModels()
    memoryBasedModels(date)



def fileBasedModels(date):
    global dictionary, file, stoplist
    # collect statistics about all tokens
    # dictionary = corpora.Dictionary([[line.split('\t')[5].lower().split() for line in open(file)] for file in files][0])
    dictionary = corpora.Dictionary([[utils.lemmatize(line.split('\t')[5].lower(), stopwords=stoplist) for line in open(file)]][0])

    # remove stop words and words that appear only once
    stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]
    once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
    #
    # remove stop words and words that appear only once
    dictionary.filter_tokens(stop_ids + once_ids)

    # remove gaps in id sequence after words that were removed
    dictionary.compactify()
    dictionary.save('models/'+date+'-dictionary.dict')

    print(dictionary)

    corpus = MyCorpus() # doesn't load the corpus into memory!
    corpora.MmCorpus.serialize('models/'+date+'-corpus.mm', corpus)


def memoryBasedModels(date):
    global dictionary, file, stoplist
    lemmatized_text = [utils.lemmatize(line.split('\t')[5].lower(), stopwords=stoplist) for line in open(file)]
    dictionary = corpora.Dictionary(lemmatized_text)

    stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]

    once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]

    dictionary.filter_tokens(stop_ids + once_ids)
    dictionary.compactify()
    dictionary.save('models/'+date+'-dictionary.dict')
    # print [line.split('\t')[5].lower() for line in open(file)][1:4]

    corpus = [dictionary.doc2bow(lemmatized_line) for lemmatized_line in lemmatized_text]

    # print corpus
    # for c in corpus:
    #     print c
    corpora.MmCorpus.serialize('models/'+date+'-corpus.mm', corpus)  # store to disk, for later use
    # for c in corpus:
    #     print(c)



if __name__ == '__main__':
    main()

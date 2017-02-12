from gensim import corpora, models, similarities
import os, logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

date = '2013-01'

if (os.path.exists("models/" + date + "-dictionary.dict")):
    dictionary = corpora.Dictionary.load("models/" + date + "-dictionary.dict")
    corpus = corpora.MmCorpus("models/" + date + "-corpus.mm")
    print("Used files generated from first tutorial")
else:
    print("Please run first tutorial to generate data set")

# print dictionary
# print corpus
# models.LdaModel()
model = models.LdaModel(corpus, alpha='auto', id2word=dictionary, num_topics=20)

# corpus_lda = model(corpus)

topics = model.print_topics(num_topics=5, num_words=5)
for topic in topics:
    print topic
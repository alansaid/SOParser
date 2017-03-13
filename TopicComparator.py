from gensim import models
import scipy
from scipy.stats import entropy
from numpy.linalg import norm

def main():
    dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12',
             '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']
    compareMonths(dates)



def compareMonths(dates):
    i = 1
    for month in dates:
        nextmonth = dates[i]
        i += 1
        if i >= len(dates):
            break
        KLDBasedSimilarity(month, nextmonth)
        JSDBasedSimilarity(month, nextmonth)
        intersectionBasedSimilarity(month, nextmonth)

def similarity(month1, month2, simfunc, filename):
    f = open("topics/"+filename+"_" + month1 + "_" + month2 + ".txt", "w")
    lda1topics = prepareDistribution(month1)
    lda2topics = prepareDistribution(month2)
    for lda1topic in lda1topics:
        line = ""
        for lda2topic in lda2topics:
            divergence = simfunc(lda1topic, lda2topic)
            line += "\t" + str(divergence)
        f.write(line + "\n")
    f.close()

def JSDBasedSimilarity(month1, month2):
    similarity(month1, month2, JSD, "jsd")

def KLDBasedSimilarity(month1, month2):
    similarity(month1, month2, scipy.stats.entropy, "kld")

def intersectionBasedSimilarity(month1, month2):
    f = open("topics/intersection_" + month1 + "_" + month2+".txt", "w")
    lda1topics = prepareWordSet(month1)
    lda2topics = prepareWordSet(month2)
    for lda1topic in lda1topics.keys():
        line = ""
        for lda2topic in lda2topics.keys():
            intersection = str(len(set.intersection(lda1topics[lda1topic], lda2topics[lda2topic])))
            line += "\t" + intersection
        f.write(line + "\n")
    f.close()

def JSD(P, Q):
    _P = P / norm(P, ord=1)
    _Q = Q / norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))

def prepareDistribution(month):
    lda = models.LdaModel.load("models/" + month + "-lda.model")
    ldalist = lda.show_topics(num_topics=20, num_words=2000, log=False, formatted=False)
    sorted_topics = [sorted(topic[1], key=lambda tup: tup[0]) for topic in ldalist]
    dist = [[words[1] for words in topic] for topic in sorted_topics]
    return dist

def prepareWordSet(month):
    lda = models.LdaModel.load("models/" + month + "-lda.model")
    ldalist = lda.show_topics(num_topics=20, num_words=100, log=False, formatted=False)
    ldatopics = getTopicWordSets(ldalist)
    return ldatopics

def getTopicWordSets(topics):
    topicwords = {}
    for topic in topics:
        topicid = topic[0]
        wordvector = topic[1]
        topicwords[topicid] = set([tup[0] for tup in wordvector if tup[1] > 0.001])
    return topicwords

if __name__ == '__main__':
    main()

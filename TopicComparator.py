from gensim import models
import scipy
from scipy.stats import entropy
from numpy.linalg import norm
from numpy import array



def main():
    global numtopics, vocabsize
    dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12',
             '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']
    dates = ['2013-01', '2013-02'] #, '2013-03', '2013-03']
    numtopics = 40
    vocabsize = 2000
    compareMonths(dates)



def compareMonths(dates):
    i = 1
    for month in dates:
        print month
        nextmonth = dates[i]
        TVDBasedSimilarity(month, nextmonth)
        KLDBasedSimilarity(month, nextmonth)
        JSDBasedSimilarity(month, nextmonth)
        # intersectionBasedSimilarity(month, nextmonth)
        i += 1
        if i >= len(dates):
            break

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

def TVDBasedSimilarity(month1, month2):
    similarity(month1, month2, TVD, "tvd")

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

def TVD(month1, month2):
    m1 = getTopIndexes(month1)
    m2 = getTopIndexes(month2)
    idxs = list(set(m1)|set(m2))
    mo1 = array(month1)[idxs]
    mo2 = array(month2)[idxs]
    return sum(abs(mo1-mo2))/2


def JSD(P, Q):
    _P = P / norm(P, ord=1)
    _Q = Q / norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))

def getTopIndexes(month):
    return sorted(range(len(month)), key=lambda i: month[i])[-20:]

def prepareDistribution(month):
    lda = models.LdaMulticore.load("ldamodels/" + month + "-lda.model")
    ldalist = lda.show_topics(num_topics=numtopics, num_words=vocabsize, log=False, formatted=False)
    sorted_topics = [sorted(topic[1], key=lambda tup: tup[0]) for topic in ldalist]
    dist = [[words[1] for words in topic] for topic in sorted_topics]
    # print [[words[0].encode('utf-8') for words in topic] for topic in sorted_topics]
    return dist

def prepareWordSet(month):
    lda = models.LdaModel.load("ldamodels/" + month + "-lda.model")
    ldalist = lda.show_topics(num_topics=numtopics, num_words=100, log=False, formatted=False)
    ldatopics = getTopicWordSets(ldalist)
    return ldatopics

def getTopicWordSets(topics):
    topicwords = {}
    for topic in topics:
        topicid = topic[0]
        wordvector = topic[1]
        topicwords[topicid] = set([tup[0] for tup in wordvector if tup[1] > 0.001])
    return topicwords

def printTopicWords(month):
    lda = models.LdaModel.load("ldamodels/" + month + "-lda.model")
    topicfile = open("topics/"+month+"-topicwords.txt", "w")
    ldalist = lda.show_topics(num_topics=numtopics, num_words=5, log=False, formatted=False)
    wordlists = { topic[0]: [wordvals[0].encode('utf-8') for wordvals in topic[1]] for topic in ldalist}
    for topic in wordlists.keys():
        line = str(topic) + "\t" + " ".join(wordlists[topic]) + "\n"
        topicfile.write(line)
    topicfile.close()




if __name__ == '__main__':
    main()


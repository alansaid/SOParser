from gensim import models

def main():
    dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12',
             '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']
    i = 1
    for month in dates:
        nextmonth = dates[i]
        i += 1
        if i > len(dates):
            break
        compareTopics(month, nextmonth)



def compareTopics(month1, month2):
    f = open("topics/comparison_" + month1 + "_" + month2+".txt", "w")
    lda1 = models.LdaModel.load("models/" + month1 + "-lda.model")
    lda2 = models.LdaModel.load("models/" + month2 + "-lda.model")

    lda1list = lda1.show_topics(num_topics=20, num_words=100, log=False, formatted=False)
    lda2list = lda2.show_topics(num_topics=20, num_words=100, log=False, formatted=False)

    lda1topics = getTopicWordSets(lda1list)
    lda2topics = getTopicWordSets(lda2list)

    for lda1topic in lda1topics.keys():
        line = ""
        for lda2topic in lda2topics.keys():
            intersection = str(len(set.intersection(lda1topics[lda1topic], lda2topics[lda2topic])))
            # line =  str(lda1topic) + "\t" + str(lda2topic) + "\t " + intersection + "\n"
            line += "\t" + intersection
        f.write(line + "\n")

    f.close()
#

def getTopicWordSets(topics):
    topicwords = {}
    for topic in topics:
        topicid = topic[0]
        wordvector = topic[1]
        topicwords[topicid] = set([tup[0] for tup in wordvector if tup[1] > 0.001])

    return topicwords


if __name__ == '__main__':
    main()

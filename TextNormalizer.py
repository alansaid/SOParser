#!/usr/local/bin/python
# -*- coding: utf-8 -*-


from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer
import string
import json


def main():
    path = '../2014-filtered-posts.tsv'
    normalizedFilePath = '../2014-normalizedPosts.txt'
    parseFile(path, normalizedFilePath)


def parseFile(path, normalizedFilePath):
    file = open(path, 'r')
    normFile = open(normalizedFilePath, 'a')
    for line in file:
        # rowID, creationDate, postTypeId, score, title, text, tags

        lineContent = line.strip().split('\t')
        if len(lineContent) < 6:
            continue
        rowID = lineContent[0]
        creationDate =lineContent[1]
        postTypeId = lineContent[2]
        score = lineContent[3]
        title = lineContent[4]
        text = lineContent[5]
        if len(lineContent) > 6:
            tags = lineContent[6]
        else:
            tags = ''

        # [rowID, creationDate, postTypeId, score, title, text, tags] = line.strip().split('\t')

        normalized_text = normalizeText(text)
        print json.dumps(normalized_text)
        if len(title) > 0:
            normalized_title = normalizeText(title)
        else:
            normalized_title = ''
        line = rowID + '\t' + creationDate + '\t' + postTypeId + '\t' + score + '\t' + normalized_title + '\t' + normalized_text + '\t' + tags + '\n'
        normFile.write(line)
    normFile.close()


def normalizeText(text):
    stop_words = set(stopwords.words('english'))
    text = text = "".join([ch for ch in text if ch not in string.punctuation])
    tokens = word_tokenize(text)
    filtered_tokens = [w for w in tokens if not w in stop_words]
    stemmer = EnglishStemmer()
    stemmed_tokens = [stemmer.stem(w.decode('utf8', 'ignore')) for w in filtered_tokens]
    return stemmed_tokens


# for w in filtered_tokens:
# 	print w.decode('utf8', 'ignore')
# 	print(stemmer.stem(w.decode('utf8', 'ignore')))

if __name__ == '__main__':
    main()

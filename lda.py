import re

import numpy as np
import pandas as pd
import sys
import sys
#print(sys.version)
import jpype
print(jpype.isJVMStarted())
from konlpy.tag import Okt
from gensim import corpora, models
from pymongo import MongoClient
from bson.objectid import ObjectId
sys.path.append(r'C:\Users\admin\anaconda3\Lib\site-packages')

print("실행")
client = MongoClient('mongodb://203.255.92.141:27017', authSource='admin')
db = client['SCIENCEON']
db.list_collection_names()
scienceOn_author = db['Author']
scienceOn_authorPapers = db['AuthorPapers']
scienceOn_rawData = db['Rawdata']
author_cursor = scienceOn_author.find({'name':'유재수', 'inst': '충북대학교'})
for author in author_cursor:
    researcher_ID = author['_id']
print(researcher_ID)
dfPapers = pd.DataFrame(columns=['papers'])
authorPapers_cursor = scienceOn_authorPapers.find({'A_ID':researcher_ID})
for authorPapers in authorPapers_cursor:
    papers = authorPapers['papers']
    for i in range(len(papers)):
        papersID = papers[i]
        objInstance = ObjectId(papersID)
        rawData_cursor = scienceOn_rawData.find({ "_id" : objInstance })
        for document in rawData_cursor:
            if type(document['paper_keyword']) != list:
                new_document = document['title'] + ' ' + document['english_title'] + ' ' + document['abstract'] + ' ' + document['paper_keyword'] + ' ' + document['english_abstract']
                print("new_document",new_document)
            else:
                paper_keyword = ''
                for j in range(len(document['paper_keyword'])):
                    paper_keyword += document['paper_keyword'][j] + ' '
                new_document = document['title'] + ' ' + document['english_title'] + ' ' + document['abstract'] + paper_keyword + document['english_abstract']
               
            df_new_document = pd.DataFrame(data=np.array([[new_document]]), columns=['papers'])
            print("df_new_document \n",df_new_document)
            dfPapers = pd.concat([dfPapers,df_new_document], ignore_index=True)

documents = dfPapers
print("documents \n", documents)
documents['papers'] = documents['papers'].map(lambda x: re.sub(r'[^\w\s]',' ',x))

# Convert the titles to lowercase
documents['papers'] = documents['papers'].map(lambda x: x.lower())

# Print out the first rows of papers
documents['papers'].head()

list_of_documents = list(documents['papers'])
list_of_documents[0]
print("dlrj",list_of_documents)
t = Okt()
pos = lambda d: ['/'.join(p) for p in t.pos(d, stem=True, norm=True)] #t.pos(d, stem=True, norm=True) or t.nouns(d)
texts_ko = [pos(doc) for doc in list_of_documents]
# print("dafsdfa",texts_ko[0])

dictionary_ko = corpora.Dictionary(texts_ko)
dictionary_ko.save('ko.dict')


#from gensim import models
tf_ko = [dictionary_ko.doc2bow(text) for text in texts_ko]
#print("afsdfasdfasdf",tf_ko)
tfidf_model_ko = models.TfidfModel(tf_ko)
tfidf_ko = tfidf_model_ko[tf_ko]
print("tf", tfidf_ko)
print(corpora.MmCorpus.serialize('ko.mm', tfidf_ko)) # save corpus to file for future use

# print first 10 elements of first document's tf-idf vector
print("tesa",tfidf_ko.corpus[0][:10])
# print top 10 elements of first document's tf-idf vector
print(sorted(tfidf_ko.corpus[0], key=lambda x: x[1], reverse=True)[:10])
# print token of most frequent element
print(dictionary_ko.get(51),dictionary_ko.get(3),dictionary_ko.get(29),dictionary_ko.get(46
))
lda_model = models.ldamodel.LdaModel(corpus=tf_ko, id2word=dictionary_ko,num_topics=5)
keywords = lda_model.print_topics(-1,5)
print(keywords)

keywords = []
for topic in lda_model.print_topics(-1,5):
    topic_list = topic[1].split('+')
    for i in range(len(topic_list)):
        count = 0
        words = topic_list[i].split('"')
        for j in range(len(words)):
            if "*" in words[j] or words[j] == "" or words[j] == " ":
                continue
            elif words[j] not in keywords:
                word = words[j].split('/')
                if word[0] not in keywords and word[1] == "Noun":
                    count += 1
                    keywords.append(word[0])
                    break
        if count >= 1:
            break

print(keywords)
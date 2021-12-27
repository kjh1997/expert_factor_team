import re, math, time, threading, logging, datetime, sys, io, queue
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.corpora import Dictionary
from sklearn.pipeline import Pipeline
from gensim.models import TfidfModel
from bson.objectid import ObjectId
from multiprocessing import Pool
from pymongo import MongoClient
from gensim import similarities
from numpy.linalg import norm
from threading import Thread
from random import randint
import scipy.sparse as sp
from time import sleep
from numpy import dot
import pandas as pd
import numpy as np
client = MongoClient('203.255.92.141:27017', connect=False)
ID = client['ID']
ntis_client  = client['NTIS']
scienceon = client['SCIENCEON']

KCI = client.PUBLIC.KCI
SCI = client.PUBLIC.SCI
kDic = {}
sDic = {}
for doc in KCI.find({}) :
    kDic[doc['name']] = doc['IF']
for doc in SCI.find({}) :
    sDic[doc['name']] = doc['IF']


"""
@ Method Name     : getBackdata
@ Method explain  : 크롤링 한 결과가 저장되 있는 DB에서 A_ID, papers 값 도출하는 함수
@ i               : run 함수에서 실행되는 반복문의 i 값
@ dataPerPage     : dataPerPage(100)
@ fid             : filtering id
@ keyID           : key id
"""
def getBackdata(i, dataPerPage, fid, keyID):
    #Domestic AuthorPapers
    sCount  = i * dataPerPage
    lCoount = dataPerPage
    
    getBackdata = []
    
    for doc in ID['Domestic'].find({"keyId":keyID, "fid":fid}, {"NTIS":1,"Scienceon":1}).skip(sCount).limit(lCoount):      
        papersNumber = 0
        getBackdataDic = {}
        
        if ("NTIS" in doc):
            getBackdataDic['ntis'] = doc['NTIS']['A_id']
            getBackdataDic['ntis papers'] = doc['NTIS']['papers']
            papersNumber += len(doc['NTIS']['papers'])
        else:
            getBackdataDic['ntis'] = None
            getBackdataDic['ntis papers'] = []
                    
        if ("Scienceon" in doc):
            getBackdataDic['scienceon'] = doc['Scienceon']['A_id']
            getBackdataDic['Scienceon papers'] = doc['Scienceon']['papers']
            papersNumber += len(doc['Scienceon']['papers'])
        else:
            getBackdataDic['scienceon'] = None
            getBackdataDic['scienceon papers'] = []
        
        getBackdataDic['number'] = papersNumber
        getBackdata.append(getBackdataDic)
    return  getBackdata

def getRawBackdata(getBackdata):
    pYears = [] #NTIS & SCIENCEON
    keywords = [] #NTIS & SCIENCEON
    qty = [] #NTIS & SCIENCEON
    totalFunds = [] #NTIS
    mngIds = [] #NTIS
    ntis_id = [] #NTIS
    authorInsts = [] #SCIENCEON
    authors = [] #SCIENCEON
    issueInsts = [] #SCIENCEON
    issueLangs = [] #SCIENCEON
    citation = [] #SCIENCEON
    scienceon_id = [] #SCIENCEON
    querykey = []
    for i in range(len(getBackdata) - 1, -1, -1):
        _pYear = [] #NTIS & SCIENCEON
        _keywords = [] #NTIS & SCIENCEON
        
        fund_list = [] #NTIS
        _mngIds = [] #NTIS
        __keyword = [] #NTIS
        
        _keyword = [] #SCIENCEON
        _authorInsts = [] #SCIENCEON
        _authors = [] #SCIENCEON
        _issueInsts = [] #SCIENCEON
        _issueLangs = [] #SCIENCEON
        _citation = [] #SCIENCEON
        _scienceon_id = [] #SCIENCEON
        
        #NTIS
        if (getBackdata[i]['ntis'] != None):
            ntis_id.insert(0,getBackdata[i]['ntis'])
            for doc in ntis_client['Rawdata'].find({"keyId": 588, "_id": {"$in" : getBackdata[i]['ntis papers']}}):
                fund_list.append(math.log(int(doc['totalFund'])+1))
                _mngIds.append(doc['mngId'])
                for j in doc['qryKeyword']:
                    if j not in querykey:
                        querykey.append(j)
                    
                if doc['prdEnd'] != 'null':
                    _pYear.append(int(doc['prdEnd'][0:4]))
                elif (doc['prdEnd'] == 'null') and (doc['prdStart'] != 'null'):
                    _pYear.append(int(doc['prdStart'][0:4]))
                else:
                    _pYear.append(int(2000))
                __keyword.append(doc['koTitle'])
                __keyword.append(doc['enTitle'])
                __keyword.append(doc['koKeyword'])
                __keyword.append(doc['enKeyword'])
            if len(__keyword) != 0 :
                _keywords.insert(0, __keyword)
                totalFunds.insert(0, sum(fund_list))
                mngIds.insert(0, _mngIds)
                #keywords.insert(0, _keywords)
                #pYears.insert(0, _pYear)
        else:
            ntis_id.insert(0,None)
            totalFunds.insert(0,0)
            mngIds.insert(0,_mngIds)
            
        #SCIENCEON
        if (getBackdata[i]['scienceon'] != None):
            for doc in scienceon['Rawdata'].find({"keyId": 588, "_id": {"$in" : getBackdata[i]['Scienceon papers']}}):
                _keyword.append(doc['title'])
                _keyword.append(doc['english_title'])
                _keyword.append(doc['paper_keyword'])
                _keyword.append(doc['abstract'])
                _keyword.append(doc['english_abstract'])
                _pYear.append(int(doc['issue_year'][0:4]))
                _authorInsts.append(doc['author_inst'])
                _authors.append(doc['author_id']) #= doc['author_id'].split(';')
                _issueInsts.append(doc['issue_inst'])
                _issueLangs.append(doc['issue_lang'])
                _citation.append(int(doc['citation']))
                    
            for k in range(len(getBackdata[i]['scienceon'])):
                scienceon_id.insert(0,getBackdata[i]['scienceon'][k])
                    
            if len(_keyword) != 0 :
                authorInsts.insert(0,_authorInsts)
                authors.insert(0, _authors)
                issueInsts.insert(0, _issueInsts)
                _keywords.insert(0,_keyword)
                #pYears.insert(0,_pYear)
                issueLangs.insert(0,_issueLangs)
                #keywords.insert(0,_keywords)
                citation.insert(0,_citation)
        else:
            issueInsts.insert(0,_issueInsts)
            issueLangs.insert(0,_issueLangs)
            citation.insert(0,_citation)
            authors.insert(0,"scienceon"+str(i))
            scienceon_id.insert(0,"sco"+str(i))
            authorInsts.insert(0,_authorInsts)
            
        pYears.insert(0,_pYear)
        keywords.insert(0, _keywords)
        qty.insert(0,getBackdata[i]['number'])
            
    return pYears, keywords, totalFunds, {'mngIds' : mngIds, 'A_ID' : ntis_id}, None, {'issueInsts' : issueInsts, 'issueLangs' : issueLangs, 'citation' : citation}, {'authors' : authors, 'A_ID' : scienceon_id  }, authorInsts, qty, querykey
    
(pYears, keywords, _ntisQtyBackdata, _ntisContBackdata, _ntisCoopBackdata, _sconQtyBackdata, _sconContBackdata, _sconCoopBackdata, qty, querykey) = getRawBackdata(getBackdata(0,100, 0, 588))




def recentness(pYears):
    dt = datetime.datetime.now()
    rct_list = []
    for i in range(len(pYears)):
        rct = 0
        for j in range(len(pYears[i])):
            if pYears[i][j] >= int(dt.year)-2: # 최신년도 기준으로 과거 2년까지 +1점
                rct += 1
            elif int(dt.year)-15 < pYears[i][j] <= int(dt.year)-3: # 최신년도 기준 과거 15년 ~ 과거 2년까지 
                rct += max(round((1-(int(dt.year)-3-pYears[i][j])*0.1),2), 0)
            else:
                rct += 0
        rct_list.append(rct / len(pYears[i]))
    return rct_list


rctt = recentness(pYears)

"""
@ Method Name     : career
@ Method explain  : 경력을 계산해 주는 함수
@ pYears          : (1) NTIS : 프로젝트 시작년도 (2) 나머지 : 논문 발행년도
"""
def career(pYears):
    crr_list = []
    for i in range(len(pYears)):
        _max = max(pYears[i])
        _min = min(pYears[i])
        crr = _max-_min+1
        crr_list.append(crr)
    return crr_list






crrt = career(pYears)


"""
@ Method Name     : durability
@ Method explain  : 연구지속성 계산해 주는 함수
@ pYears          : (1) NTIS : 프로젝트 시작년도 (2) 나머지 : 논문 발행년도
"""
def durability(pYears):
    maxLen = []
    for i in range(len(pYears)):
        pYears[i].sort(reverse=True)
        packet = []
        tmp = []
        v = pYears[i].pop()
        tmp.append(v)
        while(len(pYears[i])>0):
            vv = pYears[i].pop()
            if v+1 == vv:
                tmp.append(vv)
                v = vv
            elif v == vv:
                pass
            else:
                packet.append(tmp)
                tmp = []
                tmp.append(vv)
                v = vv
        packet.append(tmp)
        maxLen.append(packet)

    xx_list = []
    for i in range(len(maxLen)):
        x = []
        for j in range(len(maxLen[i])):
            x.append(len(maxLen[i][j]))
        xx_list.append(max(x))
    return xx_list

durat = durability(pYears)



"""
@ Method Name     : coop
@ Method explain  : 협업도 계산 함수
@ _contBackdata   : getRawBackdata 함수에서 mngIds, A_ID 값을 가지고 있는 변수
"""
def coop(_coopBackdata):
    oemList = ["Hyundai", "Kia","Toyota","Honda","Nissan","General Motors", "Chevrolet","Ford motor", "Volkswagen", "Audi", "BMW", "Bayerische Motoren Werke", "Mercedes-Benz", "daimler", "Volvo", "Renault", "Jaguar", "Acura", "Mazda", "Subaru", "Suzuki", "Isuzu","Daihatsu","Peugeot","Mclaren", "Bugatti", "Rolls Royce", "Bentley", "Aston Martin", "Land Rover", "Lotus","Lexus",   "Infiniti", "Datson", "Mitsubishi", "Mitsuoka","Great Wall","Cadillac", "Tesla", "Jeep", "Dodge", "Chrysler","Porsche", "Opel", "Borgward", "Gumfut", "FIAT", "Ferrari", "Lamborghini", "Maserati","Peugeot"]
    score = []
    for i in range(len(_coopBackdata)):
        point = 0
        for insts in _coopBackdata[i]:
            if insts != None :
                for oem in oemList :
                    if oem in insts:
                        point = point + 1
                        break
        score.append(point)
    return score



coop = coop(_sconCoopBackdata)


"""
@ Method Name     : cont
@ Method explain  : 기여도 계산 함수
@ _contBackdata   : getRawBackdata 함수에서 mngIds, A_ID 값을 가지고 있는 변수 NTIS
"""
def ntiscont(_contBackdata):
    mngIds = _contBackdata['mngIds']
    A_ID   = _contBackdata['A_ID']
    point  = []
    for i in range(len(mngIds)):
        pt = 0
        temp = 0
        for j in range(len(mngIds[i])):
            if mngIds[i][j] != None:
                if A_ID[i] == mngIds[i][j] :
                    pt += 10
                else:
                    temp += 1
        if pt > 0 : 
            pt += temp
        point.append(pt)
    return point

"""
@ Method Name     : cont
@ Method explain  : 기여도 계산 함수
@ _contBackdata   : getRawBackdata 함수에서 mngIds, A_ID 값을 가지고 있는 변수 SCIENCEON
"""
def scocont(_contBackdata):
    authors = _contBackdata['authors']
    A_ID = _contBackdata['A_ID']
    aidToDict = {i : 0 for i in A_ID}

    for i in range(len(authors)):
        for j in  range(len(authors[i])) :
            x = authors[i][j].split(';')
            for author in enumerate(x):
                if author[1] in aidToDict and author[1] == A_ID[i]:
                    if author[0] == 0:
                        aidToDict[author[1]] += 1.0
                    elif author[0] == len(x)-1:
                        aidToDict[author[1]] += 3.0
                    else :
                        aidToDict[author[1]] += ((author[0]+1)/len(x))
    return list(aidToDict.values())



contrib = []
for i in range(len(scocont(_sconContBackdata))):
    contrib.append(ntiscont(_ntisContBackdata)[i]+scocont(_sconContBackdata)[i])
print(contrib)


contBit  = [1 if i > 0 else i for i in contrib]


"""
@ Method Name     : 품질 / quality
@ Method explain  : analyzerProject, analyzerPaper 에서 다시 정의 / Redefined in analyzer Project, analyzer Paper
@ totalFunds      : 프로젝트 연구비 / project research funds NTIS
"""
def ntisquality(totalFunds):
    return totalFunds

"""
@ Method Name     : cont
@ Method explain  : 기여도 계산 함수
@ _contBackdata   : getRawBackdata 함수에서 mngIds, A_ID 값을 가지고 있는 변수 SCIENCEON
"""
def scoquality(_qtyBackdata):
    issueInsts = _qtyBackdata['issueInsts']
    issueLangs = _qtyBackdata['issueLangs']
    citation   = _qtyBackdata['citation']

    IF = []
    for i in range(len(issueInsts)):
        tempIF = 0
        for j in range(len(issueInsts[i])):
            temp = None
            tempIFIF = 0
            n = 1
            if issueLangs[i][j] == 'kor':
                if isinstance(issueInsts[i][j], str) :
                    tempIFIF = kDic.get(issueInsts[i][j],0)
            else:
                if isinstance(issueInsts[i][j], str) :
                    tempIFIF = sDic.get(issueInsts[i][j],0)
                n = 3

            tempIF += math.log(((citation[i][j]*n)+1) * (tempIFIF+1.1))
        IF.append(tempIF)
    return IF



qual = []
for i in range(len(scoquality(_sconQtyBackdata))):
    qual.append(ntisquality(_ntisQtyBackdata)[i]+scoquality(_sconQtyBackdata)[i])
print(qual)



"""
@ Method Name     : cos_sim
@ Method explain  : 코사인 유사도 함수 
@ A               : calAcc 함수에서 arr[np.argmax(arr.sum(axis=1))]
@ B               : calAcc 함수에서 qrytfidf
"""
def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))




"""
@ Method Name     : calAcc
@ Method explain  : 정확도 계산 함수(실제 acc 함수에서 각 논문/프로젝트 정확도 계산)
@ keywords        : 1) 논문 제목, 프로젝트 키워드 (in project) 
                    2) 논문 제목, 논문 키워드, abstract (in paper)
"""
def calAcc(keywords):
    flat_list = []
    for sublist in keywords :
        for item in sublist :
            if item is not None and item != 'None' and item != "" and isinstance(item, str) :
                flat_list.append(item)
    if len(flat_list) == 0 :
        return 0 

    qs = querykey #What is this ?
    qs = [_qs for _qs in qs if len(_qs) >= 2]
    tfidf_vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1))
    tfidf_vectorizer.fit(querykey)

    arr = tfidf_vectorizer.transform(flat_list).toarray()
    qrytfidf = [1] *len(qs)
    if sum(arr[np.argmax(arr.sum(axis=1))]) != 0:
        return cos_sim(arr[np.argmax(arr.sum(axis=1))], qrytfidf)
    else :
        return 0


"""
@ Method Name     : acc
@ Method explain  : 정확도 계산 함수
@ keywords        : 1) 논문 제목, 프로젝트 키워드 (in project) 
                    2) 논문 제목, 논문 키워드, abstract (in paper)
@ contBit         : contrib 값에서 0을 제외한 값
"""
def acc(keywords, contBit):
    rtv = contBit.copy()
    for i in range(len(keywords)):
        #try :
        if rtv[i] != 0:
            temp = calAcc(keywords[i])
            if temp == 0.0 :
                rtv[i] = 0.02 #Where is defaultScore
            else :
                rtv[i] = temp
        """
        except Exception as e :
            print(keywords[i])
            print(e)
        """
    return rtv
accuracy = acc(keywords, contBit)
print(accuracy)

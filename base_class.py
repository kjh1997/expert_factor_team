import re, math, time, threading, logging, datetime, sys, io, queue
import pymongo
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

'''
A_ID : 저자 고유 ID
keyID : 검색한 결과의 고유 id


querykey : 웹에서 입력받은 검색 키워드
cont : 기여도 // 삭제
qty : 생산성 // 삭제
durat : 연구지속성
accuracy : 정확도   // 


contbit : contrib 값에서 0을 제외한 값 
durability : 연구지속성 // 삭제 /  durability(지속성) / crrt(경력) * contbit
 ---------------------------------------------------------------------------------------------
recentness : 최신성 /  recentness함수 //
mean { f(과제 시작/ 종료 연도) } (3년 이내 가중치 ↑) +  mean { f(논문 출간 연도) } (3년 이내 가중치 ↑) 
                              ↓↓↓↓↓↓↓↓↓↓↓↓↓↓

 f(mean{논문/과제 연도}) + norm((mean{논문/과제 연도} ± 𝑛년 이내 연구 성과 수(기여도 반영)))

coop  : 협업도  // 변화 x 
qual : 품질 // 다른함수 ,x
acc : 정확성 // 키워드, contbit
'''
def run(i, dataPerPage, fid, keyID):
    a = factor_integration()
    #print("정상실행??", sys.argv)
   # (i, dataPerPage, fid, keyID) = sys.argv[1],sys.argv[2], sys.argv[3], sys.argv[4]
    data = a.getBackdata(i, dataPerPage, fid, keyID)
    print(i)
    #print("data", data)
    (pYears, keywords, _ntisQtyBackdata, _ntisContBackdata, _ntisCoopBackdata, _sconQtyBackdata, _sconContBackdata, _sconCoopBackdata, qty, querykey) = a.getRawBackdata(data)
    #print(pYears, keywords, _ntisQtyBackdata, _ntisContBackdata, _ntisCoopBackdata)
    #print(keywords)
    contrib = []
    qual = []
    
    for i in range(len(a.scoquality(_sconQtyBackdata))):
        qual.append(a.ntisquality(_ntisQtyBackdata)[i]+a.scoquality(_sconQtyBackdata)[i])
    
    for i in range(len(a.scocont(_sconContBackdata))):
        contrib.append(a.ntiscont(_ntisContBackdata)[i]+a.scocont(_sconContBackdata)[i])
   # print(contrib)


    contBit  = [1 if i > 0 else i for i in contrib]
    accuracy = a.acc(keywords, contBit, querykey)
    
    print("품질 : ", qual)
    print("정확성 : ", accuracy)
    print("협업도 : ", a.coop(_sconCoopBackdata))
    print("생산성, 기여도, 최신성, 연구지속성 : ", a.recentness(pYears))


class factor_integration:
    def __init__(self):
        self.client = MongoClient('203.255.92.141:27017', connect=False)
        self.ID = self.client['ID']
        self.ntis_client  = self.client['NTIS']
        self.scienceon = self.client['SCIENCEON']

        self.KCI = self.client.PUBLIC.KCI
        self.SCI = self.client.PUBLIC.SCI
        self.kDic = {}
        self.sDic = {}
        for doc in self.KCI.find({}) :
            self.kDic[doc['name']] = doc['IF']
        for doc in self.SCI.find({}) :
            self.sDic[doc['name']] = doc['IF']
    
    

    def getBackdata(self, i, dataPerPage, fid, keyID):
    #Domestic AuthorPapers
        print("실행됐나?")
        # print(i, dataPerPage, fid, keyID)
        # print(type(int(i)))
        # print(type(int(dataPerPage)))
        # print(type(int(fid)))
        # print(type(int(keyID)))
        sCount  = int(i)
        lCoount = int(dataPerPage)
        
        getBackdata = []
        
        for doc in self.ID['Domestic'].find({"keyId":keyID, "fid":fid}).skip(i).limit(dataPerPage):      
            #print(doc)
            papersNumber = 0
            getBackdataDic = {}
           # print("doc", doc)
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
        
    def getRawBackdata(self, getBackdata):
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
                for doc in self.ntis_client['Rawdata'].find({"keyId": 632, "_id": {"$in" : getBackdata[i]['ntis papers']}}):
                    fund_list.append(math.log(float(doc['totalFund'])+1))
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
                for doc in self.scienceon['Rawdata'].find({"keyId": 632, "_id": {"$in" : getBackdata[i]['Scienceon papers']}}):
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
    
    def recentness(self, pYears):
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

    def career(pYears):
        crr_list = []
        for i in range(len(pYears)):
            _max = max(pYears[i])
            _min = min(pYears[i])
            crr = _max-_min+1
            crr_list.append(crr)
        return crr_list

    
    
    def coop(self, _coopBackdata):
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
    
    def ntiscont(self, _contBackdata):
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
    
    def scocont(self, _contBackdata):
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

    def ntisquality(self, totalFunds):
        return totalFunds
    
    def scoquality(self, _qtyBackdata):
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
                        tempIFIF = self.kDic.get(issueInsts[i][j],0)
                else:
                    if isinstance(issueInsts[i][j], str) :
                        tempIFIF = self.sDic.get(issueInsts[i][j],0)
                    n = 3

                tempIF += math.log(((citation[i][j]*n)+1) * (tempIFIF+1.1))
            IF.append(tempIF*0.5)
        return IF
    
    def cos_sim(A, B):
        return dot(A, B)/(norm(A)*norm(B))

    
    
    def acc(self, keywords, contBit, querykey):
        rtv = contBit.copy()
        for i in range(len(keywords)):
            #try :
            if rtv[i] != 0:
                temp = calAcc(keywords[i], querykey)
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
def calAcc(keywords, querykey):
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

def cos_sim(A, B):
        return dot(A, B)/(norm(A)*norm(B))

    


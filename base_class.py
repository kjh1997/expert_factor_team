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
from statistics import mean 

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
    data, object_data = a.getBackdata(i, dataPerPage, fid, keyID)
    (pYears, keywords, _ntisQtyBackdata, _ntisContBackdata, _ntisCoopBackdata, _sconQtyBackdata, _sconContBackdata, _sconCoopBackdata,_KCIconQtyBackdata, _KCIContBackdata, _KCICoopBackdata, qty, querykey) = a.getRawBackdata(data,keyID, object_data)
    # return pYears, keywords, totalFunds, {'mngIds' : mngIds, 'A_ID' : ntis_id}, None, {'issueInsts' : issueInsts1, 'issueLangs' : issueLangs1, 'citation' : citation1}, {'authors' : authors1, 'A_ID' : scienceon_id  }, authorInsts1, {'issueInsts' : issueInsts2, 'issueLangs' : issueLangs2, 'citation' : citation2}, {'authors' : authors2, 'A_ID' : KCI_id  }, authorInsts2, qty, querykey
    #rint("len", len(_sconQtyBackdata))
    contrib = []
    print(object_data)
    qual = []
    print("len",len(_KCIconQtyBackdata['issueInsts']))
    print("len",len(_sconQtyBackdata['issueInsts']))
    print("len",len(_ntisQtyBackdata))
    for i in range(len(a.scoquality(_sconQtyBackdata))):
        qual.append(a.ntisquality(_ntisQtyBackdata)[i]+a.scoquality(_sconQtyBackdata)[i]+a.scoquality(_KCIconQtyBackdata)[i])

   

    for i in range(len(a.scocont(_sconContBackdata))):
       
        contrib.append(a.ntiscont(_ntisContBackdata)[i]+a.scocont(_sconContBackdata)[i]+a.scocont(_KCIContBackdata)[i])
   # print(contrib)
    coop = []
    scoop = a.coop(_sconCoopBackdata)
    kcoop = a.coop(_KCICoopBackdata)
    for i in range(len(_sconCoopBackdata)):
        coop.append(scoop[i] + kcoop[i])
    contBit  = [1 if i > 0 else i for i in contrib]
    accuracy = a.acc(keywords, contBit, querykey)
    recentness = a.recentness(pYears)
    print("품질 : ", qual)
    print("정확성 : ", accuracy)
    print("협업도 : ", coop)
    print("생산성, 기여도, 최신성, 연구지속성 : ", recentness)

    a.insert_max_factor(qual, accuracy, coop, recentness,keyID)
    for num, i in enumerate(object_data):
        data = {'qual':qual[num],'accuracy':accuracy[num], 'coop':coop[num],'recentness':recentness[num]}
        print(data, i)
        a.update_domestic(i,data)






class factor_integration:
    def __init__(self):
        self.client = MongoClient('203.255.92.141:27017', connect=False)
        self.ID = self.client['ID']
        self.PUBLIC = self.client['PUBLIC']
        self.new_max_factor = self.PUBLIC['new_factor'] 
        self.ntis_client  = self.client['NTIS']
        self.scienceon = self.client['SCIENCEON']
        self.KCI_main = self.client['KCI']
        self.keyId = ""
        self.KCI = self.client.PUBLIC.KCI
        self.SCI = self.client.PUBLIC.SCI
        self.kDic = {}
        self.sDic = {}
        for doc in self.KCI.find({}) :
            self.kDic[doc['name']] = doc['IF']
        for doc in self.SCI.find({}) :
            self.sDic[doc['name']] = doc['IF']
    def update_domestic(self, id, data):
        self.ID['Domestic'].update_one({'_id':ObjectId(id)},{"$set":{'factor':data}})

    def insert_max_factor(self, qual, accuracy, coop, pYears,keyID):
        
        qual = max(qual)
        accuracy = max(accuracy)
        coop = max(coop)
        recentness = max(pYears)
        keyId = keyID
        maxFactors = {'keyId': self.keyId, 'Quality' : qual, 'accuracy' : accuracy, 'recentness' : recentness, 'coop': coop }
     
        self.new_max_factor.update({"keyId" : keyId}, {'$max':{"Quality":qual}})
        self.new_max_factor.update({"keyId" : keyId}, {'$max':{"accuracy":accuracy}})
        self.new_max_factor.update({"keyId" : keyId}, {'$max':{"recentness":recentness}})
        self.new_max_factor.update({"keyId" : keyId}, {'$max':{"coop":coop}})
       
        # try:
        #     self.new_max_factor.update({"_id" : self.keyId}, {"$max" : 
        # except Exception as e:   
        #     self.new_max_factor.append(xFactors)
        
        

    def getBackdata(self, i, dataPerPage, fid, keyID):
        self.keyID = keyID
        print("RUN!!!",i)
        
        sCount  = int(i)
        lCoount = int(dataPerPage)
        objectid_data = []   
        getBackdata = []
        
        for doc in self.ID['Domestic'].find({"keyId":keyID, "fid":fid}).skip(i).limit(dataPerPage):      
            papersNumber = 0
            getBackdataDic = {}
            objectid_data.append(doc['_id'])
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

            if ("KCI" in doc):
                getBackdataDic['KCI'] = doc['KCI']['A_id']
                getBackdataDic['KCI papers'] = doc['KCI']['papers']
                papersNumber += len(doc['KCI']['papers'])
            else:
                getBackdataDic['KCI'] = None
                getBackdataDic['KCI papers'] = []    
            
            getBackdataDic['number'] = papersNumber
            getBackdata.append(getBackdataDic)
           
        return  getBackdata, objectid_data
        
    def getRawBackdata(self, getBackdata, keyID, object_data):

        pYears = [] #NTIS & SCIENCEON
        keywords = [] #NTIS & SCIENCEON
        qty = [] #NTIS & SCIENCEON
        totalFunds = [] #NTIS
        mngIds = [] #NTIS
        ntis_id = [] #NTIS
        authorInsts1 = [] #SCIENCEON
        authors1 = [] #SCIENCEON
        issueInsts1 = [] #SCIENCEON
        issueLangs1 = [] #SCIENCEON
        citation1 = [] #SCIENCEON
        scienceon_id = [] #SCIENCEON
        authorInsts2 = [] #KCI
        authors2 = [] #KCI
        issueInsts2 = [] #KCI
        issueLangs2 = [] #KCI
        citation2 = [] #KCI
        KCI_id = [] #KCI
        querykey = []
        all_citation = []
        cnt = 0
        for i in range(len(getBackdata) - 1, -1, -1):
            cnt += 1
            _pYear = [] #NTIS & SCIENCEON & KCI
            _keywords = [] #NTIS & SCIENCEON & KCI
            
            fund_list = [] #NTIS
            _mngIds = [] #NTIS
            __keyword = [] #NTIS
            
            _keyword1 = [] #SCIENCEON
            _authorInsts1 = [] #SCIENCEON
            _authors1 = [] #SCIENCEON
            _issueInsts1 = [] #SCIENCEON
            _issueLangs1 = [] #SCIENCEON
            _citation1 = [] #SCIENCEON
            _scienceon_id = [] #SCIENCEON
            _keyword2 = [] #KCI
            _authorInsts2 = [] #KCI
            _authors2 = [] #KCI
            _issueInsts2 = [] #KCI
            _issueLangs2 = [] #KCI
            _citation2 = [] #KCI
            _KCI_id = [] #KCI
            _citation = []
            #NTIS
            if (getBackdata[i]['ntis'] != None):
                ntis_id.append(getBackdata[i]['ntis'])
                for doc in self.ntis_client['Rawdata'].find({"keyId": keyID, "_id": {"$in" : getBackdata[i]['ntis papers']}}):
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
                    _keywords.append( __keyword)
                    totalFunds.append( sum(fund_list))
                    mngIds.append( _mngIds)
                    #keywords.append( _keywords)
                    #pYears.append( _pYear)
            else:
                ntis_id.append(None)
                totalFunds.append(0)
                mngIds.append(_mngIds)
                
            #SCIENCEON
            if (getBackdata[i]['scienceon'] != None):
                scienceon_id.append(getBackdata[i]['scienceon'])
                for doc in self.scienceon['Rawdata'].find({"keyId": keyID, "_id": {"$in" : getBackdata[i]['Scienceon papers']}}):
                    _keyword1.append(doc['title'])
                    _keyword1.append(doc['english_title'])
                    _keyword1.append(doc['paper_keyword'])
                    _keyword1.append(doc['abstract'])
                    _keyword1.append(doc['english_abstract'])
                    _pYear.append(int(doc['issue_year'][0:4]))
                    _authorInsts1.append(doc['author_inst'])
                    _authors1.append(doc['author_id']) #= doc['author_id'].split(';')
                    _issueInsts1.append(doc['issue_inst'])
                    _issueLangs1.append(doc['issue_lang'])

                    _citation1.append(int(doc['citation']))
                    _citation.append(int(doc['citation']))
                        
            
                        
                if len(_keyword1) != 0 :
                    authorInsts1.append(_authorInsts1)
                    authors1.append( _authors1)
                    issueInsts1.append( _issueInsts1)
                    _keywords.append(_keyword1)
                    #pYears.append(_pYear)
                    issueLangs1.append(_issueLangs1)
                    #keywords.append(_keywords)
                    citation1.append(_citation1)
            else:
                issueInsts1.append(_issueInsts1)
                issueLangs1.append(_issueLangs1)
                citation1.append(_citation1)
                authors1.append("scienceon"+str(i))
                scienceon_id.append("sco"+str(i))
                authorInsts1.append(_authorInsts1)
            # KCI
            if (getBackdata[i]['KCI'] != None):
                
                KCI_id.append(getBackdata[i]['KCI'])
                for doc in self.KCI_main['Rawdata'].find({"keyId": keyID, "_id": {"$in" : getBackdata[i]['KCI papers']}}):
                    _keyword2.append(doc['title'])
                    _keyword2.append(doc['english_title'])
                    _keyword2.append(doc['paper_keyword'])
                    _keyword2.append(doc['abstract'])
                    _keyword2.append(doc['english_abstract'])
                    _pYear.append(int(doc['issue_year'][0:4]))
                    _authorInsts2.append(doc['author_inst'])
                    _authors2.append(doc['author_id']) #= doc['author_id'].split(';')
                    _issueInsts2.append(doc['issue_inst'])
                    _issueLangs2.append(doc['issue_lang'])
                    _citation2.append(int(doc['citation']))
                    _citation.append(int(doc['citation']))
                        
            
                        
                if len(_keyword2) != 0 :
                    authorInsts2.append(_authorInsts2)
                    authors2.append(_authors2)
                    issueInsts2.append( _issueInsts2)
                    _keywords.append(_keyword2)
                    issueLangs2.append(_issueLangs2)
                    citation2.append(_citation2)
            else:
                issueInsts2.append(_issueInsts2)
                issueLangs2.append(_issueLangs2)
                citation2.append(_citation2)
                authors2.append("kci"+str(i))
                KCI_id.append("kci"+str(i))
                authorInsts2.append(_authorInsts2)

  
            pYears.append(_pYear)
            keywords.append( _keywords)
            qty.append(getBackdata[i]['number'])
                
        return pYears, keywords, totalFunds, {'mngIds' : mngIds, 'A_ID' : ntis_id}, None, {'issueInsts' : issueInsts1, 'issueLangs' : issueLangs1, 'citation' : citation1}, {'authors' : authors1, 'A_ID' : scienceon_id  }, authorInsts1, {'issueInsts' : issueInsts2, 'issueLangs' : issueLangs2, 'citation' : citation2}, {'authors' : authors2, 'A_ID' : KCI_id  }, authorInsts2, qty, querykey
    
    def recentness(self, pYears):
        dt = datetime.datetime.now()
        rct_list = []
        for i in range(len(pYears)):
            rct = 0
            try:
                year_avg = sum(pYears[i]) / len(pYears[i])
            except Exception as e:
                rct_list.append(0)
                continue
            for j in range(len(pYears[i])):
                if (year_avg - 5 < pYears[i][j] < year_avg + 5):
                    if pYears[i][j] >= int(dt.year)-2: # 최신년도 기준으로 과거 2년까지 +1점
                        rct += 1
                    elif int(dt.year)-15 < pYears[i][j] <= int(dt.year)-3: # 최신년도 기준 과거 15년 ~ 과거 2년까지 
                        rct += max(round((1-(int(dt.year)-3-pYears[i][j])*0.1),2), 0)
                    else:
                        rct += 0
            if len(pYears[i]) != 0:
                rct_list.append(rct / len(pYears[i]))
            else:
                rct_list.append(0)
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
        print(len(rtv), len(keywords))
        for i in range(len(keywords)):
            #try :
          #  print('rtv',rtv[i])
            if rtv[i] != 0:
               # print("keywords", keywords[i])
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
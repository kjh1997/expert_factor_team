from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
import time, math, datetime
import numpy as np
from numpy import dot

client = MongoClient('203.255.92.141:27017', connect=False)
ID = client['ID']
ID_Domestic = ID['Domestic']
ntis_client  = client['NTIS']
ntis_rawdata = ntis_client['Rawdata']
scienceon = client['SCIENCEON']
scienceon_authorpapers = scienceon['AuthorPapers']
scienceon_rawdata = scienceon['Rawdata']

def getRawBackdata(data, A_ID):
    pYears = []
    keywords = []
    totalFunds = []
    mngIds = []
    qry = []

    
    _pYear = []
    _keywords = []
    fund_list = []
    _mngIds = []
    __keyword = []
    for doc in data:
        fund_list.append(math.log(int(doc['totalFund'])+1))
        _mngIds.append(doc['mngId'])

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
        keywords.insert(0, _keywords)
        pYears.insert(0, _pYear)
   #     print("totalFunds",totalFunds )
  #  print({'mngIds' : mngIds, 'A_ID' : A_ID})    
    return pYears, keywords, totalFunds, {'mngIds' : mngIds, 'A_ID' : A_ID}, None

def storeExpertFactors(A_ID, rctt, crrt, durat, contrib, qual, qt, accuracy, coop, contBit, papers):
   # print("실행" , "A_ID", A_ID, "rctt", rctt, "crrt",  crrt, "durat", durat, "contrib",  contrib,"qual", qual,"qt",  qt,"accuracy", accuracy, "coop", coop, "contBit", contBit)
    expf = []
    

    exp = {}
    exp['A_ID']         = A_ID
    exp['keyId']        = 519
    exp['Productivity'] = qt[0] * contBit[0]
    exp['Contrib']      = contrib[0]
    exp['Durability']   = (durat[0]/crrt[0]) * contBit[0]
    exp['Recentness']   = rctt[0] * contBit[0]
    if coop is None :
        exp['Coop']     = 0
    else :
        exp['Coop']     = coop[0] * contBit[0]
    exp['Quality']      = qual[0] * contBit[0]
    exp['Acc']          = accuracy[0]
    exp['Numpaper']     = len(papers)
    expf.append(exp)
    #print("결과", expf)
    
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



AuthorPapers_A_ID_AND_Papers = list(ntis_client['AuthorPapers'].find({'keyId':519}, {'A_ID':1,"papers":1}))
# keyid를 정해서 authorpapers 컬렉션에 검색한다.
scienceon_id = []
author_paper_data_dict = {}
ntis_data = []

for A_ID_Data in AuthorPapers_A_ID_AND_Papers[0:5]:
    scienceon_author = []
    papers_data = []
    scienceon_data = []
    ntis_data = []
    #scienceon_data.append({"A_id": A_ID_Data['zA_ID']})
    ntis_paper_cnt = 0
    paper_cnt = []
    # keyid 519로 검색했을 경우의 논문
    for id_paper in A_ID_Data['papers']:
        
        
        ntis_paper_data = list(ntis_rawdata.find({"_id":id_paper},{"koTitle":1,"enTitle":1,"absAbs":1,"effAbs":1,"koKeyword":1,"enKeyword":1,"goalAbs":1,
        'totalFund':1,"mngId":1,"prdEnd":1,"prdStart":1,"qryKeyword":1}))
        ntis_data.append(ntis_paper_data[0])
        ntis_paper_cnt += 1 
    #-----------------------------------------------------    
    if ntis_paper_cnt >= 1:
        paper_cnt.append(ntis_paper_cnt) # 저자에 대한 ntis 논문 수
    else:
        paper_cnt.append(0)
    # keyid 519로 검색했을 경우 나오는 a_id에 대한 scienceon의 id
    author = ID_Domestic.find({"ntis":A_ID_Data['A_ID']},{"scienceon":1,"ntis":1})
    for id in author:
        
        if id == []:
            continue
        #print(id)
        for scienceon_id in id["scienceon"]:
            scienceon_author.append(scienceon_id)
            a = list(scienceon_authorpapers.find({"A_ID":scienceon_id},{"papers":1}))
            scienceon_paper_cnt = 0
       
            for num,scienceon_paper_id in enumerate(a):
                #print(num,list(scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1})))
                scienceon_data.append(list(scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1,"issueInsts":1,
                'issueLangs':1,'Usage Count':1,'issue_year':1,'citation':1,'author_id':1})))
               # scienceon_paper_cnt += 1
                
            #paper_cnt.append(scienceon_paper_cnt[0])  # 각 scienceon id 별 논문 수
    
    
    papers_data.append({"Scienceon_id":scienceon_author})
    papers_data.append({"scienceon_data":scienceon_data})
    papers_data.append({"ntis_data":ntis_data})
    papers_data.append({"paper_cnt":paper_cnt})
    #scienceon_data.append({"ntis_paper_cnt":ntis_paper_cnt})
    author_paper_data_dict[id['ntis']] = papers_data
  #  pprint.pprint(author_paper_data_dict)
    
def cont(_contBackdata):
    mngIds = _contBackdata['mngIds'][0]
    # print("_contBackdata['A_ID']",_contBackdata['A_ID'])
    # print("mngIds", mngIds)
    A_ID   = _contBackdata['A_ID']
    point  = []
    
    pt = 0
    temp = 0
    for j in range(len(mngIds)):
       # print(mngIds, " ", A_ID)
        if mngIds[j] != None:
            if A_ID == mngIds[j] :
                pt += 10
            else:
                temp += 1
    if pt > 0 : 
        pt += temp
    point.append(pt)
    return point


def career(pYears):
    crr_list = []
    for i in range(len(pYears)):
        _max = max(pYears[i])
        _min = min(pYears[i])
        crr = _max-_min+1
        crr_list.append(crr)
    return crr_list

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

def qty(papers):
        qt = []
        for i in range(0,len(papers)):
            cnt = 0
            cnt = len(papers[i])
            qt.append(cnt)
        return qt

def coop(_coopBackdata):
        pass
from numpy.linalg import norm

def calAcc(keywords, query):
    flat_list = []
    for sublist in keywords :
        for item in sublist :
            if item is not None and item != 'None' and item != "" and isinstance(item, str) :
                flat_list.append(item)
    if len(flat_list) == 0 :
        return 0 
    queryx = ""
    for i in query:
        queryx += i +" "
    qs = query[0].split()
    qs = [_qs for _qs in qs if len(_qs) >= 2]
    tfidf_vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1))
    tfidf_vectorizer.fit(query)

    arr = tfidf_vectorizer.transform(flat_list).toarray()
    qrytfidf = [1] *len(qs)
    if sum(arr[np.argmax(arr.sum(axis=1))]) != 0:
        return cos_sim(arr[np.argmax(arr.sum(axis=1))], qrytfidf)
    else :
        return 0

def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))

def acc(keywords, contBit, querykeyword):

    defaultScore = 0.02
    rtv = contBit.copy()
    for i in range(len(keywords)):
        
        if rtv[i] != 0:
            temp = calAcc(keywords[i],querykeyword)
            if temp == 0.0 :
                rtv[i] = defaultScore
            else :
                rtv[i] = temp
        
    return rtv

for i in author_paper_data_dict: # 저자 한놈씩 나옴
    #print(author_paper_data_dict[i][2]['ntis_data'])
    x = getRawBackdata(author_paper_data_dict[i][2]['ntis_data'],i)
    qryKeyword =author_paper_data_dict[i][2]['ntis_data'][0]['qryKeyword']
    # print("author_paper_data_dict[i][2]['ntis_data']", author_paper_data_dict[i][2]['ntis_data'])
   # print(x)
    (pYears, keywords, _qtyBackdata, _contBackdata, _coopBackdata) = getRawBackdata(author_paper_data_dict[i][2]['ntis_data'],i)
    rctt     = recentness(pYears)
    crrt     = career(pYears)
    contrib  = cont(_contBackdata)
    #print(contrib)
    contBit  = [1 if j > 0 else j for j in contrib]
    qual     = _qtyBackdata
    durat    = durability(pYears)
    qt       = qty(author_paper_data_dict[i][2]['ntis_data'])
    
    cop     = coop(_coopBackdata)
    accuracy = acc(keywords, contBit, qryKeyword)
    
    print(i, "career", crrt, "rctt",rctt, "contrib, con#tBit",contrib, contBit, "durat", durat, "qt", qt, "coop", cop, "accuracy",accuracy)

    #print(author_paper_data_dict[i][2]['ntis_data'])
    storeExpertFactors(i, rctt, crrt,  durat, contrib, qual, qt, accuracy, cop, contBit, author_paper_data_dict[i][2]['ntis_data'])
                    # A_ID, rctt, crrt, durat, contrib, qual, qt, accuracy, coop, contBit, papers
   # print(i, "career", crrt, "rctt",rctt, "contrib, con#tBit",contrib, contBit, "durat", durat, "qt", qt, "coop", cop, "accuracy",accuracy)



    
   
    






# _pYear = []
# _keywords = []
# fund_list = []
# _mngIds = []
# __keyword = []
# pYears = []
# keywords = []
# totalFunds = []
# mngIds = []
# qry = []

# for doc in data:
#     fund_list.append(math.log(int(doc['totalFund'])+1))
#     _mngIds.append(doc['mngId'])

#     if doc['prdEnd'] != 'null':
#         _pYear.append(int(doc['prdEnd'][0:4]))
#     elif (doc['prdEnd'] == 'null') and (doc['prdStart'] != 'null'):
#         _pYear.append(int(doc['prdStart'][0:4]))
#     else:
#         _pYear.append(int(2000))
#     __keyword.append(doc['koTitle'])
#     __keyword.append(doc['enTitle'])
#     __keyword.append(doc['koKeyword'])
#     __keyword.append(doc['enKeyword'])
#     if len(__keyword) != 0 :
#         _keywords.insert(0, __keyword)
#         totalFunds.insert(0, sum(fund_list))
#         mngIds.insert(0, _mngIds)
#         keywords.insert(0, _keywords)
#         pYears.insert(0, _pYear)
#         print(pYears, keywords, totalFunds,  mngIds)
# dt = datetime.datetime.now()
# rct_list = []
# for i in range(len(pYears)):
#     rct = 0
#     for j in range(len(pYears[i])):
#         if pYears[i][j] >= int(dt.year)-2: # 최신년도 기준으로 과거 2년까지 +1점
#             rct += 1
#         elif int(dt.year)-15 < pYears[i][j] <= int(dt.year)-3: # 최신년도 기준 과거 15년 ~ 과거 2년까지 
#             rct += max(round((1-(int(dt.year)-3-pYears[i][j])*0.1),2), 0)
#         else:
#             rct += 0
#     rct_list.append(rct / len(pYears[i]))
# print("rct_list", rct_list)
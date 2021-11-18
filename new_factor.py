import re, math, time, threading, logging, datetime, sys, io, queue
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
import time
client = MongoClient('203.255.92.141:27017', connect=False)
ID = client['ID']
ID_Domestic = ID['Domestic']
ntis_client  = client['NTIS']
ntis_rawdata = ntis_client['Rawdata']
scienceon = client['SCIENCEON']
scienceon_authorpapers = scienceon['AuthorPapers']
scienceon_rawdata = scienceon['Rawdata']
scienceon_id = []
papers_content = []
scienceon_dict = {}
ntis_data = []
data = [] 
AuthorPapers_A_ID_AND_Papers = list(ntis_client['AuthorPapers'].find({'keyId':519}, {'A_ID':1,"papers":1}))
for A_ID_Data in AuthorPapers_A_ID_AND_Papers[0:5]:
    scienceon_author = []
    #scienceon_data = []
    scienceon_dict['ntis'] = A_ID_Data['A_ID'] #NTIS ID
    paper_cnt = [] #Number of papers
    paper_cnt.append(len(A_ID_Data['papers']))
    papers_content = []
    # keyid 519로 검색했을 경우의 논문
    for id_paper in A_ID_Data['papers']: #NTIS Papers content
        ntis_paper_data = list(ntis_rawdata.find({"_id":id_paper},{"koTitle":1,"enTitle":1,"absAbs":1,"effAbs":1,"koKeyword":1,"enKeyword":1,"goalAbs":1,
        'totalFund':1,"mngId":1,"prdEnd":1,"prdStart":1}))
        data.append(ntis_paper_data[0])

pprint.pprint(data)
_pYear = []
_keywords = []
fund_list = []
_mngIds = []
__keyword = []
pYears = []
keywords = []
totalFunds = []
mngIds = []
qry = []

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
        print(pYears, keywords, totalFunds,  mngIds)
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
print("rct_list", rct_list)
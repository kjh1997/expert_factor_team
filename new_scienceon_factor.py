from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
import time, math, datetime
import numpy as np

client = MongoClient('203.255.92.141:27017', connect=False)
ID = client['ID']
ID_Domestic = ID['Domestic']
ntis_client  = client['NTIS']
ntis_rawdata = ntis_client['Rawdata']
scienceon = client['SCIENCEON']
scienceon_authorpapers = scienceon['AuthorPapers']
scienceon_rawdata = scienceon['Rawdata']

AuthorPapers_A_ID_AND_Papers = list(ntis_client['AuthorPapers'].find({'keyId':519}, {'A_ID':1,"papers":1}))
# keyid를 정해서 authorpapers 컬렉션에 검색한다.
scienceon_id = []
author_paper_data_dict = {}
ntis_data = []

for A_ID_Data in AuthorPapers_A_ID_AND_Papers:
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
        'totalFund':1,"mngId":1,"prdEnd":1,"prdStart":1}))
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
            a = list(scienceon_authorpapers.find({"A_ID":scienceon_id,"keyId":519},{"papers":1}))
            scienceon_paper_cnt = 0
       
            for num,scienceon_paper_id in enumerate(a):
                #print(num,list(scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1})))
                x = list(scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1,"issueInsts":1,
                'issueLangs':1,'Usage Count':1,'issue_year':1,'citation':1,'author_id':1,"paper_keyword":1,"english_title":1,"english_abstract":1,"author_inst":1,"issue_inst":1,
                "issue_lang":1}))
                scienceon_data.append(x[0])
                scienceon_paper_cnt += 1
                
           # paper_cnt.append(scienceon_paper_cnt[0])  # 각 scienceon id 별 논문 수
    
    
    papers_data.append({"Scienceon_id":scienceon_author})
    papers_data.append({"scienceon_data":scienceon_data})
    papers_data.append({"ntis_data":ntis_data})
    papers_data.append({"paper_cnt":paper_cnt})
    #scienceon_data.append({"ntis_paper_cnt":ntis_paper_cnt})
    author_paper_data_dict[id['ntis']] = papers_data
   # pprint.pprint(author_paper_data_dict)

def getRawBackdata(data, A_ID):
    pYears = []
    keywords = []
    authorInsts = []
    authors = []
    issueInsts = []
    issueLangs = []
    citation = []
    socialCitations = []

    _pYear = []
    _keywords = []
    _keyword =   []
    _authorInsts =[]
    _authors =    []
    _issueInsts = []
    _issueLangs = []
    _citation = []
    _socialCitations = []
    for doc in data:
        _keyword.append(doc['title'])
        _keyword.append(doc['english_title'])
        _keyword.append(doc['paper_keyword'])
        _keyword.append(doc['abstract'])
        _keyword.append(doc['english_abstract'])

        
        _pYear.append(int(doc['issue_year'][0:4]))

        _authorInsts.append(doc['author_inst'])
        _authors.append(doc['author_id'])
        _issueInsts.append(doc['issue_inst'])
        _issueLangs.append(doc['issue_lang'])

       
        _citation.append(int(doc['citation']))

    if len(_keyword) != 0 :
        authorInsts.insert(0,_authorInsts)
        authors.insert(0, _authors)
        issueInsts.insert(0, _issueInsts)
        _keywords.insert(0,_keyword)
        pYears.insert(0,_pYear)
        issueLangs.insert(0,_issueLangs)
        keywords.insert(0,_keywords)
        citation.insert(0,_citation)

        
    #print(pYears, keywords, {'issueInsts' : issueInsts, 'issueLangs' : issueLangs, 'citation' : citation}, {'authors' : authors, 'A_ID' : A_ID  }, authorInsts)
    return pYears, keywords, {'issueInsts' : issueInsts, 'issueLangs' : issueLangs, 'citation' : citation}, {'authors' : authors, 'A_ID' : A_ID  }, authorInsts #for coop


def recentness( pYears):
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

def career( pYears):
    crr_list = []
    for i in range(len(pYears)):
        _max = max(pYears[i])
        _min = min(pYears[i])
        crr = _max-_min+1
        crr_list.append(crr)
    return crr_list

def cont( _contBackdata):
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

def qty( papers):
    qt = []
    for i in range(0,len(papers)):
        cnt = 0
        cnt = len(papers[i])
        qt.append(cnt)
    return qt 

def durability( pYears):
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

oemList = ["Hyundai", "Kia","Toyota","Honda","Nissan","General Motors", "Chevrolet","Ford motor", "Volkswagen", "Audi", "BMW", "Bayerische Motoren Werke", "Mercedes-Benz", "daimler", "Volvo", "Renault", "Jaguar", "Acura", "Mazda", "Subaru", "Suzuki", "Isuzu","Daihatsu","Peugeot","Mclaren", "Bugatti", "Rolls Royce", "Bentley", "Aston Martin", "Land Rover", "Lotus","Lexus",   "Infiniti", "Datson", "Mitsubishi", "Mitsuoka","Great Wall","Cadillac", "Tesla", "Jeep", "Dodge", "Chrysler","Porsche", "Opel", "Borgward", "Gumfut", "FIAT", "Ferrari", "Lamborghini", "Maserati","Peugeot"]

def calAcc(self, keywords):
    flat_list = []
    for sublist in keywords :
        for item in sublist :
            if item is not None and item != 'None' and item != "" and isinstance(item, str) :
                flat_list.append(item)
    if len(flat_list) == 0 :
        return 0 

    qs = self.query.split()
    qs = [_qs for _qs in qs if len(_qs) >= 2]
    tfidf_vectorizer = TfidfVectorizer (analyzer='word', ngram_range=(1, 1))
    tfidf_vectorizer.fit([self.query])

    arr = tfidf_vectorizer.transform(flat_list).toarray()
    qrytfidf = [1] *len(qs)
    if sum(arr[np.argmax(arr.sum(axis=1))]) != 0:
        return self.cos_sim(arr[np.argmax(arr.sum(axis=1))], qrytfidf)
    else :
        return 0

def coop( _coopBackdata):
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
defaultScore = 0.02
def acc( keywords, contBit):
    rtv = contBit.copy()
    for i in range(len(keywords)):
        try :
            if rtv[i] != 0:
                temp = calAcc(keywords[i])
                if temp == 0.0 :
                    rtv[i] = defaultScore
                else :
                    rtv[i] = temp
        except Exception as e :
            print(keywords[i])
            print(e)
    return rtv

def storeExpertFactors(A_ID, rctt, crrt, durat, contrib, qual, qt, accuracy, coop, contBit, papers):
   # print("실행" , "A_ID", A_ID, "rctt", rctt, "crrt",  crrt, "durat", durat, "contrib",  contrib,"qual", qual,"qt",  qt,"accuracy", accuracy, "coop", coop, "contBit", contBit, "papers", papers)

    expf = []
    exp = {}
    exp['A_ID']         = i
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
    print("expf", expf)

kDic = {}
sDic = {}

def quality(_qtyBackdata):
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


for i in author_paper_data_dict: # 저자 한놈씩 나옴
    #print(i)
    #print("데이터", author_paper_data_dict[i][1]['scienceon_data'])
   # print(author_paper_data_dict[i][2]['ntis_data'])
    #print(author_paper_data_dict[i][1]['scienceon_data'])
    if not author_paper_data_dict[i][1]['scienceon_data']:
        continue
    #print(author_paper_data_dict[i][1]['scienceon_data'])
    print(author_paper_data_dict[i][1]['scienceon_data'][0]['author_id'])
    x = getRawBackdata(author_paper_data_dict[i][1]['scienceon_data'],i)
    
    

        
    
    (pYears, keywords, _qtyBackdata, _contBackdata, _coopBackdata) = getRawBackdata(author_paper_data_dict[i][1]['scienceon_data'],i)
    rctt     = recentness(pYears)
    crrt     = career(pYears)
    contrib  = cont(_contBackdata)
    contBit  = [1 if j > 0 else j for j in contrib]
    qual     = quality(_qtyBackdata)
    durat    = durability(pYears)
    qt       = qty(author_paper_data_dict[i][1]['scienceon_data'])
    
    cop     = coop(_coopBackdata)
    accuracy = acc(keywords, contBit)
    
    #print(i, "career", crrt, "rctt",rctt, "contrib, con#tBit",contrib, contBit, "durat", durat, "qt", qt, "coop", cop, "accuracy",accuracy)
    storeExpertFactors(i, rctt, crrt, durat, contrib, qual, qt, accuracy, cop, contBit, author_paper_data_dict[i][1]['scienceon_data'])
    print("한명끝")
   # print(author_paper_data_dict[i][2]['ntis_data'])
    #storeExpertFactors(i,rctt, crrt,  durat, contrib, qual, qt, accuracy, cop, contBit, author_paper_data_dict[i][2]['ntis_data'])
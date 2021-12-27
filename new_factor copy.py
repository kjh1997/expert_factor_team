from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
import time, math, datetime
import numpy as np
from numpy import dot
from numpy.linalg import norm


def __main__():
    a = factor_extract()
    a.mongodb_data()
    a.printa()
class factor_extract:
    def __init__(self):
        self.kDic = {}
        self.sDic = {}
        self.client = MongoClient('203.255.92.141:27017', connect=False)
        self.ID = self.client['ID']
        self.ID_Domestic = self.ID['Domestic']
        self.ntis_client  = self.client['NTIS']
        self.ntis_rawdata = self.ntis_client['Rawdata']
        self.scienceon = self.client['SCIENCEON']
        self.scienceon_authorpapers = self.scienceon['AuthorPapers']
        self.scienceon_rawdata = self.scienceon['Rawdata']
        self.author_paper_data_dict = {}

    def mongodb_data(self):
        AuthorPapers_A_ID_AND_Papers = list(self.ntis_client['AuthorPapers'].find({'keyId':519}, {'A_ID':1,"papers":1}))
        # keyid를 정해서 authorpapers 컬렉션에 검색한다.
        scienceon_id = []
        
        ntis_data = []
# 94:95
        for A_ID_Data in AuthorPapers_A_ID_AND_Papers[94:95]:
            scienceon_author = []
            papers_data = []
            scienceon_data = []
            ntis_data = []
            #scienceon_data.append({"A_id": A_ID_Data['zA_ID']})
            ntis_paper_cnt = 0
            paper_cnt = []
            # keyid 519로 검색했을 경우의 논문
            for id_paper in A_ID_Data['papers']:
                
                
                ntis_paper_data = list(self.ntis_rawdata.find({"_id":id_paper},{"koTitle":1,"enTitle":1,"absAbs":1,"effAbs":1,"koKeyword":1,"enKeyword":1,"goalAbs":1,
        'totalFund':1,"mngId":1,"prdEnd":1,"prdStart":1,"qryKeyword":1}))
                ntis_data.append(ntis_paper_data[0])
                ntis_paper_cnt += 1 
            #-----------------------------------------------------    
            if ntis_paper_cnt >= 1:
                paper_cnt.append(ntis_paper_cnt) # 저자에 대한 ntis 논문 수
            else:
                paper_cnt.append(0)
            # keyid 519로 검색했을 경우 나오는 a_id에 대한 scienceon의 id
            author = self.ID_Domestic.find({"ntis":A_ID_Data['A_ID']},{"scienceon":1,"ntis":1})
            for id in author:
                
                if id == []:
                    continue
                #print(id)
                for scienceon_id in id["scienceon"]:
                    
                    a = list(self.scienceon_authorpapers.find({"A_ID":scienceon_id,"keyId":519},{"papers":1}))
                    scienceon_paper_cnt = 0
            
                    for num,scienceon_paper_id in enumerate(a):
                        #print(num,list(scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1})))
                        x = list(self.scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1,"issueInsts":1,
                'issueLangs':1,'Usage Count':1,'issue_year':1,'citation':1,'author_id':1,"paper_keyword":1,"english_title":1,"english_abstract":1,"author_inst":1,"issue_inst":1,
                "issue_lang":1}))
                        scienceon_author.append(scienceon_id)
                        scienceon_data.append(x[0])
                        scienceon_paper_cnt += 1
                    if scienceon_paper_cnt != 0:
                        paper_cnt.append(scienceon_paper_cnt)      
                # paper_cnt.append(scienceon_paper_cnt[0])  # 각 scienceon id 별 논문 수
            
            scienceon_author = set(scienceon_author)
            scienceon_author = list(scienceon_author)
            papers_data.append({"Scienceon_id":scienceon_author})
            papers_data.append({"scienceon_data":scienceon_data})
            papers_data.append({"ntis_data":ntis_data})
            papers_data.append({"paper_cnt":paper_cnt})
            #scienceon_data.append({"ntis_paper_cnt":ntis_paper_cnt})
            self.author_paper_data_dict[id['ntis']] = papers_data
        #print(len(self.author_paper_data_dict))
        #pprint.pprint(self.author_paper_data_dict)
        
    def printa(self):
        for i in self.author_paper_data_dict:
            #print("scienceon_data", self.author_paper_data_dict[i][1]['scienceon_data'])
            #print("ntis_data", self.author_paper_data_dict[i][2]['ntis_data'])
            #print("id", )
            sc_result = self.scienceon_run(self.author_paper_data_dict[i][1]['scienceon_data'],self.author_paper_data_dict[i][0]['Scienceon_id'].pop(0))
            ntis_result = self.ntis_run(self.author_paper_data_dict[i][2]['ntis_data'], i)
            a = sc_result[0]
            b = ntis_result[0]
           # print("a,b", a,b)
            c = {}
            c['A_ID'] = a['A_ID']
            c['keyId'] = a['keyId']
            c['Productivity'] = a['Productivity'] + b['Productivity']
            c['Contrib'] = (a['Contrib'] * b['Contrib'])/2
            c['Durability'] = (a['Durability'] * b['Durability'])/2
            c['Recentness'] = (a['Recentness'] * b['Recentness'])/2
            c['Coop'] = (a['Coop'] * b['Coop'])/2
            c['Quality'] = a['Quality'] + b['Quality']
            c['Acc'] = a['Numpaper'] + b['Numpaper']
            print(c)

    #########3 실행기 ###############
    def ntis_run(self,paper,a_id):

        """ #3. DB client 생성 """
        All_count = len(self.author_paper_data_dict)
        dataPerPage = 100

        self.dt = datetime.datetime.now()
       # print('start', self.dt)
        tempQty  = -1
        tempCont = -1
        tempQual = -1
        tempCoop = -1
        maxFactors = {'Quality' : -1, 'Productivity' : -1, 'Contrib' : -1 }
        factorVars = {'Quality' : 'tempQual', 'Productivity' : 'tempQty', 'Contrib' : 'tempCont' }
        

        """ #4. 지수별 분석 실행 """
        allPage = math.ceil(All_count/dataPerPage)
        
        A_ID, papers = a_id , paper
        (pYears, keywords, _qtyBackdata, _contBackdata, _coopBackdata, query_data) = self.ntis_getRawBackdata(papers, A_ID)
        #print("keywords", keywords)
        if len(pYears) > 0 :
            contrib  = self.ntis_cont(_contBackdata)
            contBit  = [1 if j > 0 else j for j in contrib]
            rctt     = self.recentness(pYears)
            crrt     = self.career(pYears)
            durat    = self.durability(pYears)
            qt       = self.qty(papers)
            coop     = self.coop(_coopBackdata)
            qual     = self.ntis_quality(_qtyBackdata)
            accuracy = self.acc(keywords, contBit, query_data)

            tempQty  = max(qt)
            tempCont = max(contrib)
            tempQual = max(qual)

            

            for f in maxFactors :
                if maxFactors[f] < eval(factorVars[f]) :
                    maxFactors[f] = eval(factorVars[f])

            exft = self.storeExpertFactors(A_ID, rctt, crrt, durat, contrib, qual, qt, accuracy, coop, contBit, papers)
           # print(exft)
            return exft
            #progress = (len(A_ID)/self.total) * 100.0

    def scienceon_run(self, paper,a_id):

        """ #3. DB client 생성 """
        All_count = len(self.author_paper_data_dict)
        dataPerPage = 100

        self.dt = datetime.datetime.now()
        #print('start', self.dt)
        tempQty  = -1
        tempCont = -1
        tempQual = -1
        tempCoop = -1
        maxFactors = {'Quality' : -1, 'Productivity' : -1, 'Contrib' : -1 }
        factorVars = {'Quality' : 'tempQual', 'Productivity' : 'tempQty', 'Contrib' : 'tempCont' }
        
        maxFactors['Coop'] = -1
        factorVars['Coop'] = 'tempCoop'

        """ #4. 지수별 분석 실행 """
        allPage = math.ceil(All_count/dataPerPage)
        
        A_ID, papers = a_id , paper
        (pYears, keywords, _qtyBackdata, _contBackdata, _coopBackdata, query_data) = self.scienceon_getRawBackdata(papers, A_ID)

        if len(pYears) > 0 :
            contrib  = self.scienceon_cont(_contBackdata)
            contBit  = [1 if j > 0 else j for j in contrib]
            rctt     = self.recentness(pYears)
            crrt     = self.career(pYears)
            durat    = self.durability(pYears)
            qt       = self.qty(papers)
            coop     = self.scienceon_coop(_coopBackdata)
            qual     = self.scienceon_quality(_qtyBackdata)
            accuracy = self.acc(keywords, contBit, query_data)

            tempQty  = max(qt)
            tempCont = max(contrib)
            tempQual = max(qual)

            
            tempCoop = max(coop)

            for f in maxFactors :
                if maxFactors[f] < eval(factorVars[f]) :
                    maxFactors[f] = eval(factorVars[f])

            exft = self.storeExpertFactors(A_ID, rctt, crrt, durat, contrib, qual, qt, accuracy, coop, contBit, papers)
           # print("exft", exft)
            return exft

    def storeExpertFactors(self, A_ID, rctt, crrt, durat, contrib, qual, qt, accuracy, coop, contBit, papers):
        expf = []
        #print("asdf","\nA_ID", A_ID, "\nrctt", rctt, "\ncrrt" ,crrt, "\ndurat",durat, "\ncontrib", contrib, "\nqual", qual, 
        #"\nqt", qt, "\naccuracy", accuracy, "\ncoop", coop, "\ncontBit", contBit, "\npapers", papers)
        
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
        exp['Numpaper']     = len(papers[0])
        expf.append(exp)
        return expf

########################## 공통지수 ########################

    def recentness(self, pYears):
        rct_list = []
        for i in range(len(pYears)):
            rct = 0
            for j in range(len(pYears[i])):
                if pYears[i][j] >= int(self.dt.year)-2: # 최신년도 기준으로 과거 2년까지 +1점
                    rct += 1
                elif int(self.dt.year)-15 < pYears[i][j] <= int(self.dt.year)-3: # 최신년도 기준 과거 15년 ~ 과거 2년까지 
                    rct += max(round((1-(int(self.dt.year)-3-pYears[i][j])*0.1),2), 0)
                else:
                    rct += 0
            rct_list.append(rct / len(pYears[i]))
        return rct_list

    def cos_sim(self, A, B):
        return dot(A, B)/(norm(A)*norm(B))

    def qty(self, papers):
        qt = []
        for i in range(0,len(papers)):
            cnt = 0
            cnt = len(papers[i])
            qt.append(cnt)
        return qt

    def minmaxNorm(self, arr):
       rtv = []
       max_val = max(arr)
       min_val = min(arr)
       norm =  max_val-min_val
       for i in range(0, len(arr)):
           if arr[i] == min_val:
               rtv.append(self.defaultScore)
           else :
               rtv.append((arr[i]-min_val)/norm)
       return rtv

    def career(self, pYears):
        crr_list = []
        for i in range(len(pYears)):
            _max = max(pYears[i])
            _min = min(pYears[i])
            crr = _max-_min+1
            crr_list.append(crr)
        return crr_list

    def durability(self, pYears):
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
    
    

    def calAcc(self, keywords, query_data):
        flat_list = []
        for sublist in keywords :
            for item in sublist :
                if item is not None and item != 'None' and item != "" and isinstance(item, str) :
                    flat_list.append(item)
        if len(flat_list) == 0 :
            return 0 

        qs = query_data
        qs = [_qs for _qs in qs if len(_qs) >= 2]
        tfidf_vectorizer = TfidfVectorizer (analyzer='word', ngram_range=(1, 1))
        tfidf_vectorizer.fit(query_data)

        arr = tfidf_vectorizer.transform(flat_list).toarray()
        qrytfidf = [1] *len(qs)
        if sum(arr[np.argmax(arr.sum(axis=1))]) != 0:
            return self.cos_sim(arr[np.argmax(arr.sum(axis=1))], qrytfidf)
        else :
            return 0
    
    def acc(self, keywords, contBit,query_data):
        defaultScore = 0.02
        rtv = contBit.copy()
        for i in range(len(keywords)):
            
            if rtv[i] != 0:
                temp = self.calAcc(keywords[i], query_data)
                if temp == 0.0 :
                    rtv[i] = defaultScore
                else :
                    rtv[i] = temp
            
        return rtv


##############################3 공통지수 끝 ###############################

############################ NTIS 지수 #############################
    def coop(self, _coopBackdata):
        pass

    def ntis_quality(self, totalFunds):
        return totalFunds

    """
    @ Method Name     : cont
    @ Method explain  : 기여도 계산 함수
    @ _contBackdata   : getRawBackdata 함수에서 mngIds, A_ID 값을 가지고 있는 변수
    """
    def ntis_cont(self, _contBackdata):
        mngIds = _contBackdata['mngIds']
        A_ID   = _contBackdata['A_ID']
        point  = []
        pt = 0
        temp = 0
        #print("mngIds, A_ID", mngIds, A_ID)
        for j in range(len(mngIds)):
            if mngIds[j] != None:
                if A_ID == mngIds[j]:
                    pt += 10
                else:
                    temp += 1
               # print("pt,temp", pt, temp)
        pt += temp
        point.append(pt)
        return point

    def ntis_getRawBackdata(self, papers, A_ID):
        pYears = []
        keywords = []
        totalFunds = []
        mngIds = []
        qry = []
        qryKeyword = []
        
        for i in range(len(papers)-1, -1, -1):
            _pYear = []
            _keywords = []
            fund_list = []
            _mngIds = []
            __keyword = []
            _qryKeyword = []
            for doc in papers:
                fund_list.append(math.log(int(doc['totalFund'])+1))
                _mngIds.append(doc['mngId'])
               # print(len(doc['qryKeyword']),doc['qryKeyword'][0],doc['qryKeyword'][1])
                for i in range(len(doc['qryKeyword'])):
                    qryKeyword.append(doc['qryKeyword'][i])
                
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
            else :
                del A_ID[i]
                del papers[i]
        return pYears, keywords, totalFunds, {'mngIds' : mngIds, 'A_ID' : A_ID}, None, qryKeyword

    
######################## ScienceOn 지수 ########################################

    def scienceon_coop(self, _coopBackdata):
        score = []
        oemList = ["Hyundai", "Kia","Toyota","Honda","Nissan","General Motors", "Chevrolet","Ford motor", "Volkswagen", "Audi", "BMW", "Bayerische Motoren Werke", "Mercedes-Benz", "daimler", "Volvo", "Renault", "Jaguar", "Acura", "Mazda", "Subaru", "Suzuki", "Isuzu","Daihatsu","Peugeot","Mclaren", "Bugatti", "Rolls Royce", "Bentley", "Aston Martin", "Land Rover", "Lotus","Lexus",   "Infiniti", "Datson", "Mitsubishi", "Mitsuoka","Great Wall","Cadillac", "Tesla", "Jeep", "Dodge", "Chrysler","Porsche", "Opel", "Borgward", "Gumfut", "FIAT", "Ferrari", "Lamborghini", "Maserati","Peugeot"]

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

    """
    @ Method Name     : cont
    @ Method explain  : 기여도 계산 함수
    @ _contBackdata   : getRawBackdata 함수에서 mngIds, A_ID 값을 가지고 있는 변수
    """
    def scienceon_quality(self, _qtyBackdata):
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
                
            IF.append(tempIF)
        return IF
    
    """
    @ Method Name     : cont
    @ Method explain  : 기여도 계산 함수
    @ _contBackdata   : getRawBackdata 함수에서 mngIds, A_ID 값을 가지고 있는 변수
    """
    def scienceon_cont(self, _contBackdata):
        authors = _contBackdata['authors']
        A_ID = _contBackdata['A_ID']
        aidToDict = {i : 0 for i in [A_ID]}
        
        for j in range(len(authors)):
            x = authors[0][j].split(';')
            for author in enumerate(x):
                if author[1] in aidToDict and author[1] == A_ID:
                    if author[0] == 0:
                        aidToDict[author[1]] += 1.0
                    elif author[0] == len(x)-1:
                        aidToDict[author[1]] += 3.0
                    else :
                        aidToDict[author[1]] += ((author[0]+1)/len(x))
        
        return list(aidToDict.values())

    """
    @ Method Name     : getRawBackdata
    @ Method explain  : 전문가 지수를 계산하기 위해 필요로 하는 Backdata를 계산하는 함수
    @ papers          : 논문(프로젝트) 수
    @ A_ID            : 논문(프로젝트) 저자 고유 ID
    """
    def scienceon_getRawBackdata(self, papers, A_ID):
        pYears = []
        keywords = []
        authorInsts = []
        authors = []
        issueInsts = []
        issueLangs = []
        citation = []
        socialCitations = []
        qryKeyword = []
        for i in range(len(papers)-1, -1, -1):
            _pYear = []
            _keywords = []
            _keyword =   []
            _authorInsts =[]
            _authors =    []
            _issueInsts = []
            _issueLangs = []
            _citation = []
            _socialCitations = []
            _qrykeyword = []
            for doc in papers:
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

                for i in range(len(doc['qryKeyword'])):
                    qryKeyword.append(doc['qryKeyword'][i])
                
            if len(_keyword) != 0 :
                authorInsts.insert(0,_authorInsts)
                authors.insert(0, _authors)
                issueInsts.insert(0, _issueInsts)
                _keywords.insert(0,_keyword)
                pYears.insert(0,_pYear)
                issueLangs.insert(0,_issueLangs)
                keywords.insert(0,_keywords)
                citation.insert(0,_citation)

                
            else :
                del A_ID[i]
                del papers[i]
      #  print(pYears, keywords, {'issueInsts' : issueInsts, 'issueLangs' : issueLangs, 'citation' : citation}, {'authors' : authors, 'A_ID' : A_ID  }, authorInsts)
       
        return pYears, keywords, {'issueInsts' : issueInsts, 'issueLangs' : issueLangs, 'citation' : citation}, {'authors' : authors, 'A_ID' : A_ID  }, authorInsts , qryKeyword #for coop
        
    
            


    























__main__()
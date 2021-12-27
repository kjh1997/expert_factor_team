from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
import time
client = MongoClient('203.255.92.141:27017', connect=False)
ID = client['ID']
ID_Domestic = ID['Domestic']
ntis_client  = client['KCI']
ntis_rawdata = ntis_client['Rawdata']
scienceon = client['SCIENCEON']
scienceon_authorpapers = scienceon['AuthorPapers']
scienceon_rawdata = scienceon['Rawdata']

AuthorPapers_A_ID_AND_Papers = list(ntis_client['AuthorPapers'].find({'keyId':519}, {'A_ID':1,"papers":1}))
# keyid를 정해서 authorpapers 컬렉션에 검색한다.
scienceon_id = []
scienceon_dict = {}
ntis_data = []
for A_ID_Data in AuthorPapers_A_ID_AND_Papers[0:60]:
    scienceon_author = []
    scienceon_data = []
    #scienceon_data.append({"A_id": A_ID_Data['zA_ID']})
    ntis_paper_cnt = 0
    paper_cnt = []
    # keyid 519로 검색했을 경우의 논문
    for id_paper in A_ID_Data['papers']:
        
        
        ntis_paper_data = list(ntis_rawdata.find({"_id":id_paper},{"koTitle":1,"enTitle":1,"absAbs":1,"effAbs":1,"koKeyword":1,"enKeyword":1,"goalAbs":1}))
        scienceon_data.append(ntis_paper_data)
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
        print(id)
        for scienceon_id in id["scienceon"]:
            scienceon_author.append(scienceon_id)
            a = list(scienceon_authorpapers.find({"A_ID":scienceon_id},{"papers":1}))
            scienceon_paper_cnt = 0
       
            for num,scienceon_paper_id in enumerate(a):
                print(num,list(scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1})))
                scienceon_data.append(list(scienceon_rawdata.find({"_id":scienceon_paper_id['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1})))
                scienceon_paper_cnt += 1
                
            paper_cnt.append(scienceon_paper_cnt)  # 각 scienceon id 별 논문 수
    
    
    print(id['ntis'], "한사람 끝")
    scienceon_data.append({"Scienceon_id":scienceon_author})
    scienceon_data.append({"paper_cnt":paper_cnt})
    #scienceon_data.append({"ntis_paper_cnt":ntis_paper_cnt})
    scienceon_dict[id['ntis']] = scienceon_data
    pprint.pprint(scienceon_dict)
    time.sleep(2)
    
    
print(scienceon_dict)
# -----------------------------------------------------------ntis 코드 ---------------------------------------------------------------



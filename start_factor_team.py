import pymongo
from pymongo import MongoClient
client = MongoClient('203.255.92.141:27017', connect=False)
ID = client['ID']
ID_Domestic = ID['Domestic']
ntis_client  = client['NTIS']
scienceon = client['SCIENCEON']
scienceon_authorpapers = scienceon['AuthorPapers']
scienceon_rawdata = scienceon['Rawdata']
test = list(ntis_client['AuthorPapers'].find({'keyId':519}, {'A_ID':1}))
# keyid를 정해서 authorpapers 컬렉션에 검색한다.
scienceon_id = []
for i in test:
    scienceon_id.append(list(ID_Domestic.find({"ntis":i['A_ID']},{"scienceon":1})))
#검색한 결과는 ntis의 저자 id 이고 이 결과를 바탕으로 id_domestic 컬렉션에 검색한다. 여기서 나오는 결과는 scienceon의 저자 id 이다.
list_paper_title = []
for i in scienceon_id:
    if i == []:
        continue
    # print(i)
    # print(type(i))
    for j in i[0]["scienceon"]:
       # print(j)
        a = list(scienceon_authorpapers.find({"A_ID":j},{"papers":1}))
       # print(a[0]["papers"])
        # 여기까지 authorpapers에서 논문 id들을 가져왔다.
        for num, k in enumerate(a):
            #  print(k['papers'][0])
            x = list(scienceon_rawdata.find({"_id":k['papers'][0]},{"title":1,"abstract":1}))
            print(num,x)
# -------------------- 여기까지 scienceon에서 해당 저자의 title and abstract ---------------------------------




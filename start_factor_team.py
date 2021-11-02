from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('203.255.92.141:27017', connect=False)
ID = client['ID']
ID_Domestic = ID['Domestic']
ntis_client  = client['NTIS']
ntis_rawdata = ntis_client['Rawdata']
scienceon = client['SCIENCEON']
scienceon_authorpapers = scienceon['AuthorPapers']
scienceon_rawdata = scienceon['Rawdata']

test = list(ntis_client['AuthorPapers'].find({'keyId':519}, {'A_ID':1,"papers":1}))
# keyid를 정해서 authorpapers 컬렉션에 검색한다.
scienceon_id = []
scienceon_data = []
ntis_data = []
for i in test:
    scienceon_id.append(list(ID_Domestic.find({"ntis":i['A_ID']},{"scienceon":1})))
#검색한 결과는 ntis의 저자 id 이고 이 결과를 바탕으로 id_domestic 컬렉션에 검색한다. 여기서 나오는 결과는 scienceon의 저자 id 이다.
list_paper_title = []
# for i in scienceon_id:
#     if i == []:
#         continue
#     # print(i)
#     # print(type(i))
#     for j in i[0]["scienceon"]:
#        # print(j)
#         a = list(scienceon_authorpapers.find({"A_ID":j},{"papers":1}))
       
#         # 여기까지 authorpapers에서 논문 id들을 가져왔다.
#         for num,k in enumerate(a):
#             #  print(k['papers'][0])
#             print(num,list(scienceon_rawdata.find({"_id":k['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1})))
#             scienceon_data.append(list(scienceon_rawdata.find({"_id":k['papers'][0]},{"title":1,"abstract":1,"english_title":1,"qryKeyword":1})))
# print(scienceon_data)
for i in test:
    for j in i['papers']:
        print(list(ntis_rawdata.find({"_id":j},{"koTitle":1,"enTitle":1,"absAbs":1,"effAbs":1,"koKeyword":1,"enKeyword":1,"goalAbs":1})))
        ntis_data.append(list(ntis_rawdata.find({"_id":j},{"koTitle":1,"enTitle":1,"absAbs":1,"effAbs":1,"koKeyword":1,"enKeyword":1,"goalAbs":1})))
       # print(list(ntis_rawdata.find({"_id":ObjectId(j['_id'])})))
# {_id:OjectId("")}


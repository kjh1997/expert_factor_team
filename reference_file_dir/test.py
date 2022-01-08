from pymongo import MongoClient
from bson.objectid import ObjectId


client =  MongoClient('203.255.92.141:27017', connect=False)
public = client['PUBLIC']
ID = client['ID']
Domestic = ID['Domestic']
new_factor = public['new_factor']

new_factor.update_one({'keyId':655},{"$set":{'test':{"test1":5}}})
# # ID = client['ID']
# # Domestic = ID['Domestic']
# # data = Domestic.find({"keyId":650},{'_id':1})
# # cnt =0
# # for i in data:
# #     cnt += 1
# #     print(i)
# # print(cnt)
# FOR

# y= Domestic.find({"keyId":655},{"_id":1})


# for i in y:
#     print(Domestic.find_one({"_id":ObjectId(i['_id'])}))
# update_list = Domestic.find({"keyId":655},{'factor':1,"_id":1})
# for doc in update_list:
#     print(doc['factor']['qual'])
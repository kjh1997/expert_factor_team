
from multiprocessing import Process
import multiprocessing
import os
from bson.objectid import ObjectId
from pymongo import MongoClient
from base_class import run
from reference_file_dir.test import Domestic 
client =  MongoClient('203.255.92.141:27017', connect=False)
PUBLIC = client['PUBLIC']
new_max_factor =PUBLIC['new_factor'] 
ID = client['ID']
Domestic = ID['Domestic']
keyid = 650
fid = 0
ID = client['ID']
DATA = ID['Domestic'].find({"keyId":keyid, "fid":0})
b = 0
print("실행")
for i in DATA:
    #print(i)
    b += 1
print(b)  

PUBLIC = client['PUBLIC']
new_max_factor = PUBLIC['new_factor'] 
print(type(new_max_factor.find_one({'keyId': keyid})))
processList = []
if None == new_max_factor.find_one({'keyId': keyid}):
    new_max_factor.insert({'keyId': keyid},{'keyId': keyid, 'Quality' : -1, 'accuracy' : -1, 'recentness' : -1, 'coop': -1 })


for i in range(0,b , 100):
    start = 1 *i
    end = 100
    if i//100 == b//100:
        start = i
        end = b
    print(end)
    proc = Process(target=run(start, end, fid, keyid))
    processList.append(proc)
    proc.start()
for p in processList :
    p.join()

max_factor = new_max_factor.find_one({'keyId':keyid})
print(max_factor)

max_qual = max_factor['Quality']
max_acc = max_factor['accuracy']
max_recentness = max_factor['recentness']
max_coop = max_factor['coop']
update_list = Domestic.find({"keyId":keyid},{'factor':1,"_id":1})
for doc in update_list:
    if max_qual != 0:
        norm_qual = doc['factor']['qual']/max_qual
    else:
        norm_qual = doc['factor']['qual']

    Domestic.update({'_id':ObjectId(doc['_id'])},{"$set":{'factor':{"qual":norm_qual,'coop':doc['factor']['coop'],'recentness':doc['factor']['recentness'],'acc':doc['factor']['accuracy']}}})
print("정규화 끝")
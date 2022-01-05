
from multiprocessing import Process
import multiprocessing
import os
from pymongo import MongoClient
from base_class import run 
client =  MongoClient('203.255.92.141:27017', connect=False)
PUBLIC = client['PUBLIC']
new_max_factor =PUBLIC['new_factor'] 
keyid = 655
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


if __name__ == '__main__':   
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



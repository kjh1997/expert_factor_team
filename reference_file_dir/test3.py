

from multiprocessing import Process
import multiprocessing
import os
from bson.objectid import ObjectId
from pymongo import MongoClient
from time import sleep
client =  MongoClient('203.255.92.141:27017', connect=False)
PUBLIC = client['PUBLIC']
new_max_factor = PUBLIC['new_factor'] 
ID = client['ID']
Domestic = ID['Domestic']
cnt = 0
print(cnt)
data= ID['Domestic'].find({"keyId":675, "fid":0})
for i in data:
    #print(i)
    cnt += 1
print(cnt)
sleep(5)
for i in range(0,cnt,100):
    if i//100 == cnt//100:
        start = i
        end = cnt
    a= ID['Domestic'].find({"keyId":675, "fid":0}).skip(i).limit(100)
    for j in a:
        print(j)
        
    print("-------------------------------------------------------------------------\n")
    print("                             ", i, "--------------------------------\n")


print([a])
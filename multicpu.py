
from multiprocessing import Process
import multiprocessing
import os
from pymongo import MongoClient
from base_class import run 
client =  MongoClient('203.255.92.141:27017', connect=False)
keyid = 650
fid = 0
ID = client['ID']
DATA = ID['Domestic'].find({"keyId":650, "fid":0})
b = 0

for i in DATA:
    #print(i)
    b += 1
print(b)  


processList = []

    

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

# run(2200, 80, fid, keyid)


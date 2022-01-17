
from multiprocessing import Process, Queue
import multiprocessing
import os
from time import sleep
from bson.objectid import ObjectId
from pymongo import MongoClient
from new_analyzer import run2
import sys
# def __main__():
#     f_id = 0 #input
#     keyid = 672
#     analyzer = run_factor_integration(keyid, f_id)
    
#     analyzer.run()
#    # analyzer.factor_norm()

class run_factor_integration:
    def __init__(self, keyid, fid):
        self.client =  MongoClient('203.255.92.141:27017', connect=False)
        self.PUBLIC = self.client['PUBLIC']
        self.new_max_factor = self.PUBLIC['new_factor'] 
        self.ID = self.client['ID']
        self.Domestic = self.ID['Domestic']
        self.keyid = keyid
        self.fid = fid
        
        self.DATA = self.ID['Domestic'].find({"keyId":self.keyid, "fid":self.fid})


    def count_people(self):
        cnt = 0
        print(cnt)
        print("실행")
        for i in self.DATA:
            #print(i)
            cnt += 1
        return cnt
    

    def run(self):
     
        print("count_people", self.count_people)
        cnt = self.count_people()
        processList = []
        if None == self.new_max_factor.find_one({'keyId': self.keyid}):
            self.new_max_factor.insert({'keyId': self.keyid},{'keyId': self.keyid, 'Quality' : -1, 'accuracy' : -1, 'recentness' : -1, 'coop': -1 })
        
       
        for i in range(0,cnt , 100):
            start = 1 *i
            end = 100
            if i//100 == cnt//100:
                start = i
                end = cnt
            
            proc = Process(target=run2(start, end, self.fid, self.keyid),daemon = False)
            
            processList.append(proc)
            proc.start()


        for p in processList :
            p.join()
        
        self.factor_norm()
        
        


    def factor_norm(self):
        max_factor = self.new_max_factor.find_one({'keyId':self.keyid})
        print(max_factor)
        max_qual = max_factor['Quality']
        real_qual =1/ max_qual
        print(real_qual)
        print(type(real_qual))
        max_acc = max_factor['accuracy']
        max_recentness = max_factor['recentness']
        max_coop = max_factor['coop']
        print("여기까진 ok")
        self.ID['test'].update_many({'keyId':self.keyid},{"$mul":{'qual': real_qual }})
        print("여기까진 ok2222")






















__main__()

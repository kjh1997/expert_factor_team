
from multiprocessing import Process
import multiprocessing
import os
from bson.objectid import ObjectId
from pymongo import MongoClient
from base_class import run

def __main__():
    keyid = 653
    fid = 0
    analyzer = run_factor_integration(keyid, fid)
    
    analyzer.run()

class run_factor_integration:
    def __init__(self, keyid, fid):
        self.client =  MongoClient('203.255.92.141:27017', connect=False)
        self.PUBLIC = self.client['PUBLIC']
        self.new_max_factor = self.PUBLIC['new_factor'] 
        self.ID = self.client['ID']
        self.Domestic = self.ID['Domestic']
        self.keyid = keyid
        self.fid = fid
        
        self.DATA = self.ID['Domestic'].find({"keyId":self.keyid, "fid":0})
       

    def count_people(self):
        cnt = 0
        print("실행")
        for i in self.DATA:
            #print(i)
            cnt += 1
        return cnt
    

    def run(self):
        cnt = 200
        processList = []
        if None == self.new_max_factor.find_one({'keyId': self.keyid}):
            self.new_max_factor.insert({'keyId': self.keyid},{'keyId': self.keyid, 'Quality' : -1, 'accuracy' : -1, 'recentness' : -1, 'coop': -1 })


        for i in range(0,cnt , 100):
            start = 1 *i
            end = 100
            if i//100 == cnt//100:
                start = i
                end = cnt
            print(end)
            if __name__ == '__main__':
                proc = Process(target=run(start, end, self.fid, self.keyid))
                processList.append(proc)
                proc.start()
        for p in processList :
            p.join()
        
        self.factor_norm()


    def factor_norm(self):
        max_factor = self.new_max_factor.find_one({'keyId':self.keyid})

        max_qual = max_factor['Quality']
        # max_acc = max_factor['accuracy']
        # max_recentness = max_factor['recentness']
        # max_coop = max_factor['coop']
        update_list = self.Domestic.find({"keyId":self.keyid},{'factor':1,"_id":1})
        for doc in update_list:
            if max_qual != 0:
                norm_qual = doc['factor']['qual']/max_qual
            else:
                norm_qual = doc['factor']['qual']

            self.Domestic.update({'_id':ObjectId(doc['_id'])},{"$set":{'factor':{"qual":norm_qual,'coop':doc['factor']['coop'],'recentness':doc['factor']['recentness'],'acc':doc['factor']['acc']}}})
        print("정규화 끝")

__main__()

# from multiprocessing import Process
# import multiprocessing
# import os
# from bson.objectid import ObjectId
# from pymongo import MongoClient
# from base_class import run
# client =  MongoClient('203.255.92.141:27017', connect=False)
# PUBLIC = client['PUBLIC']
# new_max_factor =PUBLIC['new_factor'] 
# ID = client['ID']
# Domestic = ID['Domestic']
# keyid = 653
# fid = 0
# ID = client['ID']
# DATA = ID['Domestic'].find({"keyId":keyid, "fid":0})
# b = 0
# print("실행")
# for i in DATA:
#     #print(i)
#     b += 1
# print(b)  

# PUBLIC = client['PUBLIC']
# new_max_factor = PUBLIC['new_factor'] 
# print(type(new_max_factor.find_one({'keyId': keyid})))
# processList = []
# if None == new_max_factor.find_one({'keyId': keyid}):
#     new_max_factor.insert({'keyId': keyid},{'keyId': keyid, 'Quality' : -1, 'accuracy' : -1, 'recentness' : -1, 'coop': -1 })

# for i in range(0,b , 100):
#     start = 1 *i
#     end = 100
#     if i//100 == b//100:
#         start = i
#         end = b
#    # print(start, end, fid, keyid)
#     if __name__ == '__main__':
#         print("실행",start)
#         proc = Process(target=run(start, end, fid, keyid))
#         processList.append(proc)
#         proc.start()
# for p in processList :
#     p.join()

# max_factor = new_max_factor.find_one({'keyId':keyid})
# #print(max_factor)

# max_qual = max_factor['Quality']
# max_acc = max_factor['accuracy']
# max_recentness = max_factor['recentness']
# max_coop = max_factor['coop']
# update_list = Domestic.find({"keyId":keyid},{'factor':1,"_id":1})
# for doc in update_list:
#     if max_qual != 0:
#         norm_qual = doc['factor']['qual']/max_qual
#     else:
#         norm_qual = doc['factor']['qual']
#     #print(norm_qual, doc['factor']['coop'], doc['factor']['recentness'] , doc['factor']['acc'])
#     Domestic.update({'_id':ObjectId(doc['_id'])},{"$set":{'factor':{"qual":norm_qual,'coop':doc['factor']['coop'],'recentness':doc['factor']['recentness'],'acc':doc['factor']['acc']}}})
# print("정규화 끝")
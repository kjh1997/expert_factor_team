from pymongo import MongoClient

client =  MongoClient('203.255.92.141:27017', connect=False)
DBPIA = client['DBPIA']
DBPIA_Rawdata = DBPIA['Rawdata']
DBPIA_Author = DBPIA['Author']
data = list(DBPIA_Rawdata.find({"keyId":588},{"author_id":1}))
b = []
print("실행")
for i in data:
    data = DBPIA_Author.find({"_id":i["author_id"]},{"name":1,"inst":1})
    print(i['author_id'])

    data = i['author_id'].split(';')
    print(data)
    for j in data:
        data2 = DBPIA_Author.find({"_id":j},{"name":1,"inst":1})
        for c in list(data2):
            b.append(c)
            print(c)
        
        

print(b)
r = open("data.txt", 'w',encoding='utf8')
w = open("DBPIA_sort3.txt", 'w',encoding='utf8')
for i in b:
    i = i['name']+ "," + i['inst']
    r.write(i+"\n")
   
r.close()

r = open('data.txt', 'r',encoding='utf8')
 
#파일에서 읽은 라인들을 리스트로 읽어들임
lines = r.readlines()

#Set에 넣어서 중복 제거 후 다시 리스트 변환
#리스트 정렬
lines.sort()
 
#정렬,중복제거한 리스트 파일 쓰기
for line in lines :
    w.write(line)
 
#파일 닫기
w.close()
r.close()





# r = open("data.txt", 'w',encoding='utf8')
# w = open("DBPIA2_sort.txt", 'w',encoding='utf8')
# for i in b:
#     for c in i:
#         r.write(c+"\n")
   
# r.close()

# r = open('data.txt', 'r',encoding='utf8')
 
# #파일에서 읽은 라인들을 리스트로 읽어들임
# lines = r.readlines()

# #Set에 넣어서 중복 제거 후 다시 리스트 변환
# #리스트 정렬
# lines.sort()
 
# #정렬,중복제거한 리스트 파일 쓰기
# for line in lines :
#     w.write(line)
 
# #파일 닫기
# w.close()
# r.close()



# from pymongo import MongoClient

# client =  MongoClient('203.255.92.141:27017', connect=False)
# KCI = client['DBPIA']
# KCI_Rawdata = KCI['Rawdata']

# data = list(KCI_Rawdata.find({"keyId":587},{"author":1,"author_inst":1}))
# b = []
# for i in data:
#     a = i["author"],i["author_inst"]
#     length = len(str(a).split(";")) -1
#     #print(a)
#     data = str(a).replace("'","").replace("(","").replace(")","").replace(", ","")
#     #print(data)
#     #print(type(data))

#     data = data.split(';')
#     for i in range(int(len(data)/2)):
#         b.append(data[i]+ "," + data[int(len(data)/2)+i])

# print(b)
# r = open("data.txt", 'w',encoding='utf8')
# w = open("DBPIA_sort.txt", 'w',encoding='utf8')
# for i in b:
    
#     r.write(i+"\n")
   
# r.close()

# r = open('data.txt', 'r',encoding='utf8')
 
# #파일에서 읽은 라인들을 리스트로 읽어들임
# lines = r.readlines()

# #Set에 넣어서 중복 제거 후 다시 리스트 변환
# #리스트 정렬
# lines.sort()
 
# #정렬,중복제거한 리스트 파일 쓰기
# for line in lines :
#     w.write(line)
 
# #파일 닫기
# w.close()
# r.close()

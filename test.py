
mngIds = ['318595007279', '318595007279']
A_ID   = '10062717'
point  = []
for i in range(len(mngIds)):
    #print(i)
    
    pt = 0
    temp = 0
    for j in range(len(mngIds[i])):
        if mngIds[i][j] != None:
            if A_ID[i] == mngIds[i][j] :
                print(A_ID,mngIds)
                pt += 10
            else:
                temp += 1
    if pt > 0 : 
        pt += temp
    print("pt",pt)
    point.append(pt)
print(point)
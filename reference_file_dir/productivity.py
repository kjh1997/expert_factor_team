def productivity(pYears):
    dt = datetime.datetime.now()
    rct_list = []
    for i in range(len(pYears)):
        rct = 0
        mean_year = mean(pYears[i])
        for j in range(len(pYears[i])):
            if (mean_year - 5 < pYears[i][j] < mean_year + 5):
                if pYears[i][j] >= int(dt.year)-2: # 최신년도 기준으로 과거 2년까지 +1점
                    rct += 1
                elif int(dt.year)-15 < pYears[i][j] <= int(dt.year)-3: # 최신년도 기준 과거 15년 ~ 과거 2년까지 
                    rct += max(round((1-(int(dt.year)-3-pYears[i][j])*0.1),2), 0)
                else:
                    rct += 0
        if len(pYears[i]) != 0:
            rct_list.append(rct / len(pYears[i]))
        else:
            rct_list.append(0)
    return rct_list

print("생산성 / productivity")
prod = productivity(pYears)
print(prod)
print()
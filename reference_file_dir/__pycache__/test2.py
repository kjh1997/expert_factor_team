def test(bool):
    cnt = 0
    if bool == True:
        for i in range(1,51):
            cnt = i
    else:
        for i in range(50,101):
            cnt = i
    return cnt

sav = test(True)
print(sav)
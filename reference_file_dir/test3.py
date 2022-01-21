# import re
# univ0 = "충북대학교병원"
# univ1 = re.sub("산학협력단|병원","",str(univ0))
# print(univ1)
originalName = "충북대학교;충남대학교;부산대학교;충북대학교;충남대학교;"
x = originalName.split(';')
x = list(set(x))
for num, i in enumerate(x):
    if x[num] == "":
        x.pop(num)


print(x)
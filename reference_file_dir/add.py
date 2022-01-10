def isEnglishOrKorean(input_s):
    k_count = 0
    e_count = 0
    for c in input_s:
        if ord('가') <= ord(c) <= ord('힣'):
            k_count+=1
        elif ord('a') <= ord(c.lower()) <= ord('z'):
            e_count+=1
    return "k" if k_count>1 else "e"

def check_college(univ0):
    branch_set = ['성균관대학교', '건국대학교', '한양대학교']
    univName = client['PUBLIC']['CollegeName']
    univ1 = re.sub("산학협력단|병원","",univ0)
    univ2 = re.sub("대학교","대학교 ",univ1)

    try:
        if isEnglishOrKorean(univ0) == 'e':
            univ0 = univ0.upper()
            univ0 = univ0.replace('.', ',')
            univ = univ0.split(', ')
        else:
            univ = univ2.replace(",", "").split()
            univ = list(set(univ))   
            
        for uni in univ:
            if uni in branch_set:
                if ("ERICA" or "에리카") in univ0:
                    univ[univ.index("한양대학교")] = "한양대학교(ERICA캠퍼스)"
                elif ("글로컬" or "GLOCAL") in univ0:
                    univ[univ.index("건국대학교")] = "건국대학교 GLOCAL(글로컬)캠퍼스"
                elif "자연과학캠퍼스" in univ0:
                    univ[univ.index("성균관대학교")] = "성균관대학교(자연과학캠퍼스)"

        univs = '{"$or": ['
        for u in range(len(univ)):
            if univ[-1] == univ[u]:
                univs += '{"inputName": "' + univ[u] + '"}'
            else:
                univs += '{"inputName": "' + univ[u] + '"}, '
        univs += ']}'

        univ_query = univName.find_one(eval(univs))

        if univ_query is None:
            print("Search inst None")
            return univ0, False
        else:
            #print("rawInput:[",univ0,"]","queryOutput:" ,univ_query['originalName'])
            return univ_query['originalName'], True #univ0, univ_query
        
    except SyntaxError as e:
        print(e)
        print(univ0)
        return univ0, False
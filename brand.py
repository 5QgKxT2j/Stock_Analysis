import jsm
q=jsm.Quotes()
b = q.get_brand()
for i in b.keys():
    for j in b[i]:
        print(j.ccode)


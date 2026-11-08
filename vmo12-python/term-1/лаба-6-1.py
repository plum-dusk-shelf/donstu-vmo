# string = input()
string = 'текст, текст после 1 запятой, текст после 2 запятой'
buff = ''
res = []
for i in string:
    if i == ',':
        res.append(buff)
        buff = ''
        continue
    buff += i

print(res[1], len(res[1]))
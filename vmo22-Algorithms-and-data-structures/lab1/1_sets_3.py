S = set('hfu38382j2hfвыао,.~→')
print(f'{S} power: {len(S)}')

A, B, C, D = set(), set(), set(), set()

for i in S:
    i = i.lower()
    if i in 'абвгдеёжзийклмнопрстуфхцшщъыьэюя':
        A.add(i)

    elif i in 'abcdefghijklmnopqrstuvwxyz':
        B.add(i)

    elif i in '1234567890':
        C.add(i)

    else:
        D.add(i)

print(A, B, C, D, sep='\n')



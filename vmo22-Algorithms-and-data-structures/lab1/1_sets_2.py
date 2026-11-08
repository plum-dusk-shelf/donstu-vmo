sentence1 = 'serve little cabbage dog the pistol during pandemic'
sentence2 = 'the print google dog family umbrella'

set1 = set(sentence1.split())
set2 = set(sentence2.split())

print(f'{set1}\n{set2}')

len1 = len(set1)
len2 = len(set2)
print(f'sentence length difference: {max(len1, len2) - min(len1, len2)}') # а если длинна одинаковая?

matches = []

for word in set1:
    if word in set2:
        matches.append(word)

print(f'sentences intersection: {matches}')
    

base = 10

n = base
a = base
d = base

progression = []

i = 0
while i < n:
    progression.append(a*d**i)
    i += 1

print(progression)
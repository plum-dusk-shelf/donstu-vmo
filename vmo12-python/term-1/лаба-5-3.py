import  math
res = 0
for i in range(-40, 42, 2):
    x = i/10
    if x != -2:
        res = math.cos(x)/(2+x)

    print(res)

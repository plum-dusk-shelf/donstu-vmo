x1, x2, x3 = input().split()

def print_figures(a,b,c):
    s = set()
    string_ = a+b+c
    for i in string_: s.add(i)
    print(s)

print_figures(x1, x2, x3)


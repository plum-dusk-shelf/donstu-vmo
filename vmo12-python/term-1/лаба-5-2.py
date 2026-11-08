from math import factorial

sum = 0
x = int(input())
n = int(input())
fact = 1
for i in range(1, n + 1):
    fact *= i
    sum += (x ** i) / fact
print(sum)

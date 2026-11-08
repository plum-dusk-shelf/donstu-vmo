# Вариант 12
from math import *

print('Задание 1')
lambd, x, R = int(input()), int(input()), int(input())

expression = (2 / sqrt(x)) * ((x - lambd / R) / ((x - lambd / 2) ** 2) ** (1 / 3) + lambd ** 2)

print(expression)


print('Задание 2')
r = int(input())

print((2 * r) ** 2 - pi * r ** 2)


print('Задание 3')
x, y = int(input()), int(input())
x1, y1 = x, y

if x < y:
    x = (x1 + y1) / 2
    y = x1 * y1 * 2

else:
    y = (x1 + y1) / 2
    x = x1 * y1 * 2

print(x, y)


print('Задание 4')
amount = int(input())
points = 0

if amount >= 8:
    points = 60
elif amount >= 6:
    points = 30
elif amount >= 4:
    points = 15
elif amount >= 2:
    points = 5

print(points)

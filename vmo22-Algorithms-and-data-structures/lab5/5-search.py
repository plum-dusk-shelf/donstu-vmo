import random, time
from matplotlib import pyplot as plt

def linear_search(arr, x):
    iters = 0
    arr.append(x)
    for i in range(len(arr)+1):
        iters += 1
        if arr[i] == x:
            return i, iters
    return 'No such element'

def binary_search(arr, x):
    iters = 0
    L, R = 0, len(arr)
    while L < R:
        iters += 1
        c = (L + R) // 2
        if x == arr[c]:
            return c, iters
        if x > arr[c]:
            L = c+1
        else:
            R = c

def create_timer(func, arr, x):
    t0 = time.time()
    index, iters = func(arr, x)
    return time.time() - t0, iters

sizes = [100, 500, 1000, 3000, 10000]
timers_linear = []
timers_binary = []

for size in sizes:
    arr = [i for i in range(size)]
    x = size - 1

    timers_linear.append(create_timer(linear_search, arr, x)[0])
    timers_binary.append(create_timer(binary_search, arr, x)[0])

print(f'{timers_linear}\n{timers_binary}')

fig, (ax1) = plt.subplots(1, 1, figsize=(6, 6))
ax1.plot(sizes, timers_linear)
ax1.plot(sizes, timers_binary)
plt.show()

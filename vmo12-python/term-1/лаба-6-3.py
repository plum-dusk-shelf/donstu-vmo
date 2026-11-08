arr = [11, 12, 13, 14, 16, 18]

if len([x for x in arr if x % 2 == 0]) > len(arr) // 2:
    for i in range(len(arr)):
        if arr[i] % 2 == 0:
            if arr[i]:
                arr[i] += 1

print(arr)
import time
import random
import matplotlib.pyplot as plt
from typing import List, Callable

def bubble_sort(arr: List[int]) -> List[int]:
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def selection_sort(arr: List[int]) -> List[int]:
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def insertion_sort(arr: List[int]) -> List[int]:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def merge_sort(arr: List[int]) -> List[int]:
    if len(arr) > 1:
        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]

        merge_sort(left)
        merge_sort(right)

        i = j = k = 0

        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1
    return arr

def quick_sort(arr: List[int]) -> List[int]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def test_sorting_algorithm(algorithm: Callable[[List[int]], List[int]], 
                          array_size: int, repetitions: int = 10) -> float:
    total_time = 0.0
    for _ in range(repetitions):
        arr = [random.randint(0, 10000) for _ in range(array_size)]
        start_time = time.time()
        algorithm(arr.copy())
        total_time += time.time() - start_time
    return total_time / repetitions

def main():
    algorithms = {
        "Bubble Sort": bubble_sort,
        "Selection Sort": selection_sort,
        "Insertion Sort": insertion_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "Timsort": sorted  # Встроенная сортировка Python (Timsort)
    }

    min_size = 10
    max_size = 10000
    step = 500
    sizes = list(range(min_size, max_size + 1, step))
    
    results = {name: [] for name in algorithms}
    
    for size in sizes:
        print(f"Testing size: {size}")
        for name, algorithm in algorithms.items():
            avg_time = test_sorting_algorithm(algorithm, size)
            results[name].append(avg_time)
            print(f"{name}: {avg_time:.6f} sec")
    
    plt.figure(figsize=(12, 8))
    for name, timings in results.items():
        plt.plot(sizes, timings, label=name)
    
    plt.title("Сравнение алгоритмов сортировки")
    plt.xlabel("Размер массива")
    plt.ylabel("Среднее время выполнения (сек)")
    plt.legend()
    plt.grid(True)
    
    # Увеличиваем масштаб для маленьких размеров массива
    #plt.figure(figsize=(12, 8))
    #for name, timings in results.items():
    #    plt.plot(sizes[:20], timings[:20], label=name)
    
    plt.title("Сравнение алгоритмов сортировки (малые размеры массивов)")
    plt.xlabel("Размер массива")
    plt.ylabel("Среднее время выполнения (сек)")
    plt.legend()
    plt.grid(True)
    
    plt.show()

if __name__ == "__main__":
    main()

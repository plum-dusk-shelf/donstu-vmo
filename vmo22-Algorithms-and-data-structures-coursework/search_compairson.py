import time
import random
import matplotlib.pyplot as plt
from typing import List, Callable, Dict, Optional

def linear_search(arr: List[int], target: int) -> Optional[int]:
    for i, num in enumerate(arr):
        if num == target:
            return i
    return None

def binary_search(arr: List[int], target: int) -> Optional[int]:
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return None

def hash_table_search(arr: List[int], target: int) -> Optional[int]:
    hash_table = {num: i for i, num in enumerate(arr)}
    return hash_table.get(target, None)

def test_search_algorithm(algorithm: Callable[[List[int], int], Optional[int]], 
                         array_size: int, repetitions: int = 10) -> float:
    total_time = 0.0
    for _ in range(repetitions):
        arr = sorted([random.randint(0, 100000) for _ in range(array_size)])  # Сортируем для бинарного поиска
        target = random.choice(arr)  # Гарантируем, что цель есть в массиве
        start_time = time.time()
        algorithm(arr, target)
        total_time += time.time() - start_time
    return total_time / repetitions

def main():
    algorithms = {
        "Linear Search": linear_search,
        "Binary Search": binary_search,
        "Hash Table Search": hash_table_search
    }

    min_size = 10
    max_size = 10000
    step = 500
    sizes = list(range(min_size, max_size + 1, step))
    
    results = {name: [] for name in algorithms}
    
    for size in sizes:
        print(f"Testing size: {size}")
        for name, algorithm in algorithms.items():
            avg_time = test_search_algorithm(algorithm, size)
            results[name].append(avg_time)
            print(f"{name}: {avg_time:.6f} sec")
    
    plt.figure(figsize=(12, 8))
    for name, timings in results.items():
        plt.plot(sizes, timings, label=name)
    
    plt.title("Сравнение алгоритмов поиска")
    plt.xlabel("Размер массива")
    plt.ylabel("Среднее время выполнения (сек)")
    plt.legend()
    plt.grid(True)
    
    # Увеличиваем масштаб для маленьких размеров массива
    plt.figure(figsize=(12, 8))
    for name, timings in results.items():
        plt.plot(sizes[:20], timings[:20], label=name)
    
    plt.title("Сравнение алгоритмов поиска (малые размеры массивов)")
    plt.xlabel("Размер массива")
    plt.ylabel("Среднее время выполнения (сек)")
    plt.legend()
    plt.grid(True)
    
    plt.show()

if __name__ == "__main__":
    main()

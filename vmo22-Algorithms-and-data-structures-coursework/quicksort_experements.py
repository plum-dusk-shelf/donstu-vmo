import random
import time
import matplotlib.pyplot as plt
from typing import List, Callable, Dict

def partition(arr: List[int], low: int, high: int, pivot_choice: str) -> int:
    """Улучшенное разбиение с защитой от зацикливания"""
    if pivot_choice == "first":
        pivot = arr[low]
    elif pivot_choice == "last":
        pivot = arr[high]
        arr[high], arr[low] = arr[low], arr[high]  # Перемещаем pivot в начало
    elif pivot_choice == "middle":
        mid = (low + high) // 2
        pivot = arr[mid]
        arr[mid], arr[low] = arr[low], arr[mid]
    elif pivot_choice == "random":
        rand_idx = random.randint(low, high)
        pivot = arr[rand_idx]
        arr[rand_idx], arr[low] = arr[low], arr[rand_idx]
    
    i = low + 1
    j = high
    
    while True:
        while i <= j and arr[i] <= pivot:
            i += 1
        while i <= j and arr[j] > pivot:
            j -= 1
        if i >= j:
            break
        arr[i], arr[j] = arr[j], arr[i]
    
    arr[low], arr[j] = arr[j], arr[low]
    return j

def quicksort_safe(arr: List[int], pivot_choice: str = "random") -> List[int]:
    """Оптимизированная версия с защитой от зависаний"""
    stack = []
    stack.append((0, len(arr) - 1))
    
    while stack:
        low, high = stack.pop()
        if high - low < 20:  # Переключаемся на сортировку вставками для малых массивов
            insertion_sort(arr, low, high)
            continue
        
        pivot_idx = partition(arr, low, high, pivot_choice)
        
        # Сначала добавляем больший подмассив
        if pivot_idx - low > high - pivot_idx:
            stack.append((low, pivot_idx - 1))
            stack.append((pivot_idx + 1, high))
        else:
            stack.append((pivot_idx + 1, high))
            stack.append((low, pivot_idx - 1))
    
    return arr

def insertion_sort(arr: List[int], low: int, high: int):
    """Сортировка вставками для малых подмассивов"""
    for i in range(low + 1, high + 1):
        key = arr[i]
        j = i - 1
        while j >= low and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

def generate_test_data(size: int, case: str) -> List[int]:
    """Генерация тестовых данных с защитой от патологических случаев"""
    if case == "random":
        return [random.randint(0, size) for _ in range(size)]
    elif case == "sorted":
        return list(range(size))
    elif case == "reverse_sorted":
        return list(range(size, 0, -1))
    elif case == "almost_sorted":
        arr = list(range(size))
        swaps = max(1, size // 10)
        for _ in range(swaps):
            i, j = random.randint(0, size-1), random.randint(0, size-1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    elif case == "many_duplicates":
        return [random.choice([0, 1, size//2, size]) for _ in range(size)]
    else:
        raise ValueError(f"Unknown test case: {case}")

def benchmark():
    sizes = [100, 1000, 5000, 10000]
    cases = ["random", "sorted", "reverse_sorted", "almost_sorted", "many_duplicates"]
    strategies = {
        "First": "first",
        "Last": "last",
        "Middle": "middle",
        "Random": "random"
    }
    
    results = {case_: {strategy: [] for strategy in strategies} for case_ in cases}
    
    for size in sizes:
        print(f"\n\nTesting size: {size}")
        for case_ in cases:
            data = generate_test_data(size, case_)
            print(f"\nCase: {case_:<20}", end="")
            
            for strategy_name, strategy in strategies.items():
                test_data = data.copy()
                start_time = time.perf_counter()
                quicksort_safe(test_data, strategy)
                elapsed = time.perf_counter() - start_time
                
                results[case_][strategy_name].append(elapsed)
                print(f"{strategy_name}: {elapsed:.5f}s | ", end="")
    
    for case_ in cases:
        plt.figure(figsize=(12, 6))
        for strategy in strategies:
            plt.plot(sizes, results[case_][strategy], 
                    label=strategy, marker='o', linestyle='--')
        
        plt.title(f"QuickSort Performance ({case_.replace('_', ' ').title()})")
        plt.xlabel("Array Size")
        plt.ylabel("Time (seconds)")
        plt.legend()
        plt.grid(True)

        filename = f"quicksort_{case_}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')

        plt.show()
        plt.close()

if __name__ == "__main__":
    benchmark()

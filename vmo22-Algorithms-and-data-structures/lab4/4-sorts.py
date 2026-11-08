import random
import time
from matplotlib import pyplot as plt

def insertion_sort(arr):
    comparisons = 0
    swaps = 0
    iterations = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        comparisons += 1
        while j >=0 and key < arr[j] :
            comparisons += 1
            iterations += 1
            swaps += 1
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return comparisons, swaps, iterations

def selection_sort(arr):
    comparisons = 0
    swaps = 0
    iterations = 0
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            comparisons += 1
            iterations += 1
            if arr[min_idx] > arr[j]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        swaps += 1
    return comparisons, swaps, iterations

def bubble_sort(arr):
    comparisons = 0
    swaps = 0
    iterations = 0
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            comparisons += 1
            iterations += 1
            if arr[j] > arr[j+1] :
                swaps += 1
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return comparisons, swaps, iterations

def partition(arr, low, high):
    i = (low-1)
    pivot = arr[high]
    for j in range(low , high):
        if arr[j] <= pivot:
            i = i+1
            arr[i],arr[j] = arr[j],arr[i]
    arr[i+1],arr[high] = arr[high],arr[i+1]
    return (i+1)

def quick_sort(arr, low, high):
    if low < high:
        p = partition(arr, low, high)
        quick_sort(arr, low, p-1)
        quick_sort(arr, p+1, high)
    return arr

def test_sorting_algorithm(sort_func, arr):
    start_time = time.time()
    comparisons, swaps, iterations = sort_func(arr)
    end_time = time.time()
    return end_time - start_time, comparisons, swaps, iterations


array_sizes = [20, 500, 1000, 3000, 5000, 10000]

def presorted_compairson():
    pre_sorts = [0, 25, 50, 75]

    for size in array_sizes:
        for pre_sort in pre_sorts:
            #if size == 20:
            #    arr = list(map(int, input("Enter 20 elements separated by space: ").split()))
            #else:
            arr = [random.randint(1, 10000) for i in range(size)]
            pre_sort_calc = round(size/100*25)
            arr = quick_sort(arr[:pre_sort_calc], 0, pre_sort_calc-1) + arr[pre_sort_calc:]
        
            print(f"\nArray of {size} sorted by {pre_sort}%")
        
            time_taken, comparisons, swaps, iterations = test_sorting_algorithm(insertion_sort, arr.copy())
            print(f"Insertion sort\nTime: {time_taken:.6f}s, Comparisons: {comparisons}, Swaps: {swaps}, Iterations: {iterations}")
        
            time_taken, comparisons, swaps, iterations = test_sorting_algorithm(selection_sort, arr.copy())
            print(f"Selection sort\nTime: {time_taken:.6f}s, Comparisons: {comparisons}, Swaps: {swaps}, Iterations: {iterations}")
        
            time_taken, comparisons, swaps, iterations = test_sorting_algorithm(bubble_sort, arr.copy())
            print(f"Bubble sort\nTime: {time_taken:.6f}s, Comparisons: {comparisons}, Swaps: {swaps}, Iterations: {iterations}")
        
            arr_copy = arr.copy()
            start_time = time.time()
            quick_sort(arr_copy, 0, len(arr_copy)-1)
            end_time = time.time()
            print(f"Quick sort\nTime: {end_time - start_time:.6f}s")

def visual_compairson():
    sorts = [insertion_sort, selection_sort, bubble_sort]
    sorting_memory = {}#sort: size for sort in sorts for size in array_sizes}
    for sort in sorts:
        sorting_memory[sort.__name__] = {}
        for size in array_sizes:
            sorting_memory[sort.__name__][size] = []
            arr = [random.randint(1, 10000) for i in range(size)]
            time_taken, comparisons, swaps, iterations = test_sorting_algorithm(sort, arr.copy())
            sorting_memory[sort.__name__][size] = [time_taken, comparisons, swaps, iterations]
            print(f'{sort.__name__} {size:05} done')
    
    plt.style.use('seaborn-v0_8')

    fig, ax = plt.subplots(figsize=(10, 6))

    for method_name, sizes_data in sorting_memory.items():
        # Извлекаем размеры массивов и соответствующие времена
        sizes = sorted(sizes_data.keys())
        times = [sizes_data[size][0] for size in sizes]  # время — первый элемент
        
        # Строим график для текущего метода
        ax.plot(sizes, times, marker='o', label=method_name, linewidth=2)

    ax.set_title('Зависимость времени сортировки от размера массива', fontsize=14)
    ax.set_xlabel('Размер массива', fontsize=12)
    ax.set_ylabel('Время (сек)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(fontsize=10)

    ax.ticklabel_format(style='plain', axis='x')  # отключаем научную нотацию для оси X

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    visual_compairson()

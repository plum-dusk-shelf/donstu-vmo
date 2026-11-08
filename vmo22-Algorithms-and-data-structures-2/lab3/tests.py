import time
import random
from typing import Callable

from rb_set import SetRB
from randomized_set import SetR
from  avl_set import SetAVL

def test_search_performance(set_class: Callable, size: int, repeats: int = 10000):
    tree = set_class()
    keys = [random.randint(0, 10 * size) for _ in range(size)]
    for key in keys:
        tree.insert(key)

    search_key = random.choice(keys)

    start_time = time.perf_counter_ns()

    for _ in range(repeats):
        tree.search(search_key)

    total_time = time.perf_counter_ns() - start_time
    avg_time = total_time / repeats

    return avg_time


def run_tests(sizes: list, repeats: int = 10000):
    implementations = [
        ("Binary Search Tree", SetR),
        ("AVL Tree", SetAVL),
        ("Red-Black Tree", SetRB)
    ]

    results = {name: [] for name, _ in implementations}

    for size in sizes:
        print(f"\nTesting size: {size}")
        for name, impl in implementations:
            avg_time = test_search_performance(impl, size, repeats)
            results[name].append(avg_time)
            print(f"{name}: {avg_time:.2f} наносекунд")

    return results


tree_sizes = [100, 1000, 10000, 100000]
repeats = 100000

results = run_tests(tree_sizes, repeats)
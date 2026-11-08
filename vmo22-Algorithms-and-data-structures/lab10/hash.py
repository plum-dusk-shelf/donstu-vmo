import os

class HashTable:
    def __init__(self, size):
        self.size = size
        self.buckets = [f"bucket_{i}.txt" for i in range(size)]
        self._initialize_buckets()

    def _initialize_buckets(self):
        for bucket in self.buckets:
            if not os.path.exists(bucket):
                with open(bucket, 'w') as f:
                    pass

    def _hash(self, key):
        return sum(ord(char) for char in key) % self.size

    def insert(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        with open(bucket, 'a') as f:
            f.write(key + '\n')

    def search(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        steps = 0
        with open(bucket, 'r') as f:
            for line in f:
                steps += 1
                if line.strip() == key:
                    return steps
        return -1

    def display(self):
        for i, bucket in enumerate(self.buckets):
            print(f"Bucket {i}:", end=" ")
            with open(bucket, 'r') as f:
                for line in f:
                    print(line.strip(), end=" -> ")
            print("None")

keys = ["apple", "banana", "grape", "orange", "pear", "kiwi"]
hash_table = HashTable(5)

for key in keys:
    hash_table.insert(key)

hash_table.display()

search_keys = ["apple", "banana", "grape", "orange", "pear", "kiwi", "mango"]
for key in search_keys:
    steps = hash_table.search(key)
    if steps == -1:
        print(f"{key} not found")
    else:

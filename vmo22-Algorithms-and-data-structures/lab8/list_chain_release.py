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

class Node:
    def __init__(self, value):
        self.value = value
        self.fllwing = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.count = 0

    def append(self, value):
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            return
        last = self.head
        while last.fllwing:
            last = last.fllwing
        last.fllwing = new_node

        self.count += 1

    def add_element(self, value):
        new_node = Node(value)
        new_node.fllwing = self.head
        self.head = new_node
        self.count += 1
        
    def get_element(self, index):
        current = self.head
        for i in range(index):
            if current.fllwing:
                current = current.fllwing
            else:
                raise Exception('Index out of range')

        return current.value

    def delete_element(self, key):
        current = self.head

        if current and current.value == key:
            self.head = current.fllwing
            current = None
            return

        prev = None
        while current and current.value != key:
            prev = current
            current = current.fllwing

        if current is None:
            return

        prev.fllwing = current.fllwing
        current = None

    def get_all(self):
        current = self.head
        memory = []
        while current:
            memory.append(current.value)
            current = current.fllwing
        return memory

    def sort(self):
        memory = self.get_all()
        low, high = 0, self.count
        return quick_sort(memory, low, high)



if __name__ == "__main__":
    list1 = LinkedList()
    list1.append(1)
    list1.append(3)
    list1.append(2)
    list1.add_element(0)
    print(list1.sort())
    print(list1.get_element(1))
    list1.delete_element(2)
    print(list1.get_all())

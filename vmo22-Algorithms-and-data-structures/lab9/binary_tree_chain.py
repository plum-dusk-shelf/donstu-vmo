import random


def snif_down(a, n, pos):
    pass


def heap_sort(a, n):
    # строим пирамиду
    i = len(a) // 2 - 1  # индекс крайнего правого элемента с потомками
    while i >= 0:
        snif_down(a, n, i)
        i += 1

    j = len(a) - 1
    while j > 0:
        temp = a[0]
        a[0] = a[j]
        a[j] = temp
        n -= 1
        snif_down(a, n, 0)
        i -= 1


class ChainLink:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class BinaryTree:
    def __init__(self):
        self.root = None

    def add_element(self, value):
        if not self.root:
            self.root = ChainLink(value)
        else:
            self._insert(self.root, value)

    # красивое
    def _insert(self, node, value):
        if value < node.value:
            if not node.left:
                node.left = ChainLink(value)
                return
            self._insert(node.left, value)
            print('Added to left')
            return
        if not node.right:
            node.right = ChainLink(value)
            return
        self._insert(node.right, value)
        print('Added to right')

    def from_list(self, arr):
        for value in arr:
            self.add_element(value)

    def inorder_traversal(self):
        return self._inorder_traversal(self.root, [])

    def _inorder_traversal(self, node, result):
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node.value)
            self._inorder_traversal(node.right, result)

    def search(self, key, barrier=None):
        self.comparison_count = 0
        self.transition_count = 0
        return self._search(self.root, key, barrier)

    def _search(self, node, key, barrier):
        if node is None:
            return False

        self.comparison_count += 1
        if barrier is not None and self.comparison_count > barrier:
            return False

        if key == node.value:
            return self.comparison_count
        elif key < node.value:
            self.transition_count += 1
            return self._search(node.left, key, barrier)
        else:
            self.transition_count += 1
            return self._search(node.right, key, barrier)

def main():
    bintree1 = BinaryTree()
    bintree1.from_list(random.sample([1, 6, 7, 1, 3, 14, 56, 2], 8))
    bintree1.inorder_traversal()
    print(bintree1.search(14))


if __name__ == '__main__':
    main()

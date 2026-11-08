from collections import deque


class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.count = 1

    def __str__(self):
        return f"{self.value}({self.count})"


class BinarySearchTree:
    def __init__(self):
        self.root = None
        self._size = 0

    def is_empty(self):
        return self.root is None

    def insert(self, value):
        if self.root is None:
            self.root = BSTNode(value)
            self._size += 1
            return True

        current = self.root
        while True:
            if value == current.value:
                return False
            elif value < current.value:
                if current.left is None:
                    current.left = BSTNode(value)
                    self._size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = BSTNode(value)
                    self._size += 1
                    return True
                current = current.right

    def _find_node_and_parent(self, value):
        parent = None
        current = self.root

        while current:
            if value == current.value:
                return parent, current
            parent = current
            if value < current.value:
                current = current.left
            else:
                current = current.right
        return None, None

    def contains(self, value):
        return self.find(value) is not None

    def find(self, value):
        _, node = self._find_node_and_parent(value)
        return node

    def delete(self, value):
        parent, node_to_delete = self._find_node_and_parent(value)
        if node_to_delete is None:
            return False

        if node_to_delete.left is None or node_to_delete.right is None:
            new_child = node_to_delete.left if node_to_delete.left else node_to_delete.right

            if parent is None:
                self.root = new_child
            elif parent.left == node_to_delete:
                parent.left = new_child
            else:
                parent.right = new_child

            self._size -= 1
            return True

        successor_parent = node_to_delete
        successor = node_to_delete.right
        while successor.left:
            successor_parent = successor
            successor = successor.left

        node_to_delete.value = successor.value
        node_to_delete.count = successor.count

        if successor_parent.left == successor:
            successor_parent.left = successor.right
        else:
            successor_parent.right = successor.right

        self._size -= 1
        return True

    def inorder(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append((node.value, getattr(node, 'count', 1)))
            self._inorder_recursive(node.right, result)

    def size(self):
        return self._size

    def __iter__(self):
        return iter(self.inorder())


class MultiSetBST(BinarySearchTree):
    def __init__(self):
        super().__init__()
        self.total = 0

    def insert(self, value):
        self.total += 1
        if self.root is None:
            self.root = BSTNode(value)
            self._size += 1
            return True

        current = self.root
        while True:
            if value == current.value:
                current.count += 1
                return True
            elif value < current.value:
                if current.left is None:
                    current.left = BSTNode(value)
                    self._size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = BSTNode(value)
                    self._size += 1
                    return True
                current = current.right

    def add(self, value):
        return self.insert(value)

    def remove(self, value):
        node = super().find(value)
        if node is None:
            return False

        self.total -= 1
        if node.count > 1:
            node.count -= 1
            return True

        return super().delete(value)

    def remove_all(self, value):
        node = super().find(value)
        if node is None:
            return False

        self.total -= node.count
        return super().delete(value)

    def count(self, value):
        node = super().find(value)
        return node.count if node else 0

    def total_elements(self):
        return self.total

    def distinct_elements(self):
        return super().size()

    def __len__(self):
        return self.total

    def __contains__(self, value):
        return super().contains(value)

    def __str__(self):
        items = super().inorder()
        return "{" + ", ".join(f"{val}[{cnt}]" for val, cnt in items) + "}"

    def sorted(self):
        result = []
        self.inorder_collect(self.root, result)
        return result

    def inorder_collect(self, node, result):
        if node:
            self.inorder_collect(node.left, result)
            result.extend([node.value] * node.count)
            self.inorder_collect(node.right, result)


def MultisetBST_test():
    print("Создаем мультимножество:")
    mset = MultiSetBST()
    elements = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 5]
    for elem in elements:
        mset.add(elem)

    print("Мультимножество:", mset)
    print("Все элементы:", list(mset))
    print("Общее количество элементов:", len(mset))
    print("Уникальных элементов:", mset.distinct_elements())

    print("\nПроверка операций:")
    print("Количество 5:", mset.count(5))
    print("Содержит 9?", 9 in mset)

    print("\nУдаление:")
    mset.remove(5)
    print("После удаления одной 5:", mset)
    mset.remove_all(1)
    print("После удаления всех 1:", mset)

    print(mset.sorted())
    print(mset)

if __name__ == "__main__":
    MultisetBST_test()
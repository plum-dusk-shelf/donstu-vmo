import random


class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.size = 1


class RandomizedBST:
    def __init__(self):
        self.root = None

    def _size(self, node):
        return node.size if node else 0

    def _update_size(self, node):
        if node:
            node.size = 1 + self._size(node.left) + self._size(node.right)

    def empty(self):
        return self.root is None

    def _rotate_right(self, y):
        x = y.left
        y.left = x.right
        x.right = y
        self._update_size(y)
        self._update_size(x)
        return x

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        y.left = x
        self._update_size(x)
        self._update_size(y)
        return y

    def _insert_at_root(self, node, key):
        if not node:
            return Node(key)

        if key < node.key:
            node.left = self._insert_at_root(node.left, key)
            return self._rotate_right(node)
        else:
            node.right = self._insert_at_root(node.right, key)
            return self._rotate_left(node)

    def insert_at_root(self, key):
        self.root = self._insert_at_root(self.root, key)

    def _insert(self, node, key):
        if not node:
            return Node(key)

        if random.randint(0, self._size(node)) == 0:
            return self._insert_at_root(node, key)

        if key < node.key:
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)

        self._update_size(node)
        return node

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def search(self, key):
        node = self.root
        while node:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def _print_tree(self, node, level=0, prefix="Root: "):
        if node:
            print(" " * (level * 4) + prefix + str(node.key) + f" (size={node.size})")
            self._print_tree(node.left, level + 1, "L ")
            self._print_tree(node.right, level + 1, "R ")

    def print_tree(self):
        self._print_tree(self.root)

    def _search(self, node, key):
        if not node:
            return None
        if key == node.key:
            return node
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def _min_node(self, node):
        current = node
        while current and current.left:
            current = current.left
        return current

    def _remove(self, node, key):
        if not node:
            return None

        if key < node.key:
            node.left = self._remove(node.left, key)
        elif key > node.key:
            node.right = self._remove(node.right, key)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            else:
                temp = self._min_node(node.right)
                node.key = temp.key
                node.right = self._remove(node.right, temp.key)

        self._update_size(node)
        return node

    def _to_list(self, node):
        if not node:
            return []
        return self._to_list(node.left) + [node.key] + self._to_list(node.right)



def main():
    tree = RandomizedBST()

    print("Дерево пустое?", tree.empty())

    keys = [5, 3, 7, 2, 4, 6, 8]
    for key in keys:
        tree.insert(key)

    print("\nДерево после вставки элементов:")
    tree.print_tree()

    print("\nДерево пустое?", tree.empty())

    search_key = 4
    node = tree.search(search_key)
    print(f"\nПоиск ключа {search_key}: {'найден' if node else 'не найден'}")

    new_root_key = 10
    print(f"\nДобавляем {new_root_key} как корень дерева")
    tree.insert_at_root(new_root_key)
    tree.print_tree()


if __name__ == '__main__':
    main()

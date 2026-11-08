class Node:
    def __init__(self, key, value=None, color='R'):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.color = color


class RBTree:
    def __init__(self):
        self.NIL = Node(key=None, color='B')
        self.root = self.NIL

    def is_empty(self):
        return self.root == self.NIL

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node == self.NIL or key == node.key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def insert(self, key, value=None):
        new_node = Node(key, value)
        new_node.left = self.NIL
        new_node.right = self.NIL

        parent = None
        current = self.root

        while current != self.NIL:
            parent = current
            if new_node.key < current.key:
                current = current.left
            else:
                current = current.right

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif new_node.key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        new_node.color = 'R'

        self._fix_insert(new_node)

    def _fix_insert(self, node):
        while node != self.root and node.parent.color == 'R':
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle.color == 'R':
                    # Случай 1: дядя красный
                    node.parent.color = 'B'
                    uncle.color = 'B'
                    node.parent.parent.color = 'R'
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        # Случай 2: дядя черный и узел - правый потомок
                        node = node.parent
                        self._left_rotate(node)
                    # Случай 3: дядя черный и узел - левый потомок
                    node.parent.color = 'B'
                    node.parent.parent.color = 'R'
                    self._right_rotate(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle.color == 'R':
                    # Случай 1: дядя красный
                    node.parent.color = 'B'
                    uncle.color = 'B'
                    node.parent.parent.color = 'R'
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        # Случай 2: дядя черный и узел - левый потомок
                        node = node.parent
                        self._right_rotate(node)
                    # Случай 3: дядя черный и узел - правый потомок
                    node.parent.color = 'B'
                    node.parent.parent.color = 'R'
                    self._left_rotate(node.parent.parent)

        self.root.color = 'B'

    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        y.right = x
        x.parent = y

    def print_tree(self):
        self._print_tree(self.root, "", True)

    def _print_tree(self, node, indent, last):
        if node != self.NIL:
            print(indent, end='')
            if last:
                print("R----", end='')
                indent += "     "
            else:
                print("L----", end='')
                indent += "|    "

            color = "R" if node.color == 'R' else "B"
            print(f"{node.key}({color})")
            self._print_tree(node.left, indent, False)
            self._print_tree(node.right, indent, True)

    def remove_even(self):
        even_keys = []
        self._collect_even_keys(self.root, even_keys)

        for key in even_keys:
            self.delete(key)

    def _collect_even_keys(self, node, even_keys):
        if node != self.NIL:
            if node.key % 2 == 0:
                even_keys.append(node.key)
            self._collect_even_keys(node.left, even_keys)
            self._collect_even_keys(node.right, even_keys)

    def delete(self, key):
        node = self.search(key)
        if node == self.NIL:
            return  # Узел не найден

        self._delete_node(node)

    def _delete_node(self, node):
        y = node
        y_original_color = y.color
        if node.left == self.NIL:
            x = node.right
            self._transplant(node, node.right)
        elif node.right == self.NIL:
            x = node.left
            self._transplant(node, node.left)
        else:
            y = self._minimum(node.right)
            y_original_color = y.color
            x = y.right
            if y.parent == node:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = node.right
                y.right.parent = y

            self._transplant(node, y)
            y.left = node.left
            y.left.parent = y
            y.color = node.color

        if y_original_color == 'BLACK':
            self._fix_delete(x)

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _minimum(self, node):
        while node.left != self.NIL:
            node = node.left
        return node

    def _fix_delete(self, x):
        self._fix_insert(x)

def main2():
    rbt = RBTree()
    numbers = [15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9]

    for num in numbers:
        rbt.insert(num)

    print("Исходное дерево:")
    rbt.print_tree()

    print("\nУдаляем четные значения...")
    rbt.remove_even()

    print("\nДерево после удаления четных значений:")
    rbt.print_tree()

def main1():
    rbt = RBTree()

    print("Дерево пустое?", rbt.is_empty())

    keys = [10, 20, 30, 15, 25, 5, 35, 40]
    for key in keys:
        rbt.insert(key)

    print("Дерево пустое?", rbt.is_empty())

    print("Поиск 20:", "Найден" if rbt.search(20) != rbt.NIL else "Не найден")
    print("Поиск 100:", "Найден" if rbt.search(100) != rbt.NIL else "Не найден")

    print("\nСтруктура дерева:")
    rbt.print_tree()

if __name__ == '__main__':
    main2()

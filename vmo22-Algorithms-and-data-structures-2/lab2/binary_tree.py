from collections import deque


class BinaryTreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.count = 1

    def str(self):
        return f"{self.value}({self.count})"


class BinaryTree:
    def __init__(self):
        self.root = None
        self.size = 0

    def is_empty(self):
        return self.root is None

    def insert(self, value):
        new_node = BinaryTreeNode(value)
        if self.is_empty():
            self.root = new_node
            self.size += 1
            return

        queue = deque()
        queue.append(self.root)

        while queue:
            current = queue.popleft()

            if current.left is None:
                current.left = new_node
                self.size += 1
                return
            else:
                queue.append(current.left)

            if current.right is None:
                current.right = new_node
                self.size += 1
                return
            else:
                queue.append(current.right)

    def find_recursive(self, node, value):
        if node is None:
            return None

        if node.value == value:
            return node

        left_result = self.find_recursive(node.left, value)
        if left_result is not None:
            return left_result

        return self.find_recursive(node.right, value)

    def find(self, value):
        return self.find_recursive(self.root, value)

    def get_deepest_node(self):
        if self.is_empty():
            return None

        queue = deque()
        queue.append(self.root)
        deepest_node = None

        while queue:
            deepest_node = queue.popleft()

            if deepest_node.left:
                queue.append(deepest_node.left)
            if deepest_node.right:
                queue.append(deepest_node.right)

        return deepest_node

    def delete_deepest_node(self, deepest_node):
        if self.is_empty():
            return

        queue = deque()
        queue.append(self.root)

        while queue:
            current = queue.popleft()

            if current is deepest_node:
                current = None
                return

            if current.left:
                if current.left is deepest_node:
                    current.left = None
                    return
                else:
                    queue.append(current.left)

            if current.right:
                if current.right is deepest_node:
                    current.right = None
                    return
                else:
                    queue.append(current.right)

    def delete(self, value):
        if self.is_empty():
            return False

        node_to_delete = self.find(value)
        if node_to_delete is None:
            return False

        deepest_node = self.get_deepest_node()
        if deepest_node is None:
            return False

        node_to_delete.value = deepest_node.value

        self.delete_deepest_node(deepest_node)
        self.size -= 1
        return True

    def tree_nodes(self):
        if self.is_empty():
            return []

        result = []
        queue = deque()
        queue.append(self.root)

        while queue:
            levelsize = len(queue)
            current_level = []

            for _ in range(levelsize):
                node = queue.popleft()
                current_level.append(node)

                if node:
                    queue.append(node.left)
                    queue.append(node.right)

            if any(current_level):
                result.append(current_level)

        return result

    def display(self):
        if self.is_empty():
            print("Дерево пусто")
            return

        levels = self.tree_nodes()
        max_level = len(levels)
        max_width = 2 ** (max_level + 1)

        for i, level in enumerate(levels):
            spaces_before = 2 ** (max_level - i + 1) - 1
            spaces_between = 2 ** (max_level - i + 2) - 1

            print(" " * spaces_before, end="")

            for j, node in enumerate(level):
                if node:
                    print(node.value, end="")
                else:
                    print(" ", end="")

                if j < len(level) - 1:
                    print(" " * spaces_between, end="")

            print()

    def depth_recursive(self):
        result = []
        self.depth_recursion(self.root, result)
        return result

    def depth_recursion(self, node, result):
        if node:
            result.append(node.value)
            self.depth_recursion(node.left, result)
            self.depth_recursion(node.right, result)

    def depth(self):
        if self.is_empty():
            return []

        result = []
        queue = deque()
        queue.append(self.root)

        while queue:
            node = queue.popleft()
            result.append(node.value)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        return result

    def contains(self, value):
        return self.find(value) is not None

    def height(self, node):
        if node is None:
            node = self.root
            if node is None:
                return 0

        return self.height_recursive(node)

    def height_recursive(self, node) -> int:
        if node is None:
            return 0

        left_height = self.height_recursive(node.left)
        right_height = self.height_recursive(node.right)

        return max(left_height, right_height) + 1

    def find_node_and_parent(self, value):
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

    def __iter__(self):
        if self.is_empty():
            return iter([])

        queue = deque()
        queue.append(self.root)

        while queue:
            node = queue.popleft()
            yield node.value

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    def is_bst(self):
        """Проверяет, является ли дерево двоичным деревом поиска (BST)."""
        if self.is_empty():
            return True

        # Вспомогательная функция для рекурсивной проверки
        def _is_bst_helper(node, min_val=float('-inf'), max_val=float('inf')):
            if node is None:
                return True

            # Проверяем, что значение узла находится в допустимых границах
            if not (min_val < node.value < max_val):
                return False

            # Рекурсивно проверяем левое и правое поддеревья
            return (_is_bst_helper(node.left, min_val, node.value)) and (_is_bst_helper(node.right, node.value, max_val))

        return _is_bst_helper(self.root)

class BinarySearchTree(BinaryTree):
    def insert(self, value):
        if self.contains(value):
            return False

        new_node = BinaryTreeNode(value)
        if self.is_empty():
            self.root = new_node
            self.size += 1
            return True

        current = self.root
        while True:
            if value < current.value:
                if current.left is None:
                    current.left = new_node
                    self.size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    self.size += 1
                    return True
                current = current.right

    def delete(self, value):
        """Удаление узла с сохранением свойств BST"""
        parent, node_to_delete = self.find_node_and_parent(value)
        if node_to_delete is None:
            return False

        # Случай 1: Нет детей или только один ребенок
        if node_to_delete.left is None or node_to_delete.right is None:
            new_child = node_to_delete.left if node_to_delete.left else node_to_delete.right

            if parent is None:
                self.root = new_child
            elif parent.left == node_to_delete:
                parent.left = new_child
            else:
                parent.right = new_child

            self.size -= 1
            return True

        # Случай 2: Два ребенка
        # Находим преемника (минимальный в правом поддереве)
        successor_parent = node_to_delete
        successor = node_to_delete.right
        while successor.left:
            successor_parent = successor
            successor = successor.left

        # Копируем значение преемника
        node_to_delete.value = successor.value

        # Удаляем преемника
        if successor_parent.left == successor:
            successor_parent.left = successor.right
        else:
            successor_parent.right = successor.right

        self.size -= 1
        return True

    def _find_min(self, node):
        while node.left:
            node = node.left
        return node

    def depth_recursive(self):
        result = []
        self.depth_recursion(self.root, result)
        return result

    def depth_recursion(self, node, result):
        if node:
            self.depth_recursion(node.left, result)
            result.append(node.value)
            self.depth_recursion(node.right, result)

    def split(self, value):
        """Разделяет дерево на два по указанному значению.
        Возвращает два дерева: одно с элементами <= value, другое с элементами > value.
        Узел с указанным значением попадает в первое дерево."""
        left_tree = BinarySearchTree()
        right_tree = BinarySearchTree()

        if self.root is None:
            return left_tree, right_tree

        stack = [(self.root, False)]

        while stack:
            node, processed = stack.pop()
            if not processed:
                if node.right:
                    stack.append((node.right, False))
                stack.append((node, True))
                if node.left:
                    stack.append((node.left, False))
            else:
                if node.value <= value:
                    left_tree.insert(node.value)
                else:
                    right_tree.insert(node.value)

        return left_tree, right_tree

    @staticmethod
    def merge(left_tree, right_tree):
        """Объединяет два BST в один. Все элементы left_tree должны быть <= всех элементов right_tree."""
        merged_tree = BinarySearchTree()

        # Добавляем все элементы из левого дерева
        if left_tree.root:
            stack = [left_tree.root]
            while stack:
                node = stack.pop()
                merged_tree.insert(node.value)
                if node.right:
                    stack.append(node.right)
                if node.left:
                    stack.append(node.left)

        # Добавляем все элементы из правого дерева
        if right_tree.root:
            stack = [right_tree.root]
            while stack:
                node = stack.pop()
                merged_tree.insert(node.value)
                if node.right:
                    stack.append(node.right)
                if node.left:
                    stack.append(node.left)

        return merged_tree


class MySet:
    def __init__(self, elements=None):
        self.bst = BinarySearchTree()
        if elements:
            for elem in elements:
                self.add(elem)

    def is_empty(self):
        return self.bst.is_empty()

    def add(self, element):
        return self.bst.insert(element)

    def remove(self, element):
        return self.bst.delete(element)

    def contains(self, element):
        return self.bst.contains(element)

    def intersection(self, other_set):
        result = MySet()
        for elem in self:
            if other_set.contains(elem):
                result.add(elem)
        return result

    def union(self, other_set):
        result = MySet()
        for elem in self:
            result.add(elem)
        for elem in other_set:
            result.add(elem)
        return result

    def difference(self, other_set):
        result = MySet()
        for elem in self:
            if not other_set.contains(elem):
                result.add(elem)
        return result

    def __iter__(self):
        return iter(self.bst)

    def __len__(self):
        return self.bst.size

    def __str__(self):
        return "{" + ", ".join(map(str, self)) + "}"

    def __contains__(self, element):
        return self.contains(element)

    def __sub__(self, other):
        return self.difference(other)

    def __or__(self, other):
        return self.union(other)

    def __and__(self, other):
        return self.intersection(other)


def BST_test():
    bst = BinarySearchTree()

    values = [50, 30, 70, 20, 40, 60, 80]
    for val in values:
        bst.insert(val)

    print("\nДерево после вставки:")
    bst.display()

    print("\nКоличество узлов:", bst.size)
    print("Высота дерева:", bst.height(None))
    print("Содержит 40?", bst.contains(40))
    print("Содержит 99?", bst.contains(99))

    print("\nСимметричный обход:", bst.depth_recursive())

    print("\nУдаляем 20 (лист):", bst.delete(20))
    print("Удаляем 30 (с одним ребенком):", bst.delete(30))
    print("Удаляем 50 (корень с двумя детьми):", bst.delete(50))

    print("\nДерево после удаления:")
    bst.display()


def BT_test():
    tree = BinaryTree()

    tree.display()
    print()

    tree.insert(10)
    tree.insert(5)
    tree.insert(15)
    tree.insert(3)
    tree.insert(7)
    tree.insert(12)
    tree.insert(18)

    tree.display()
    print()

    tree.delete(10)

    tree.display()
    print()

    print(tree.depth())
    print(tree.depth_recursive())


def split_merge_test():
    print("\nТестирование split и merge:")
    bst = BinarySearchTree()
    values = [50, 30, 70, 20, 40, 60, 80, 35, 45]
    for val in values:
        bst.insert(val)

    print("\nИсходное дерево:")
    bst.display()

    # Тестирование split
    split_value = 40
    left, right = bst.split(split_value)

    print(f"\nЛевое дерево (<= {split_value}):")
    left.display()
    print(f"\nПравое дерево (> {split_value}):")
    right.display()

    # Тестирование merge
    merged = BinarySearchTree.merge(left, right)
    print("\nОбъединенное дерево:")
    merged.display()

    print("\n\nОбъединенное дерево является двоичным деревом поиска" * merged.is_bst())


def MySet_test():
    print("Создаем множества:")
    set1 = MySet([1, 2, 3, 4, 5])
    set2 = MySet([4, 5, 6, 7, 8])

    print("Множество 1:", set1)
    print("Множество 2:", set2)

    print("\nПроверка операций:")
    print("Пересечение:", set1 & set2)
    print("Объединение:", set1 | set2)
    print("Разность (set1 - set2):", set1 - set2)
    print("Разность (set2 - set1):", set2 - set1)

    print("\nПроверка принадлежности:")
    print("3 в set1?", 3 in set1)
    print("9 в set1?", 9 in set1)

    print("\nДобавление и удаление элементов:")
    set1.add(6)
    set1.remove(2)
    print("Множество 1 после изменений:", set1)

    print("\nРазмер множества 1:", len(set1))
    print("Множество 1 пустое?", set1.is_empty())


if __name__ == "__main__":
    split_merge_test()

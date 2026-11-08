from avl_tree import AVLTree


class SetAVL(AVLTree):

    def __init__(self):
        super().__init__()

    def add(self, value):
        super().insert(value)

    def contains(self, value):
        return super().search(value) is not None

    def remove(self, value):
        self.root = self._remove(self.root, value)

    def _remove(self, node, value):
        if node is None:
            return node

        if value < node.key:
            node.left = self._remove(node.left, value)
        elif value > node.key:
            node.right = self._remove(node.right, value)
        else:
            if node.left is None:
                temp = node.right
                node = None
                return temp
            elif node.right is None:
                temp = node.left
                node = None
                return temp

            temp = self._get_min_value_node(node.right)
            node.key = temp.key
            node.right = self._remove(node.right, temp.key)

        if node is None:
            return node

        node.height = 1 + max(self._get_height(node.left),
                              self._get_height(node.right))

        balance = self._get_balance(node)

        # Левый левый случай
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)

        # Левый правый случай
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Правый правый случай
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)

        # Правый левый случай
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _get_min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def union(self, other_set):
        result = SetAVL()
        self._add_all_nodes_to_set(self.root, result)
        self._add_all_nodes_to_set(other_set.root, result)
        return result

    def intersection(self, other_set):
        result = SetAVL()
        self._intersection_helper(self.root, other_set, result)
        return result

    def _intersection_helper(self, node, other_set, result):
        if node is None:
            return
        if other_set.contains(node.key):
            result.add(node.key)
        self._intersection_helper(node.left, other_set, result)
        self._intersection_helper(node.right, other_set, result)

    def difference(self, other_set):
        result = SetAVL()
        self._difference_helper(self.root, other_set, result)
        return result

    def _difference_helper(self, node, other_set, result):
        if node is None:
            return
        if not other_set.contains(node.key):
            result.add(node.key)
        self._difference_helper(node.left, other_set, result)
        self._difference_helper(node.right, other_set, result)

    def _add_all_nodes_to_set(self, node, target_set):
        if node is None:
            return
        target_set.add(node.key)
        self._add_all_nodes_to_set(node.left, target_set)
        self._add_all_nodes_to_set(node.right, target_set)

    def __contains__(self, value):
        """Поддержка оператора 'in'"""
        return self.contains(value)

    def __or__(self, other):
        return self.union(other)

    def __and__(self, other):
        return self.intersection(other)

    def __sub__(self, other):
        return self.difference(other)

    def __str__(self):
        elements = []
        self._inorder_traversal(self.root, elements)
        return "{" + ", ".join(map(str, elements)) + "}"

    def _inorder_traversal(self, node, elements):
        if node:
            self._inorder_traversal(node.left, elements)
            elements.append(node.key)
            self._inorder_traversal(node.right, elements)

def main():
    set1 = SetAVL()
    set1.add(5)
    set1.add(10)
    set1.add(15)
    set1.add(20)

    set2 = SetAVL()
    set2.add(10)
    set2.add(20)
    set2.add(25)
    set2.add(30)

    print("Множество 1:", set1)
    print("Множество 2:", set2)

    print("10 в set1?", 10 in set1)
    print("25 в set1?", 25 in set1)

    print("Объединение:", set1 | set2)
    print("Пересечение:", set1 & set2)
    print("Разность set1 - set2:", set1 - set2)

    set1.remove(10)
    print("После удаления 10:", set1)

if __name__ == '__main__':
    main()
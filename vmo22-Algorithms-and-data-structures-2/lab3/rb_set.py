from rb_tree import RBTree


class SetRB(RBTree):
    def __init__(self):
        super().__init__()

    def add(self, value):
        self.insert(value, value)

    def remove(self, value):
        node = self.search(value)
        if node != self.NIL:
            pass

    def contains(self, value):
        return self.search(value) != self.NIL

    def __contains__(self, value):
        return self.contains(value)

    def __iter__(self):
        return self._inorder_traversal(self.root)

    def _inorder_traversal(self, node):
        if node != self.NIL:
            yield from self._inorder_traversal(node.left)
            yield node.key
            yield from self._inorder_traversal(node.right)

    def union(self, other_set):
        result = SetRB()
        for value in self:
            result.add(value)
        for value in other_set:
            result.add(value)
        return result

    def intersection(self, other_set):
        result = SetRB()
        for value in self:
            if value in other_set:
                result.add(value)
        return result

    def difference(self, other_set):
        result = SetRB()
        for value in self:
            if value not in other_set:
                result.add(value)
        return result

    def __str__(self):
        return "{" + ", ".join(map(str, self)) + "}"


def main():
    print("Создаем множество A:")
    A = SetRB()
    A.add(5)
    A.add(3)
    A.add(7)
    A.add(2)
    A.add(4)
    print("A:", A)

    print("\nПроверка наличия элементов:")
    print("3 в A?", 3 in A)  # True
    print("6 в A?", 6 in A)  # False

    print("\nСоздаем множество B:")
    B = SetRB()
    B.add(4)
    B.add(6)
    B.add(7)
    B.add(8)
    print("B:", B)

    print("\nОперации с множествами:")
    print("A ∪ B:", A.union(B))
    print("A ∩ B:", A.intersection(B))
    print("A \\ B:", A.difference(B))

    print("\nИтерация по множеству:")
    for num in A:
        print(num, end=" ")
    print()


if __name__ == '__main__':
    main()

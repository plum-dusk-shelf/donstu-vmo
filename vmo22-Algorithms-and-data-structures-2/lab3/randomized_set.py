import random
from randomized_bst import RandomizedBST


class SetR(RandomizedBST):
    def __init__(self):
        super().__init__()

    def add(self, value):
        self.root = self._insert(self.root, value)

    def discard(self, value):
        self.root = self._remove(self.root, value)

    def remove(self, value):
        if not self.contains(value):
            raise KeyError(value)
        self.discard(value)

    def contains(self, value):
        return self._search(self.root, value) is not None

    def __contains__(self, value):
        return self.contains(value)

    def __len__(self):
        return self._size(self.root)

    def __iter__(self):
        return iter(self._to_list(self.root))

    def __str__(self):
        return "{" + ", ".join(map(str, self)) + "}"

    def __bool__(self):
        return self.root is not None

    def clear(self):
        """Очищает множество"""
        self.root = None

    def is_empty(self):
        """Проверяет, пусто ли множество"""
        return self.root is None

    def update(self, iterable):
        for item in iterable:
            self.add(item)

    def __or__(self, other):
        result = SetR()
        result.update(self)
        result.update(other)
        return result

    def __and__(self, other):
        result = SetR()
        for item in self:
            if item in other:
                result.add(item)
        return result

    def __sub__(self, other):
        result = SetR()
        for item in self:
            if item not in other:
                result.add(item)
        return result

    def __xor__(self, other):
        return (self - other) | (other - self)

    def print_tree(self):
        if not self.root:
            print("Пустое множество")
            return

        def display_aux(node):
            if not node.right and not node.left:
                line = f"{node.key}({node.size})"
                return [line], len(line), 1, len(line) // 2

            if not node.right:
                lines, n, p, x = display_aux(node.left)
                s = f"{node.key}({node.size})"
                u = len(s)
                first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
                second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
                shifted_lines = [line + u * ' ' for line in lines]
                return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

            if not node.left:
                lines, n, p, x = display_aux(node.right)
                s = f"{node.key}({node.size})"
                u = len(s)
                first_line = s + x * '_' + (n - x) * ' '
                second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
                shifted_lines = [u * ' ' + line for line in lines]
                return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

            left, n, p, x = display_aux(node.left)
            right, m, q, y = display_aux(node.right)
            s = f"{node.key}({node.size})"
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
            second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
            if p < q:
                left += [n * ' '] * (q - p)
            elif q < p:
                right += [m * ' '] * (p - q)
            zipped_lines = zip(left, right)
            lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
            return lines, n + m + u, max(p, q) + 2, n + u // 2

        lines, *_ = display_aux(self.root)
        for line in lines:
            print(line)


if __name__ == "__main__":
    s1 = SetR()
    s1.add(5)
    s1.add(3)
    s1.add(7)
    s1.add(2)
    s1.add(4)

    print("Множество s1:", s1)
    print("Содержит 3?", 3 in s1)
    print("Размер s1:", len(s1))

    print("\nДерево s1:")
    s1.print_tree()

    s1.remove(3)
    print("\nПосле удаления 3:", s1)

    s2 = SetR()
    s2.update([4, 5, 6, 7, 8])
    print("\nМножество s2:", s2)

    print("\nОбъединение s1 | s2:", s1 | s2)
    print("Пересечение s1 & s2:", s1 & s2)
    print("Разность s2 - s1:", s2 - s1)
    print("Симметрическая разность s1 ^ s2:", s1 ^ s2)
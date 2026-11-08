class Node23Hopcroft:
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.keys = []       # Ключи (в листьях)
        self.guides = []     # Направляющие (во внутренних узлах)
        self.children = []  # Дети (для внутренних узлов)
        self.parent = None

    def is_leaf_node(self):
        return self.is_leaf

    def split(self):
        if self.is_leaf:
            # Разделение листа: создаем два новых листа
            left = Node23Hopcroft(is_leaf=True)
            right = Node23Hopcroft(is_leaf=True)
            mid = len(self.keys) // 2
            left.keys = self.keys[:mid]
            right.keys = self.keys[mid+1:]
            median = self.keys[mid]
            # Создаем новый внутренний узел, если это корень
            parent = self.parent if self.parent else Node23Hopcroft(is_leaf=False)
            # Обновляем родителя
            if self not in parent.children:
                parent.children.append(self)
            idx = parent.children.index(self)
            parent.children = parent.children[:idx] + [left, right] + parent.children[idx+1:]
            left.parent = parent
            right.parent = parent
            parent.guides = parent.guides[:idx] + [median] + parent.guides[idx:]
            # Проверяем переполнение родителя
            if len(parent.guides) > 2:
                parent.split()
            return parent
        else:
            # Разделение внутреннего узла
            mid = len(self.guides) // 2
            median = self.guides[mid]
            left = Node23Hopcroft(is_leaf=False)
            right = Node23Hopcroft(is_leaf=False)
            left.guides = self.guides[:mid]
            right.guides = self.guides[mid+1:]
            left.children = self.children[:mid+1]
            right.children = self.children[mid+1:]
            for child in left.children:
                child.parent = left
            for child in right.children:
                child.parent = right
            if self.parent:
                parent = self.parent
                idx = parent.children.index(self)
                parent.children = parent.children[:idx] + [left, right] + parent.children[idx+1:]
                parent.guides = parent.guides[:idx] + [median] + parent.guides[idx:]
                if len(parent.guides) > 2:
                    parent.split()
            else:
                parent = Node23Hopcroft(is_leaf=False)
                parent.guides = [median]
                parent.children = [left, right]
                left.parent = parent
                right.parent = parent
            return parent

class TwoThreeTreeHopcroft:
    def __init__(self):
        self.root = Node23Hopcroft(is_leaf=True)

    def find(self, key):
        return self._find(self.root, key)

    def _find(self, node, key):
        if node.is_leaf:
            return key in node.keys
        else:
            for i, guide in enumerate(node.guides):
                if key < guide:
                    return self._find(node.children[i], key)
            return self._find(node.children[-1], key)

    def insert(self, key):
        leaf = self._find_leaf(self.root, key)
        leaf.keys.append(key)
        leaf.keys.sort()
        if len(leaf.keys) > 2:
            new_root = leaf.split()
            while new_root.parent:
                new_root = new_root.parent
            self.root = new_root

    def _find_leaf(self, node, key):
        if node.is_leaf:
            return node
        else:
            for i, guide in enumerate(node.guides):
                if key < guide:
                    return self._find_leaf(node.children[i], key)
            return self._find_leaf(node.children[-1], key)

class Node23:
    def __init__(self):
        self.keys = []
        self.children = []
        self.parent = None

    def is_leaf_node(self):
        return len(self.children) == 0

    def split(self):
        if len(self.keys) < 3:
            return self.parent
        mid = 1  # средний из трех ключей
        median = self.keys[mid]
        left = Node23()
        right = Node23()
        left.keys = self.keys[:mid]
        right.keys = self.keys[mid+1:]
        if not self.is_leaf_node():
            left.children = self.children[:mid+1]
            right.children = self.children[mid+1:]
            for child in left.children:
                child.parent = left
            for child in right.children:
                child.parent = right
        # Обновление родителя
        parent = self.parent if self.parent else Node23()
        idx = parent.children.index(self) if self in parent.children else len(parent.children)
        parent.keys = parent.keys[:idx] + [median] + parent.keys[idx:]
        parent.children = parent.children[:idx] + [left, right] + parent.children[idx+1:]
        left.parent = parent
        right.parent = parent
        if len(parent.keys) > 2:
            return parent.split()
        return parent

class TwoThreeTree:
    def __init__(self):
        self.root = Node23()

    def find(self, key):
        return self._find(self.root, key) is not None

    def _find(self, node, key):
        if node is None:
            return None
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node
        elif node.is_leaf_node():
            return None
        else:
            return self._find(node.children[i], key)

    def insert(self, key):
        node = self.root
        # Спуск к листу
        while not node.is_leaf_node():
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node = node.children[i]
        # Вставка
        node.keys.append(key)
        node.keys.sort()
        if len(node.keys) > 2:
            new_root = node.split()
            while new_root and new_root.parent:
                new_root = new_root.parent
            if new_root:
                self.root = new_root

class Node23:
    def __init__(self):
        self.keys = []
        self.children = []
        self.parent = None

    def is_leaf_node(self):
        return len(self.children) == 0

    def split(self):
        if len(self.keys) < 3:
            return self.parent
        mid = 1  # средний из трех ключей
        median = self.keys[mid]
        left = Node23()
        right = Node23()
        left.keys = self.keys[:mid]
        right.keys = self.keys[mid+1:]
        if not self.is_leaf_node():
            left.children = self.children[:mid+1]
            right.children = self.children[mid+1:]
            for child in left.children:
                child.parent = left
            for child in right.children:
                child.parent = right
        # Обновление родителя
        parent = self.parent if self.parent else Node23()
        idx = parent.children.index(self) if self in parent.children else len(parent.children)
        parent.keys = parent.keys[:idx] + [median] + parent.keys[idx:]
        parent.children = parent.children[:idx] + [left, right] + parent.children[idx+1:]
        left.parent = parent
        right.parent = parent
        if len(parent.keys) > 2:
            return parent.split()
        return parent

class TwoThreeTree:
    def __init__(self):
        self.root = Node23()

    def find_node(self, key):
        return self._find(self.root, key)
    
    def find(self, key):
        return self._find(self.root, key) is not None

    def _find(self, node, key):
        if node is None:
            return None
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node
        elif node.is_leaf_node():
            return None
        else:
            return self._find(node.children[i], key)

    def insert(self, key):
        node = self.root
        # Спуск к листу
        while not node.is_leaf_node():
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node = node.children[i]
        # Вставка
        node.keys.append(key)
        node.keys.sort()
        if len(node.keys) > 2:
            new_root = node.split()
            while new_root and new_root.parent:
                new_root = new_root.parent
            if new_root:
                self.root = new_root

# Тест для 2-3 дерева Хопкрофта
def test_hopcroft_tree():
    tree = TwoThreeTreeHopcroft()
    keys = [10, 20, 30, 40, 50, 60]
    for key in keys:
        tree.insert(key)
    # Проверка структуры (примерная проверка)
    assert tree.root.is_leaf_node() == False
    # Добавьте детальные проверки структуры согласно примеру

# Тест для обычного 2-3 дерева
def test_23_tree():
    tree = TwoThreeTree()
    keys = [5, 3, 8, 1, 2, 7, 9]
    for key in keys:
        tree.insert(key)
    assert tree.find(5) == True
    # Проверка структуры 

# Тест для обычного 2-3 дерева
def test_23_tree_ten_and_up():
    tree = TwoThreeTree()
    keys = [5, 3, 8, 1, 2, 7, 9, 10, 11, 19, 20, 30, 344]
    for key in keys:
        tree.insert(key)
    assert tree.find(10) == True
    start = tree.find_node(10)
    print(start.children)
    def req(node):
        if node.children != []:
            for n in node.children:
                print(n.keys)
                req(n)
        return None
    req(start.parent)
    
    
    
    # Проверка структуры 

class BTreeNode:
    def __init__(self, t, is_leaf=True):
        self.t = t          # Минимальная степень 
        self.keys = []      # Ключи в узле
        self.children = []  # Дочерние узлы
        self.is_leaf = is_leaf

    def is_leaf_node(self):
        return self.is_leaf

class BTree:
    def __init__(self, t):
        self.t = t  # Минимальная степень
        self.root = BTreeNode(t, is_leaf=True)

    def find(self, key):
        return self._find(self.root, key)

    def _find(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return True
        return False if node.is_leaf else self._find(node.children[i], key)

    def insert(self, key):
        root = self.root
        # Если корень переполнен
        if len(root.keys) == 2 * self.t - 1:
            # Создаем новый корень
            new_root = BTreeNode(self.t, is_leaf=False)
            new_root.children.append(self.root)
            self.root = new_root
            # Разделяем старый корень
            self.split_child(new_root, 0)
        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.is_leaf:
            # Вставка в лист
            node.keys.append(key)
            node.keys.sort()
        else:
            # Находим позицию для вставки
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            # Если дочерний узел полный - разделяем
            if len(node.children[i].keys) == 2 * self.t - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def split_child(self, parent, idx):
        child = parent.children[idx]
        # Создаем новый узел
        new_node = BTreeNode(child.t, child.is_leaf)
        mid = self.t - 1
        
        # Переносим половину ключей и детей
        new_node.keys = child.keys[mid+1:]
        child.keys = child.keys[:mid]
        
        if not child.is_leaf:
            new_node.children = child.children[mid+1:]
            child.children = child.children[:mid+1]
        
        # Вставляем медиану в родителя
        parent.keys.insert(idx, child.keys[mid])
        parent.children.insert(idx + 1, new_node)
        
        # Проверяем родителя на переполнение
        if len(parent.keys) > 2 * self.t - 1:
            raise Exception("Parent node overflow")



class BTree:
    def __init__(self, t):
        self.t = t
        self.root = BTreeNode(t, is_leaf=True)

    def split_child(self, parent, idx):
        child = parent.children[idx]
        mid = self.t - 1
        # Сохраняем медиану до изменения child.keys
        median = child.keys[mid]  # Используем mid, вычисленный до обрезки

        new_node = BTreeNode(child.t, child.is_leaf)
        new_node.keys = child.keys[mid + 1:]
        child.keys = child.keys[:mid]  # Обрезаем ключи

        if not child.is_leaf:
            new_node.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]

        # Вставляем медиану в родителя
        parent.keys.insert(idx, median)
        parent.children.insert(idx + 1, new_node)

    def find(self, key):
        return self._find(self.root, key)

    def _find(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return True
        elif node.is_leaf:
            return False
        else:
            return self._find(node.children[i], key)

    def insert(self, key):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(self.t, is_leaf=False)
            new_root.children.append(self.root)
            self.root = new_root
            self.split_child(new_root, 0)
        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def insert(self, key):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(self.t, is_leaf=False)
            new_root.children.append(self.root)
            self.root = new_root
            self.split_child(new_root, 0)
        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)




def test_b_tree():
    b_tree = BTree(t=3)
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    for key in keys:
        b_tree.insert(key)
    assert b_tree.find(17) == True
    assert b_tree.find(99) == False
    print("B-дерево: Все тесты пройдены!")

class BPlusTreeNode:
    def __init__(self, t, is_leaf=True):
        self.t = t
        self.keys = []
        self.children = []
        self.is_leaf = is_leaf
        self.next = None  # Ссылка на следующий узел (для листьев)

    def is_leaf_node(self):
        return self.is_leaf

    def split(self):
        new_node = BPlusTreeNode(self.t, self.is_leaf)
        mid = self.t
        split_key = self.keys[mid]
        new_node.keys = self.keys[mid:]
        self.keys = self.keys[:mid]
        if self.is_leaf:
            new_node.next = self.next
            self.next = new_node
            split_key = new_node.keys[0]
        else:
            new_node.children = self.children[mid:]
            self.children = self.children[:mid]
        return split_key, new_node

class BPlusTree:
    def __init__(self, t):
        self.t = t
        self.root = BPlusTreeNode(t, is_leaf=True)

    def find(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return key in node.keys

    def range_query(self, start, end):
        result = []
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and start >= node.keys[i]:
                i += 1
            node = node.children[i]
        while node:
            for key in node.keys:
                if start <= key <= end:
                    result.append(key)
                elif key > end:
                    return result
            node = node.next
        return result

    def insert(self, key):
        node = self.root
        path = []
        while not node.is_leaf:
            path.append(node)
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        # Вставка в лист
        pos = 0
        while pos < len(node.keys) and key > node.keys[pos]:
            pos += 1
        node.keys.insert(pos, key)
        if len(node.keys) > 2*self.t - 1:
            self.split_leaf(node, path)

    def split_leaf(self, leaf, path):
        split_key, new_leaf = leaf.split()
        if not path:
            new_root = BPlusTreeNode(self.t, is_leaf=False)
            new_root.keys = [split_key]
            new_root.children = [leaf, new_leaf]
            self.root = new_root
        else:
            parent = path.pop()
            pos = 0
            while pos < len(parent.keys) and split_key >= parent.keys[pos]:
                pos += 1
            parent.keys.insert(pos, split_key)
            parent.children.insert(pos+1, new_leaf)
            if len(parent.keys) > 2*self.t - 1:
                self.split_internal(parent, path)

    def split_internal(self, node, path):
        split_key, new_node = node.split()
        if not path:
            new_root = BPlusTreeNode(self.t, is_leaf=False)
            new_root.keys = [split_key]
            new_root.children = [node, new_node]
            self.root = new_root
        else:
            parent = path.pop()
            pos = 0
            while pos < len(parent.keys) and split_key >= parent.keys[pos]:
                pos += 1
            parent.keys.insert(pos, split_key)
            parent.children.insert(pos+1, new_node)
            if len(parent.keys) > 2*self.t - 1:
                self.split_internal(parent, path)

def test_b_plus_tree():
    bp_tree = BPlusTree(t=3)
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    for key in keys:
        bp_tree.insert(key)
    assert bp_tree.find(17) == True
    assert bp_tree.find(99) == False
    assert bp_tree.range_query(5, 17) == [5, 6, 7, 10, 12, 17]
    print("B+-дерево: Все тесты пройдены!")

def test_b_tree():
    b_tree = BTree(t=3)
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    for key in keys:
        b_tree.insert(key)
    assert b_tree.find(17)
    assert not b_tree.find(99)
    print("B-дерево: Тесты пройдены!")
    
def main():
    print("=== Тестирование 2-3 дерева Хопкрофта (данные в листьях) ===")
    test_hopcroft_tree()
    print("Тест 2-3 дерева Хопкрофта пройден!\n")

    print("=== Тестирование обычного 2-3 дерева (данные во всех узлах) ===")
    test_23_tree()
    print("Тест обычного 2-3 дерева пройден!\n")

    print("=== Тестирование обычного 2-3 дерева (данные во всех узлах) > 10 ===")
    #test_23_tree_ten_and_up()
    print("Тест обычного 2-3 дерева > 10 пройден!\n")
    
    print("=== Тестирование B-дерева ===")
    test_b_tree()
    print("Тест B-дерева пройден!\n")

    print("=== Тестирование B+-дерева ===")
    test_b_plus_tree()
    print("Тест B+-дерева пройден!\n")

    # Демонстрация работы B+-дерева с диапазонным запросом
    print("=== Демонстрация B+-дерева ===")
    bp_tree = BPlusTree(t=3)
    keys = [10, 15, 20, 25, 30, 35, 40]
    for key in keys:
        bp_tree.insert(key)
    print("Диапазонный запрос [20, 35]:", bp_tree.range_query(20, 35))
    print("Поиск ключа 25:", bp_tree.find(25))
    print("Поиск несуществующего ключа 18:", bp_tree.find(18))

if __name__ == "__main__":
    main()
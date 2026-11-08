# Реализация 2-3 дерева с хранением данных во всех узлах

class Node:
    def __init__(self):
        self.keys = []  # Ключи в узле (1 или 2 ключа)
        self.children = []  # Дети узла (0, 2 или 3 ребенка)
        self.parent = None  # Родительский узел
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def is_full(self):
        return len(self.keys) == 2
    
    def insert_key(self, key):
        """Вставка ключа в узел с сохранением порядка"""
        if not self.keys:
            self.keys.append(key)
        else:
            if key < self.keys[0]:
                self.keys.insert(0, key)
            elif len(self.keys) == 1 or key < self.keys[1]:
                self.keys.insert(1, key)
            else:
                self.keys.append(key)
    
    def insert_child(self, child, index):
        """Вставка ребенка в узел по указанному индексу"""
        self.children.insert(index, child)
        child.parent = self
    
    def remove_child(self, child):
        """Удаление ребенка из узла"""
        self.children.remove(child)
        child.parent = None


class TwoThreeTree:
    def __init__(self):
        self.root = None
    
    def is_leaf(self, node):
        """Проверка, является ли узел листом"""
        return node.is_leaf()
    
    def search(self, key):
        """Поиск узла с заданным ключом"""
        return self._search(self.root, key)
    
    def _search(self, node, key):
        """Рекурсивный поиск ключа в дереве"""
        if not node:
            return None
        
        # Проверяем ключи в текущем узле
        if key in node.keys:
            return node
        
        # Если узел - лист, ключ не найден
        if node.is_leaf():
            return None
        
        # Определяем, в какого ребенка идти
        if key < node.keys[0]:
            return self._search(node.children[0], key)
        elif len(node.keys) == 1 or key < node.keys[1]:
            return self._search(node.children[0], key)
        else:
            return self._search(node.children[2], key)
    
    def insert(self, key):
        """Вставка ключа в дерево"""
        if not self.root:
            self.root = Node()
            self.root.insert_key(key)
            return
        
        # Ищем лист для вставки
        leaf = self._find_leaf(self.root, key)
        
        # Вставляем ключ в лист
        leaf.insert_key(key)
        
        # Если лист переполнен, выполняем разделение
        if leaf.is_full():
            self._split(leaf)
    
    def _find_leaf(self, node, key):
        """Поиск листа для вставки ключа"""
        if node.is_leaf():
            return node
        
        if key < node.keys[0]:
            return self._find_leaf(node.children[0], key)
        elif len(node.keys) == 1 or key < node.keys[1]:
            return self._find_leaf(node.children[0], key)
        else:
            return self._find_leaf(node.children[2], key)
    
    def _split(self, node):
        """Разделение переполненного узла"""
        if not node.is_full():
            return
        
        # Создаем новый узел
        new_node = Node()
        
        # Переносим средний ключ в родителя или создаем новый корень
        middle_key = node.keys[1]
        
        if not node.parent:
            # Разделяем корень
            new_root = Node()
            new_root.insert_key(middle_key)
            
            left_child = Node()
            left_child.insert_key(node.keys[0])
            
            right_child = Node()
            right_child.insert_key(node.keys[2] if len(node.keys) > 2 else node.keys[1])
            
            # Переносим детей, если они есть
            if not node.is_leaf():
                left_child.children = node.children[:2]
                right_child.children = node.children[2:]
                for child in left_child.children + right_child.children:
                    child.parent = left_child if child in left_child.children else right_child
            
            new_root.insert_child(left_child, 0)
            new_root.insert_child(right_child, 1)
            
            left_child.parent = new_root
            right_child.parent = new_root
            
            self.root = new_root
        else:
            parent = node.parent
            parent.insert_key(middle_key)
            
            # Создаем новый узел с правыми ключами
            new_node.insert_key(node.keys[2] if len(node.keys) > 2 else node.keys[1])
            
            # Определяем позицию для вставки нового узла
            index = parent.keys.index(middle_key)
            
            # Переносим детей, если они есть
            if not node.is_leaf():
                new_node.children = node.children[2:]
                node.children = node.children[:2]
                for child in new_node.children:
                    child.parent = new_node
            
            # Вставляем новый узел в родителя
            parent.insert_child(new_node, index + 1)
            
            # Проверяем, не переполнился ли родитель
            if parent.is_full():
                self._split(parent)
    
    def print_tree(self):
        """Вывод дерева в удобочитаемом виде"""
        if not self.root:
            print("Tree is empty")
            return
        
        levels = {}
        self._collect_nodes(self.root, 0, levels)
        
        for level in sorted(levels.keys()):
            nodes = levels[level]
            line = ""
            for node in nodes:
                line += str(node.keys) + " "
            print(f"Level {level}: {line}")
    
    def _collect_nodes(self, node, level, levels):
        """Сбор узлов по уровням для вывода"""
        if level not in levels:
            levels[level] = []
        levels[level].append(node)
        
        for child in node.children:
            self._collect_nodes(child, level + 1, levels)


# Пример использования
if __name__ == "__main__":
    tree = TwoThreeTree()
    
    # Вставка ключей
    keys = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    for key in keys:
        tree.insert(key)
        print(f"After inserting {key}:")
        tree.print_tree()
        print()
    
    # Поиск ключей
    search_keys = [30, 45, 60, 100, 110]
    for key in search_keys:
        node = tree.search(key)
        if node:
            print(f"Key {key} found in node with keys: {node.keys}")
        else:
            print(f"Key {key} not found in the tree")
    
    # Проверка, является ли узел листом
    node = tree.search(30)
    if node:
        print(f"Node with key 30 is leaf: {tree.is_leaf(node)}")
    
    node = tree.search(100)
    if node:
        print(f"Node with key 100 is leaf: {tree.is_leaf(node)}")

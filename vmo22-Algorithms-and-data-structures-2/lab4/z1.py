class Node:
    def __init__(self):
        self.keys = []  # Список ключей в узле (1 или 2 ключа)
        self.children = []  # Список дочерних узлов (0, 2 или 3 узла)
        self.parent = None  # Родительский узел
    
    def is_leaf(self):
        """Проверяет, является ли узел листом (не имеет дочерних узлов)"""
        return len(self.children) == 0
    
    def is_full(self):
        """Проверяет, содержит ли узел максимальное количество ключей (2)"""
        return len(self.keys) == 2
    
    def insert_key(self, key):
        """Вставляет ключ в узел в отсортированном порядке"""
        if not self.keys:
            self.keys.append(key)
        else:
            if key < self.keys[0]:
                self.keys.insert(0, key)
            elif len(self.keys) == 1 or key < self.keys[1]:
                self.keys.insert(1, key)
            else:
                self.keys.append(key)
    
    def insert_child(self, child):
        """Вставляет дочерний узел в правильном порядке"""
        child.parent = self
        if not self.children:
            self.children.append(child)
        else:
            if child.keys[0] < self.children[0].keys[0]:
                self.children.insert(0, child)
            elif len(self.children) == 1 or child.keys[0] < self.children[1].keys[0]:
                self.children.insert(1, child)
            else:
                self.children.append(child)

class TwoThreeTree:
    def __init__(self):
        self.root = None
    
    def search(self, key, node=None):
        """Поиск узла, содержащего заданный ключ"""
        if node is None:
            node = self.root
            if node is None:
                return None
        
        # Проверяем, есть ли ключ в текущем узле
        if key in node.keys:
            return node
        
        # Если узел - лист, ключ не найден
        if node.is_leaf():
            return None
        
        # Определяем, в какого ребенка идти
        if key < node.keys[0]:
            return self.search(key, node.children[0])
        elif len(node.keys) == 1 or key < node.keys[1]:
            return self.search(key, node.children[1])
        else:
            return self.search(key, node.children[2])
    
    def insert(self, key):
        """Вставка нового ключа в дерево"""
        if self.root is None:
            self.root = Node()
            self.root.insert_key(key)
            return
        
        # Находим лист для вставки
        leaf = self._find_leaf(key)
        
        # Вставляем ключ в лист
        leaf.insert_key(key)
        
        # Если лист переполнен, выполняем разделение
        if leaf.is_full():
            self._split(leaf)
    
    def _find_leaf(self, key, node=None):
        """Находит лист, в который нужно вставить ключ"""
        if node is None:
            node = self.root
        
        if node.is_leaf():
            return node
        
        if key < node.keys[0]:
            return self._find_leaf(key, node.children[0])
        elif len(node.keys) == 1 or key < node.keys[1]:
            return self._find_leaf(key, node.children[0])
        else:
            return self._find_leaf(key, node.children[2])
    
    def _split(self, node):
        """Разделяет переполненный узел"""
        if not node.is_full():
            return
        
        # Создаем два новых узла
        left = Node()
        right = Node()
        
        # Распределяем ключи и детей
        left.insert_key(node.keys[0])
        right.insert_key(node.keys[1])
        
        if not node.is_leaf():
            left.children = node.children[:2]
            right.children = node.children[2:]
            for child in left.children:
                child.parent = left
            for child in right.children:
                child.parent = right
        
        # Если разделяем корень
        if node.parent is None:
            new_root = Node()
            new_root.insert_key(node.keys[1])
            new_root.insert_child(left)
            new_root.insert_child(right)
            self.root = new_root
        else:
            parent = node.parent
            # Удаляем старый узел из родителя
            parent.children.remove(node)
            # Добавляем новые узлы
            parent.insert_child(left)
            parent.insert_child(right)
            # Вставляем средний ключ в родителя
            parent.insert_key(node.keys[1])
            
            # Если родитель переполнен, рекурсивно разделяем его
            if parent.is_full():
                self._split(parent)
    
    def __str__(self):
        """Визуализация дерева (для отладки)"""
        if self.root is None:
            return "Empty tree"
        
        levels = []
        current_level = [self.root]
        
        while current_level:
            level_str = ""
            next_level = []
            
            for node in current_level:
                level_str += str(node.keys) + " "
                next_level.extend(node.children)
            
            levels.append(level_str)
            current_level = next_level
        
        return "\n".join(levels)

# Пример использования
if __name__ == "__main__":
    tree = TwoThreeTree()
    keys = [5, 3, 7, 1, 4, 6, 8, 2, 9]
    
    for key in keys:
        tree.insert(key)
        print(f"After inserting {key}:")
        print(tree)
        print("-----")
    
    # Поиск ключей
    print("Search results:")
    for key in range(10):
        node = tree.search(key)
        if node:
            print(f"Key {key} found in node with keys: {node.keys}")
        else:
            print(f"Key {key} not found")

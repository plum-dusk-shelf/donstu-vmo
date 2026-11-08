class Node:
    def __init__(self):
        self.keys = []
        self.children = []
        self.is_leaf = True
        self.parent = None

    def is_full(self):
        return len(self.keys) == 3

    def is_2node(self):
        return len(self.keys) == 1

    def is_3node(self):
        return len(self.keys) == 2

    def insert_key(self, key):
        self.keys.append(key)
        self.keys.sort()

    def insert_child(self, child):
        self.children.append(child)
        self.children.sort(key=lambda x: x.keys[0])
        child.parent = self


class TwoThreeTree:
    def __init__(self):
        self.root = Node()

    def search(self, key, node=None):
        if node is None:
            node = self.root

        if key in node.keys:
            return node

        if node.is_leaf:
            return None

        if len(node.keys) == 1:
            if key < node.keys[0]:
                return self.search(key, node.children[0])
            else:
                return self.search(key, node.children[1])
        else:
            if key < node.keys[0]:
                return self.search(key, node.children[0])
            elif key < node.keys[1]:
                return self.search(key, node.children[1])
            else:
                return self.search(key, node.children[2])

    def insert(self, key):
        node = self._find_leaf_to_insert(key)
        self._insert_into_leaf(node, key)

    def _find_leaf_to_insert(self, key, node=None):
        if node is None:
            node = self.root

        if node.is_leaf:
            return node

        if len(node.keys) == 1:
            if key < node.keys[0]:
                return self._find_leaf_to_insert(key, node.children[0])
            else:
                return self._find_leaf_to_insert(key, node.children[1])
        else:
            if key < node.keys[0]:
                return self._find_leaf_to_insert(key, node.children[0])
            elif key < node.keys[1]:
                return self._find_leaf_to_insert(key, node.children[1])
            else:
                return self._find_leaf_to_insert(key, node.children[2])

    def _insert_into_leaf(self, node, key):
        node.insert_key(key)

        if node.is_full():
            self._split_node(node)

    def _split_node(self, node):
        if node.parent is None:
            self._split_root()
        else:
            self._split_internal_node(node)

    def _split_root(self):
        old_root = self.root
        self.root = Node()
        self.root.is_leaf = False

        left = Node()
        left.insert_key(old_root.keys[0])
        right = Node()
        right.insert_key(old_root.keys[2])

        if not old_root.is_leaf:
            left.children = old_root.children[:2]
            right.children = old_root.children[2:]
            for child in left.children + right.children:
                child.parent = left if child in left.children else right
            left.is_leaf = False
            right.is_leaf = False

        self.root.insert_key(old_root.keys[1])
        self.root.insert_child(left)
        self.root.insert_child(right)

    def _split_internal_node(self, node):
        parent = node.parent
        left = Node()
        left.insert_key(node.keys[0])
        right = Node()
        right.insert_key(node.keys[2])

        if not node.is_leaf:
            left.children = node.children[:2]
            right.children = node.children[2:]
            for child in left.children + right.children:
                child.parent = left if child in left.children else right
            left.is_leaf = False
            right.is_leaf = False

        parent.insert_key(node.keys[1])
        parent.children.remove(node)
        parent.insert_child(left)
        parent.insert_child(right)

        if parent.is_full():
            self._split_node(parent)

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root

        print(f"Level {level}: {node.keys}")
        if not node.is_leaf:
            for child in node.children:
                self.print_tree(child, level + 1)


def main():
    tree = TwoThreeTree()
    keys = list(range(10))

    for key in keys:
        tree.insert(key)

    print("2-3 Tree structure:")
    tree.print_tree()

    print("\nSearch results:")
    for key in range(10):
        result = tree.search(key)
        if result:
            print(f"Ключ {key} найден в {result.keys}")
        else:
            print(f"Key {key} not found")


if __name__ == '__main__':
    main()
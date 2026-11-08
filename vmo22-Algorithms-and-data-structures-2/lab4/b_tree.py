class BTreeNode:
    def __init__(self, t):
        self.t = t
        self.keys = 2*t

class BTree:
    def __init__(self, t):
        self.root = None
        self.t = t


def main():
    btree = BTree(4)


if __name__ == '__main__':
    main()
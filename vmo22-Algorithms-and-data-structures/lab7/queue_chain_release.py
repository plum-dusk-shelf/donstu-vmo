class QueueRelease:
    def __init__(self):
        self.head = self.tail = -1

    def add_element(self, value):
        if self.head == self.tail == -1:
            self.head = self.tail = QueueChainLink(value, None)
            return

        q = QueueChainLink(value, self.tail)
        self.tail.following = q
        self.tail = q

    def get_element(self):
        q = self.head
        self.head = q.following
        return q.value

    def get_all(self):
        q = []
        while self.head:
            q.append(self.get_element())

        return q

    def is_empty(self):
        if not self.head:
            return True

    def get_least_then_next(self):
        q = self.head
        while q.following:
            if q.value - q.next.value < 2:
                return q.value


class QueueChainLink():
    def __init__(self, value, previous, following=None):
        self.value = value
        self.previous = previous
        self.following = following


def main():
    queue1 = QueueRelease()
    for i in range(15):
        queue1.add_element(i)

    print(queue1.get_all())
    print(queue1.is_empty())


if __name__ == "__main__":
    main()

class QueueRelease:
    def __init__(self):
        self.__memory = [0] * 10
        self.size = len(self.__memory)
        self.count = 0
        self.head = -1
        self.tail = -1

    def add_element(self, value):
        if self.count == self.size:
            raise Exception("QueueRelease is full")
        elif self.head == self.tail == -1:
            self.head = 0
        elif self.tail == self.size - 1:
            self.tail = -1

        self.tail += 1
        self.count += 1
        self.__memory[self.tail] = value

    def get_element(self):
        if self.count == 0:
            raise Exception("QueueRelease is empty")
        elif not self.is_empty():
            element = self.__memory[self.head]
            self.head += 1
            self.count -= 1
            return element

    def get_all(self):
        while not self.is_empty():
            print(self.get_element())

    def is_empty(self):
        if self.head == self.tail + 1:
            return True

    def get_memory(self):
        print(f'h{self.head}\tt{self.tail}\n{self.__memory}')


def main():
    queue1 = QueueRelease()
    for i in range(1, 11):
        queue1.add_element(i)
        queue1.get_memory()
    for i in range(5):
        queue1.get_element()
        queue1.get_memory()

    for i in range(20, 25):
        queue1.add_element(i)
        queue1.get_memory()


if __name__ == "__main__":
    main()

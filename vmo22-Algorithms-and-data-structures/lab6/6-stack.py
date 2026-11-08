class StackChain:
    def __init__(self):
        self.top = None

    def add_link(self, value):
        if self.top is None:
            self.top = StackChainLink(value, None)
        else:
            self.top = StackChainLink(value, self.top)

    def get_element(self):
        element = self.top
        self.top = self.top.previous_link
        return element

    def get_all(self):
        q = self.top
        while q.previous_link:
            q = self.get_element()
            print(q.value)

    def is_empty(self):
        if self.top.previous_link is None:
            return True
        else:
            return False


class StackChainLink:
    def __init__(self, value, previous_link):
        self.value = value
        self.previous_link = previous_link


class Stack:
    def __init__(self):
        self.__memory = [0] * 10
        self.top = -1

    def add_element(self, value):
        if self.top == -1:
            self.__memory[0] = value
            self.top = 0
        elif self.top == len(self.__memory) - 1:
            raise Exception("Stack overflow")
        else:
            self.top += 1
            self.__memory[self.top] = value

    def get_element(self):
        q = self.__memory[self.top]
        self.top -= 1
        return q

    def get_all(self):
        all_elements = []
        while self.top != -1:
            all_elements.append(self.get_element())

        return all_elements

    def is_empty(self):
        if self.top == -1:
            return True
        else:
            return False

    def get_biggest_triple(self):
        maxim = -10 ** 10
        for i in self.get_all():
            if i > 99 and 1000 > i:
                maxim = max(i, maxim)
        return maxim


stack1 = StackChain()
stack1.add_link(23)
stack1.add_link(50)
stack1.add_link(100)
stack1.get_all()

print('\n\n')

stack2 = Stack()
stack2.add_element(10)
stack2.add_element(310)
stack2.add_element(700)
print(stack2.get_biggest_triple())

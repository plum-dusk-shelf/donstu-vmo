import random


class ListWithPointers:
    def __init__(self):
        self.__memory = [0] * 10
        self.__pointers = list(range(len(self.__memory)))
        random.shuffle(self.__pointers)
        self.entry = None  # точка входа по умолчанию
        self.empties = self.__pointers.index(0)

    def add_element(self, value, index=None):
        if not index:
            index = self.entry



def main():
    list1 = ListWithPointers()
    print(list1.add_element(1))


if __name__ == "__main__":
    main()

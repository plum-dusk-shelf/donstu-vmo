from math import sqrt


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def draw(self):
        print(self.x, self.y)

    def go(self):
        pass


class Line:
    def __init__(self, p1: Point, p2: Point):  # p1 и p2 — объекты класса Point
        self.p1 = p1
        self.p2 = p2

    def draw(self):
        print('Линия')
        self.p1.draw()
        self.p2.draw()


class Section(Line):
    def __init__(self, p1, p2, name):
        super().__init__(p1, p2)
        self.name = name

    def len(self):
        return sqrt((self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2)

    def draw(self):
        print('Отрезок')
        self.p1.draw()
        self.p2.draw()
        print(self.len())


A = Point(1, 3)
B = Point(4, 2)

ab = Line(A, B)
ab.draw()

AB = Section(A, B, 'AB')
AB.draw()

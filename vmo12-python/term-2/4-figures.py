import math
from abc import abstractmethod


class Figure:
    def __init__(self, sides:list):
        self.sides = sides

    @abstractmethod
    def square_space(self):
        pass

    @abstractmethod
    def perimetr(self):
        pass

    def perimetr1(self):
        pass

    def angles_count(self):
        if self.sides:
            return len(self.sides) + 1
        return 'Эта фигура не имеет углов'

    def print_properties(self):
        print(f'Площадь {self.square_space()}, а периметр {self.perimetr()}')


class Rectangle(Figure):
    def __init__(self, sides:list):
        super().__init__(sides)
        self.sides = sides

    def perimetr(self):
        return sum(self.sides) * 2

    def square_space(self):
        return self.sides[0] * self.sides[1]


class Circle(Figure):
    def __init__(self, radius):
        super().__init__([radius])
        self.radius = radius

    def square_space(self):
        return self.radius ** 2 * 3.14

    def perimetr(self):
        return self.radius * 2 * 3.14

    def angles_count(self):
        return 'Круг не имеет углов'


class Trapezium(Figure):
    def __init__(self, sides):
        super().__init__(sides)
        height, width_a, width_b = sides
        self.height = height
        self.width_a = min(width_a, width_b)
        self.width_b = max(width_a, width_b)

    def square_space(self):
        return (self.width_a + self.width_b) / 2 * self.height

    def perimetr(self):
        side_one = math.sqrt((self.width_b - self.width_a) ** 2 + self.height ** 2)
        return side_one + self.width_a + self.width_b + self.height


class Picture:
    def __init__(self):
        self.list_figures = []

    def add_figure(self, figure):
        self.list_figures.append(figure)

    def show_figures(self):
        for fig in self.list_figures:
            fig.print_properties()


picture1 = Picture()

circle1 = Circle(10)
print(circle1.square_space(), circle1.perimetr())
picture1.add_figure(circle1)

trapezium1 = Trapezium([10, 8, 12])
print(trapezium1.square_space(), trapezium1.perimetr())
picture1.add_figure(trapezium1)

rectangle1 = Rectangle([2, 3])
print(rectangle1.square_space(), rectangle1.perimetr())
picture1.add_figure(rectangle1)

picture1.show_figures()

import random
import string


def readFile(filename):
    with open(filename, 'r', encoding='cp1251') as f:
        lines = f.readlines()
    return lines


def fillData(file_to_fill):
    characters = string.ascii_lowercase + string.digits
    list = []
    lines_number = random.randint(1, 10)
    with open(file_to_fill, 'w') as f:
        for i in range(lines_number):
            line = ''.join(random.choices(characters, k=random.randint(1, 10))) + '\n'
            list.append(line)
            f.write(line)
        f.close()


def saveLongest(line):
    with open('1-2-longest-line.txt', 'w', encoding='utf-8') as f:
        f.write(line)


def addLongest(line):
    with open('1-2-longest-line.txt', 'a', encoding='utf-8') as f:
        f.write(line)


if __name__ == "__main__":
    fillData('1-2-lines.txt')

    maximum = -(10 ** 10)

    lines = readFile('1-2-lines.txt')

    for line in lines:
        line.replace('\n', '')

        if len(line) > maximum:
            saveLongest(line)
            maximum = len(line)
        elif len(line) == maximum:
            addLongest(line)

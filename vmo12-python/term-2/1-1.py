import json

letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
file_name = input('Введите имя файла\n')


# '1-1—yevgeniy-onegin.txt'

def openFile(file_name):
    with open(file_name, 'r', encoding='cp1251') as file:
        text = file.read()
        return text


def writeResult():
    with open('1-1—unique_letters.txt', 'w', encoding='utf-8') as file:
        # json.dump(unique_letters, file)
        for letter in unique_letters:
            file.write(f'{letter} — {unique_letters[letter]}\n')
            # pass


try:
    text = openFile(file_name)
except:
    print('Файл не существует')

unique_letters = {}
for letter in letters:
    unique_letters[letter] = 0

for letter in text:
    if letter in letters:
        unique_letters[letter] += 1

writeResult()
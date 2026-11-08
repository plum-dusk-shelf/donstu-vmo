def main():
    data = {
        'яблоко': 1,
        'банан': 2,
        'вишня': 3,
        'шоколад': 4
    }

    def search(dictionary, key):
        if key in dictionary:
            return dictionary[key]
        else:
            return None

    inpt = input()
    result = search(data, inpt)

    if result is not None:
        print(f"{inpt} -> {result}")
    else:
        print(f"{inpt} не найден")


if __name__ == "__main__":
    main()

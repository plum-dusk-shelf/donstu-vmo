import random
def main():
    with open('2_files_2.txt') as f:
        place, char = input('place, char: ').split()
        try:
            place = int(place)
        except Exception as e:
            print('Error ocured')
        line = f.read().split('\n')[:-1]
        if not line:
            line = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for x in range(100)])

    with open('2_files_2.txt', 'w') as f:
        try:
            to_write = line[:place+1] + char + line[place:]
        except Exception:
            print('Error ocured')
        f.write(to_write)
        print(to_write)

if __name__ == '__main__':
    main()

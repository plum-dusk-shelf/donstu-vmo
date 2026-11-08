import random
def main():
    with open('2_files_4.txt') as f:
        try:
            query = input('Search: ')
            lines = f.read().split('\n')
            for line_num in range(len(lines)):
                pos_in_line = lines[line_num].find(query)
                if pos_in_line != -1:
                    print(f'{line_num} {pos_in_line}')
        except:
            print(f'Error ocured: {Exception}')
            exit()


if __name__ == '__main__':
    main()

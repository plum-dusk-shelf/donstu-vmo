import random
def main():
    with open('2_files_3.txt') as f:
        try:
            num = int(input('line number: '))
        except:
            print('Error ocured')
            exit()
        
        lines = f.readlines()

        if num > len(lines):
            print('no such string in file')
        
        else:
            print(lines[num])

    with open('2_files_3.txt', 'w') as f:
        numbers = [str(random.choice('abc'))+'\n' for i in range(100)][:-1]
        f.writelines(numbers)

if __name__ == '__main__':
    main()

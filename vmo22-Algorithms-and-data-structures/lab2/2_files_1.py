import random
def main():
    
    with open('2_files_1.txt') as f:
        numbers = f.read().split('\n')[:-1]
        print(numbers)
        negatives = len([x for  x in numbers if int(x)<0])
        print(negatives)

    with open('2_files_1.txt', 'w') as f:
        numbers = [str(random.choice([1, -1]))+'\n' for i in range(100)]
        f.writelines(numbers)

if __name__ == '__main__':
    main()

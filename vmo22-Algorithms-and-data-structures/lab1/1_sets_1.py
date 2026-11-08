my_set = set()

while True:
    inpt = input()

    if inpt == 'new_set':
        my_set = input('new set elements:').split()

    elif inpt == 'print_set':
        print(f'{my_set} has {len(my_set)} elements')
    
    elif inpt == 'exit':
        exit()

    else:
        print('unknown command')


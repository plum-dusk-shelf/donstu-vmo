import random
def main():
    with open('2_files_4.txt') as f:
        try:
            unique_words = {}
            words = f.read().split()
            for w in words:
                w = w.lower()
                if w not in unique_words.keys():
                    unique_words[w] = 1
                else:
                    unique_words[w] += 1

            for key in unique_words.keys():
                if unique_words[key] > 1:
                    print(f'{key}: {unique_words[key]}')
                
        except:
            print(f'Error ocured: {Exception}')
            exit()


if __name__ == '__main__':
    main()

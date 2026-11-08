#include <iostream>

#include "lab1.cpp"
#include "lab2.h"
#include "lab3.h"
#include "lab4.h"
#include "lab5.h"
#include "lz4_parallel.h"
#include "compressor.h"

int main(int argc, char* argv[]) {
    int sizes[] = {100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 10000000};
    int threads[] = {2, 4};
            for (int threadd: threads) {
        for (int size : sizes) {
    for (int i = 0; i < 10; i++) {
                runCompressor(size,threadd);
                cout << endl;
            }
        }
    }
}
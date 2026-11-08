#include "lab1.h"
#include <cmath>
#include <iostream>
#include <iomanip>

using namespace lab1;
using namespace std;

void lab1::problem22(int M, int N, int J) {
    std::cout.setf(ios::right);
    int rows = M, cols = N;
    int matrix[rows][cols];
    int counter = 0;
    int sums[rows];
    for (int i = 0; i < rows; i++){
        for (int j = 0; j < cols; j++) {
            if (j == J){
            matrix[i][j] = 5*J;}
            else{matrix[i][j] = counter++;}
        }
    }

    for (int i = 0; i < rows; i++) {
        sums[i] = 0;
    }


    for (int i = 0; i < rows; i++){
        for (int j = 0; j < cols; j++) {
            std::cout << std::setw(5) << matrix[i][j];
        }
        std::cout << std::endl << std::endl;
    }
    cout << std::endl << std::endl;


    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            sums[i] = sums[i] + matrix[i][j];
        }
    }

    for (int i = 0; i < rows; i++) {
        cout << sums[i] << " ";
    }
}

void lab1::problem1() {
    float S, x;

    cin >> x;
    S = pow(x, 2)/2;
    cout << S << endl;
}

void lab1::problem21(int N, int K) {
    int array[N];
    int array_new[N+1];

  for (int i = 0; i < N; i++) {
        array[i] = i;
    }

    for (int i = 0; i < N+1; i++) {
        if (i != K & i < K) {
            array_new[i] = array[i];
        }
        else if (i != K && i > K) {
            array_new[i] = array[i-1];
        }
        else {
            array_new[i] = 0;
        }
    }

    array_new[K] = 0;

    for (int new_: array_new) {
        cout << new_ << endl;
    }
}

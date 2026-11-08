#include "lab3.h"

#include <functional>
#include <iostream>
#include <ostream>
#include <cmath>
using namespace std;

/*
float A[] = {1, 2, 3, 4, 6, 5, 7, 8, 9, -1, -2, -3, -4, -5, -6, -7, -8, -9, -1, -2};
float B[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -2, -3,-4,-5, -6};
float C[] = {1, 2, 3, 4, 5, 6, 7, 8, 9,-12};
cout << "Problem 1: " << lab3::problem1(A, B, C) << endl;
cout << "Problem 2: " << lab3::problem2(10)<< endl;
*/

float sum(float arr[], int len) {
    float res = 0;
    float counter = 0;

    for (int i = 0; i < len; i++) {
        if (arr[i]>= 0){res += arr[i];}
        counter++;
    }

    return res / counter;
}
float lab3::problem1(float A[20], float B[15], float C[10]) {
    return (sum(A, 20) + sum(B, 15) + sum(C, 10)) / 2;
}

float my_function(float X) {
    int n = 10;
    float res = 0;
    for (int i = 1; i <= n; i++) {
        res += pow(sin(X), 2)/pow(i,3);
    }
    return res;
}

float lab3::problem2(float X) {
    float f = my_function(X);
    return f;
}
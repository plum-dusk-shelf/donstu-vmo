#include "lab2.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>

using namespace lab2;
using namespace std;

void lab2::problem111() {
    int n = 10;
    auto *pA = new float[n];
    float *pAt = pA;
    float array[n] = {-10, 5, 1, 13, 43, -1, 100, -2, -100, 100};


    for (int i=0; i < n; i++, pAt++) {
        *pAt = array[i];
        // cin >> *pAt;
        // cout << i << ": " << *pAt << endl;
    }
    pAt = pA;


    float *biggest = pA;
    for (int i = 0; i < n; i++, pAt++) {
        if (fabs(*pAt) > *biggest) {biggest = pAt;}
    }
    pAt = pA;

    cout << "biggest = " << *biggest << endl;
}

// void lab2::sort_array(float &pA){
//     float *pTemp = &pA;
//     cout << pTemp << endl;
// }

void lab2::problem112() {
    int n = 10;
    float biggest = 0;
    vector<float> array = {-10, 5, 1, 13, 43, -1, 100, -2, -100, 100};
    for (float el: array) {
        if (el > biggest) {biggest = el;}
    }

    cout << "biggest = " << biggest << endl;
}

void lab2::problem121 () {
    int n = 10;
    float counter = 0, multiplication = 1, C = 40;
    auto *pA = new float[n];
    float *pAt = pA, *biggest = pA;
    float array[n] = {-10, 5, 1, 13, 43, -1, 100, -2, -100, 100};


    // Заполнение динамического массива элементами из статического
    for (int i=0; i < n; i++, pAt++) {
        *pAt = array[i];
        // cout << i << ": " << *pAt << endl;
    }
    pAt = pA;


    // Нахождение наибольшего элемента и подсчет элементов больших чем C
    // cout << *pA << endl;
    for (int i=0; i < n; i++, pAt++) {
        if (*pAt > C) {counter++;}
        if (fabs(*pAt) > *biggest) {biggest = pAt;}
    }
    pAt = pA;

    bool cutoff = false;
    for (int i=0; i < n; i++, pAt++) {
        if (*pAt == *biggest) {cutoff = true;}
        if (cutoff) {multiplication *= *pAt;}
    }
    pAt = pA;

    // sort_array(&pAt);

    cout << "C = " << counter << endl;
    cout << "B = " << *biggest << endl;
    cout << "Result = " << multiplication << endl;
}

void lab2::problem122() {
    vector<float> array = {-10, 5, 1, 13, 43, -1, 100, -2, -100, 100};
    float counter = 0, multiplication = 1, C = 40, biggest = 0;

    for (float el: array) {
        if (fabs(el) > biggest) {biggest = el;}
        if (el > C) {counter++;}
    }

    bool cutoff = false;
    for (float el: array) {
        if (el == biggest) {cutoff = true;}
        if (cutoff) {multiplication *= el;}
    }
    cout << "C = " << counter << endl;
    cout << "B = " << biggest << endl;
    cout << "Result = " << multiplication << endl;
}

void lab2::problem211() {
    char alphabet[] = "abcdefghijklmnopqrtuvwxyz";
    char inputed[] = "teX234:t2";
    int counter = 0, biggest_counter = 0;
    for (char el : inputed) {
        bool el_in_alph = 0;
        for (char symb: alphabet) {
            if (tolower(el) == symb) {
                el_in_alph = 1;
                counter = 0;
                continue;
            }
        }
        if (not el_in_alph) {counter++;}
        if (counter > biggest_counter) {biggest_counter = counter;}
    }

    cout << biggest_counter;
}

void lab2::problem212() {
    string alphabet = "abcdefghijklmnopqrtuvwxyz";
    string inputed = "teX234:t2";
    int counter = 0, biggest_counter = 0;
    for (char el : inputed) {
        bool el_in_alph = (alphabet.find(tolower(el)) != string::npos);
        if (el_in_alph) {counter=0;}
        else {counter++;}
        if (counter > biggest_counter) {biggest_counter = counter;}
    }

    cout << biggest_counter;
}
void lab2::problem221() {
    char str[] = "word letter opptioon";
    int counter = 0;

    int inner_counter = 0;
    char last;
    for (char el: str) {
        if (el == ' ') {
            if (inner_counter) {counter++;}
            inner_counter = 0;
        }
        else if (el == last) {inner_counter++;}
        last = el;
    }

    cout << inner_counter;
}

void lab2::problem222() {
    string str = "word letter opptioon";
    int counter = 0;

    int inner_counter = 0;
    for (int i=0; i<str.length(); i++) {
        if (str[i] == str[i+1]) {inner_counter++;}
        if (str[i] == ' ' or i == str.length()-1) {
            cout << i << endl;
            if (inner_counter) {counter++;}
            inner_counter = 0;
        }
    }

    cout << endl << counter;
}
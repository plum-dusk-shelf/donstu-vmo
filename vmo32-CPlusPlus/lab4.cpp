#include <string>
#include "lab4.h"
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <string>
using namespace std;
using namespace lab4;

void lab4::test() {
    fstream fin (
        R"(C:\Users\simafrus\CPP\Labs\cant_stop.txt)", ios::in);
    if (!fin.is_open()) {
        cerr << "File not opened :(" << endl;
        exit(1);
    }

    // Вычисление длины файла
    int length;
    fin.seekg(0, ios::end);
    length = fin.tellg();
    fin.seekg(0, ios::beg);

    // Временные переменные
    char buff[100];
    int count = 0;
    string* array = new string[length];
    string* temp = array;

    while (fin.getline(buff,100)) {
    }
    fin.close();
    cout << count << endl;
}

lab4::Problem1::Problem1(){
    alphabet = "abcdefghijklmnopqrstuvwxyz";
    main_counter = 0;

    int count[alphabet.length()] = {0};
    fin = openFile("C:\\Users\\simafrus\\CPP\\Labs\\cant_stop.txt");

    char ch;
    while (!fin.eof()) {
        ch = fin.get();
        count[alphabet.find(ch)]++;
        main_counter++;
    }

    fstream fout("C:\\Users\\simafrus\\CPP\\Labs\\lab4_problem1.txt", ios::out);

    for (int i = 0; i < alphabet.length(); i++) {
        fout << alphabet[i] << ": " << count[i] << endl;
    }
    cout << "Total: " << main_counter << endl;
}

fstream lab4::Problem1::openFile(string path) {
    fstream fin(path, ios::in);
    if (!fin.is_open()) {
        cout << "File not opened :(" << endl;
        exit(1);
    }

    return fin;
}

Problem2::Problem2() {
    clearFile("C:\\Users\\simafrus\\CPP\\Labs\\lab4_problem2.txt");
    alphabet = "abcdefghijklmnopqrstuvwxyz";
    fin = openFile("C:\\Users\\simafrus\\CPP\\Labs\\cant_stop.txt");
    while (!fin.eof()) {
        std::getline(fin, buff);
        if (buff.length() > max_length) {
            max_length = buff.length();
            clearFile("C:\\Users\\simafrus\\CPP\\Labs\\lab4_problem2.txt");
        }
        buff = "";
    }

    fin.seekg(0, ios::beg);
    while (!fin.eof()) {
        std::getline(fin, buff);
        if (buff.length() == max_length) {
            writeLine("C:\\Users\\simafrus\\CPP\\Labs\\lab4_problem2.txt", buff);
        }
    }
}

fstream Problem2::openFile(string path) {
    fstream fin(path, ios::in);
    if (!fin.is_open()) {
        cout << "File not opened :(" << endl;
        exit(1);
    }

    return fin;
}

void lab4::Problem2::clearFile(string path) {
    fstream fin(path, ios::trunc);
}


void lab4::Problem2::writeLine(string path, string line) {
    fstream fout(path, ios::app);
    if (!fout.is_open()) {
        cout << "File not opened :(" << endl;
        exit(1);
    }

    fout << line << endl;
}



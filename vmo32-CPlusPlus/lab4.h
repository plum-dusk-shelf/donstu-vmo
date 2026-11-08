#include <string>
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
using namespace std;

#ifndef LABS_LAB4_H
#define LABS_LAB4_H

namespace lab4 {
    void test();
    class Problem1 {
    private:
        string alphabet;
        int main_counter;
        fstream fin;
        public:
        Problem1();
        fstream openFile(string path);
    };

    class Problem2 {
        private:
        string alphabet;
        int max_length;
        fstream fin;
        fstream fout;
        string buff;
        int counter{};
        char s{};
        public:
        Problem2();
        fstream openFile(string path);
        void writeLine(string path, string line);
        void clearFile(string path);
    };
}

#endif //LABS_LAB4_H
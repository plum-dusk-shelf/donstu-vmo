#include "lab2_matrix.h"
#include <iostream>
#include <chrono>

using namespace std;

int run2() {
    int n = 5000;
     cout << "Matrixes size: " << n << endl;

    Matrix A(n, n), B(n, n);
    A.randomFill();
    B.randomFill();

    auto start = chrono::high_resolution_clock::now();
    Matrix C1 = A.add(B);
    auto end = chrono::high_resolution_clock::now();

    cout << "Sequential add: "
         << chrono::duration<double>(end - start).count() << " sec\n";

    start = chrono::high_resolution_clock::now();
    Matrix C2 = parallelAdd(A, B);
    end = chrono::high_resolution_clock::now();

    cout << "Thread add: "
         << chrono::duration<double>(end - start).count() << " sec\n";

    start = chrono::high_resolution_clock::now();
    Matrix C3 = asyncAdd(A, B);
    end = chrono::high_resolution_clock::now();

    cout << "Async add: "
         << chrono::duration<double>(end - start).count() << " sec\n";

    start = chrono::high_resolution_clock::now();
    Matrix C4 = winapiAdd(A, B);
    end = chrono::high_resolution_clock::now();

    cout << "WinAPI add: "
     << chrono::duration<double>(end - start).count() << " sec\n";

     n = 500;
     cout << "\n\nMatrixes size: " << n << endl;

     A = Matrix(n, n);
     B = Matrix(n, n);
     A.randomFill();
     B.randomFill();

     start = chrono::high_resolution_clock::now();
     Matrix C5 = A.multiply(B);
     end = chrono::high_resolution_clock::now();

     cout << "Sequential multiply: "
          << chrono::duration<double>(end - start).count() << " sec\n";

     start = chrono::high_resolution_clock::now();
     Matrix C6 = parallelMultiply(A, B);
     end = chrono::high_resolution_clock::now();

     cout << "Thread multipy: "
          << chrono::duration<double>(end - start).count() << " sec\n";

     start = chrono::high_resolution_clock::now();
     Matrix C7 = asyncMultiply(A, B);
     end = chrono::high_resolution_clock::now();

     cout << "Async multiply: "
          << chrono::duration<double>(end - start).count() << " sec\n";

     start = chrono::high_resolution_clock::now();
     Matrix C8 = winapiMultiply(A, B);
     end = chrono::high_resolution_clock::now();

     cout << "WinAPI multiply: "
      << chrono::duration<double>(end - start).count() << " sec\n";
     return 0;
}

using Row = std::vector<double>;
using Dataset = std::vector<Row>;

int run22() {
     Dataset csv = loadCSV("C:\\Users\\simafrus\\CPP\\PCDA\\wine.csv");
     Dataset cleaned = asyncRemoveZeroRows(csv);
     int csv_len, cleaned_len;
     for (auto line: csv) csv_len += 1;
     for (auto line: cleaned) cleaned_len += 1;
     cout << "From: " << csv_len << " to: " << cleaned_len << endl;
     return  0;
     for (auto& row : cleaned) {
          for (double x : row)
               std::cout << x << " ";
          std::cout << "\n";
     }
     return 0;
}
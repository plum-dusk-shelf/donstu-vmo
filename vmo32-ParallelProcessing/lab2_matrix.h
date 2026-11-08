#ifndef MATRIX_H
#define MATRIX_H

#include <vector>
#include <thread>
#include <future>

class Matrix {
private:
    int rows, cols;
    std::vector<std::vector<double>> data;

public:
    Matrix(int r = 0, int c = 0);

    void randomFill();
    void print() const;

    Matrix add(const Matrix& other) const;
    Matrix multiply(const Matrix& other) const;

    int getRows() const;
    int getCols() const;

    std::vector<double>& operator[](int i);
    const std::vector<double>& operator[](int i) const;
};

Matrix parallelAdd(const Matrix& A, const Matrix& B);
Matrix parallelMultiply(const Matrix& A, const Matrix& B);

Matrix asyncAdd(const Matrix& A, const Matrix& B);
Matrix asyncMultiply(const Matrix& A, const Matrix& B);

Matrix winapiAdd(const Matrix& A, const Matrix& B);
Matrix winapiMultiply(const Matrix& A, const Matrix& B);

using Row = std::vector<double>;
using Dataset = std::vector<Row>;
Dataset loadCSV(const std::string& filename);
Dataset asyncRemoveZeroRows(const Dataset& data);

#endif
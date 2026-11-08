#include "lab2_matrix.h"
#include <iostream>
#include <random>
#include <windows.h>

using namespace std;

Matrix::Matrix(int r, int c) : rows(r), cols(c), data(r, vector<double>(c)) {}

void Matrix::randomFill() {
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dis(0, 10);

    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            data[i][j] = dis(gen);
}

void Matrix::print() const {
    for (auto& row : data) {
        for (auto& x : row)
            cout << x << " ";
        cout << endl;
    }
}

Matrix Matrix::add(const Matrix& other) const {
    Matrix res(rows, cols);
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            res.data[i][j] = data[i][j] + other.data[i][j];
    return res;
}

Matrix Matrix::multiply(const Matrix& other) const {
    Matrix res(rows, other.cols);
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < other.cols; j++)
            for (int k = 0; k < cols; k++)
                res.data[i][j] += data[i][k] * other.data[k][j];
    return res;
}

int Matrix::getRows() const { return rows; }
int Matrix::getCols() const { return cols; }

vector<double>& Matrix::operator[](int i) { return data[i]; }
const vector<double>& Matrix::operator[](int i) const { return data[i]; }

void addPart(const Matrix& A, const Matrix& B, Matrix& R, int start, int end) {
    for (int i = start; i < end; i++)
        for (int j = 0; j < A.getCols(); j++)
            R[i][j] = A[i][j] + B[i][j];
}

Matrix parallelAdd(const Matrix& A, const Matrix& B) {
    int n = A.getRows();
    Matrix R(n, A.getCols());

    int threadsCount = thread::hardware_concurrency();
    vector<thread> threads;

    int block = n / threadsCount;

    for (int i = 0; i < threadsCount; i++) {
        int start = i * block;
        int end = (i == threadsCount - 1) ? n : start + block;

        threads.emplace_back(addPart, cref(A), cref(B), ref(R), start, end);
    }

    for (auto& t : threads) t.join();

    return R;
}

void multPart(const Matrix& A, const Matrix& B, Matrix& R, int start, int end) {
    for (int i = start; i < end; i++) {
        for (int j = 0; j < B.getCols(); j++) {
            for (int k = 0; k < A.getCols(); k++) {
                R[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

Matrix parallelMultiply(const Matrix& A, const Matrix& B) {
    int n = A.getRows();
    Matrix R(n, B.getCols());

    int threadsCount = std::thread::hardware_concurrency();
    if (threadsCount == 0) threadsCount = 4;

    int block = n / threadsCount;

    std::vector<std::thread> threads;

    for (int i = 0; i < threadsCount; i++) {
        int start = i * block;
        int end = (i == threadsCount - 1) ? n : start + block;

        threads.emplace_back(multPart,
                             std::cref(A),
                             std::cref(B),
                             std::ref(R),
                             start,
                             end);
    }

    for (auto& t : threads) t.join();

    return R;
}

Matrix asyncAdd(const Matrix& A, const Matrix& B) {
    int n = A.getRows();
    Matrix R(n, A.getCols());
    std::vector<std::future<void>> futures;

    int threadsCount = thread::hardware_concurrency();

    int block = n / threadsCount;

    for (int i = 0; i < threadsCount; i++) {
        int start = i * block;
        int end = (i == threadsCount - 1) ? n : start + block;

        futures.push_back(async(launch::async, addPart, cref(A), cref(B), ref(R), start, end));
    }

    for (auto& f: futures) f.get();

    return R;
    /*
    return async(launch::async, [&]() {
        return A.add(B);
    }).get();
    */
}

Matrix asyncMultiply(const Matrix& A, const Matrix& B) {
    int n = A.getRows();
    Matrix R(n, B.getCols());

    int threadsCount = std::thread::hardware_concurrency();
    if (threadsCount == 0) threadsCount = 4;

    int block = n / threadsCount;

    std::vector<std::future<void>> futures;

    for (int i = 0; i < threadsCount; i++) {
        int start = i * block;
        int end = (i == threadsCount - 1) ? n : start + block;

        futures.push_back(std::async(std::launch::async,
            multPart,
            std::cref(A),
            std::cref(B),
            std::ref(R),
            start,
            end
        ));
    }

    for (auto& f : futures)
        f.get();

    return R;
}


struct ThreadData {
    const Matrix* A;
    const Matrix* B;
    Matrix* R;
    int start, end;
};

DWORD WINAPI addThread(LPVOID param) {
    ThreadData* d = (ThreadData*)param;

    for (int i = d->start; i < d->end; i++)
        for (int j = 0; j < d->A->getCols(); j++)
            (*(d->R))[i][j] = (*(d->A))[i][j] + (*(d->B))[i][j];

    return 0;
}

Matrix winapiAdd(const Matrix& A, const Matrix& B) {
    int n = A.getRows();
    Matrix R(n, A.getCols());

    const int threadsCount = 4;
    HANDLE threads[threadsCount];
    ThreadData data[threadsCount];

    int block = n / threadsCount;

    for (int i = 0; i < threadsCount; i++) {
        data[i] = { &A, &B, &R,
                   i * block,
                   (i == threadsCount - 1) ? n : (i + 1) * block };

        threads[i] = CreateThread(NULL, 0, addThread, &data[i], 0, NULL);
    }

    WaitForMultipleObjects(threadsCount, threads, TRUE, INFINITE);

    for (int i = 0; i < threadsCount; i++)
        CloseHandle(threads[i]);

    return R;
}

DWORD WINAPI multThread(LPVOID param) {
    ThreadData* d = (ThreadData*)param;

    for (int i = d->start; i < d->end; i++) {
        for (int j = 0; j < d->B->getCols(); j++) {
            for (int k = 0; k < d->A->getCols(); k++) {
                (*(d->R))[i][j] += (*(d->A))[i][k] * (*(d->B))[k][j];
            }
        }
    }

    return 0;
}


Matrix winapiMultiply(const Matrix& A, const Matrix& B) {
    int n = A.getRows();
    Matrix R(n, B.getCols());

    const int threadsCount = 4;
    HANDLE threads[threadsCount];
    ThreadData data[threadsCount];

    int block = n / threadsCount;

    for (int i = 0; i < threadsCount; i++) {
        int start = i * block;
        int end = (i == threadsCount - 1) ? n : start + block;

        data[i] = { &A, &B, &R, start, end };

        threads[i] = CreateThread(NULL, 0, multThread, &data[i], 0, NULL);
    }

    WaitForMultipleObjects(threadsCount, threads, TRUE, INFINITE);

    for (int i = 0; i < threadsCount; i++)
        CloseHandle(threads[i]);

    return R;
}

#include <fstream>
#include <sstream>

using Row = std::vector<double>;
using Dataset = std::vector<Row>;
#include <fstream>
#include <sstream>
#include <algorithm>

double safeStod(std::string cell) {
    cell.erase(remove_if(cell.begin(), cell.end(), ::isspace), cell.end());

    if (cell.empty() || cell == "NA" || cell == "null" || cell == "?")
        return 0.0;

    try {
        return std::stod(cell);
    } catch (...) {
        return 0.0;
    }
}

Dataset loadCSV(const std::string& filename) {
    Dataset data;
    std::ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "File opening error\n";
        return data;
    }

    std::string line;

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        Row row;

        while (std::getline(ss, cell, ',')) {
            row.push_back(safeStod(cell));
        }

        if (!row.empty())
            data.push_back(row);
    }

    return data;
}
/*
Dataset loadCSV(const std::string& filename) {
    Dataset data;
    std::ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "File open error\n";
        return data;
    }

    std::string line;

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        Row row;

        while (std::getline(ss, cell, ',')) {
            if (cell.empty()) {
                row.push_back(0.0); 
            } else {
                row.push_back(std::stod(cell));
            }
        }

        data.push_back(row);
    }

    return data;
}
*/
void filterPart(const Dataset& input,
                Dataset& output,
                std::mutex& mtx,
                int start,
                int end)
{
    Dataset local;

    for (int i = start; i < end; i++) {
        bool hasZero = false;

        for (double val : input[i]) {
            if (val == 0) {
                hasZero = true;
                break;
            }
        }

        if (!hasZero)
            local.push_back(input[i]);
    }

    std::lock_guard<std::mutex> lock(mtx);
    output.insert(output.end(), local.begin(), local.end());
}

#include <future>
#include <thread>
#include <mutex>

Dataset asyncRemoveZeroRows(const Dataset& data) {
    int n = data.size();

    int threadsCount = std::thread::hardware_concurrency();
    if (threadsCount == 0) threadsCount = 4;

    int block = n / threadsCount;

    Dataset result;
    std::mutex mtx;

    std::vector<std::future<void>> futures;

    for (int i = 0; i < threadsCount; i++) {
        int start = i * block;
        int end = (i == threadsCount - 1) ? n : start + block;

        futures.push_back(std::async(std::launch::async,
            filterPart,
            std::cref(data),
            std::ref(result),
            std::ref(mtx),
            start,
            end
        ));
    }

    for (auto& f : futures)
        f.get();

    return result;
}
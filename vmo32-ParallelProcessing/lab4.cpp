#include "lab4.h"
#include <omp.h>
#include <random>
#include <iostream>

void run4() {
    int threads = 4;

    
    int steps = 10000000;

    double t1 = omp_get_wtime();
    double pi_seq = compute_pi_sequential(steps);
    double t2 = omp_get_wtime();

    double pi_par = compute_pi_parallel(steps, threads);
    double t3 = omp_get_wtime();

    std::cout << "PI sequential: " << pi_seq << " time: " << t2 - t1 << "\n";
    std::cout << "PI parallel:   " << pi_par << " time: " << t3 - t2 << "\n\n";

    
    int size = 5000;
    auto arr1 = generate_array(size);
    auto arr2 = arr1;

    t1 = omp_get_wtime();
    selection_sort_sequential(arr1);
    t2 = omp_get_wtime();

    selection_sort_parallel(arr2, threads);
    t3 = omp_get_wtime();

    std::cout << "Sort sequential: " << t2 - t1 << "\n";
    std::cout << "Sort parallel:   " << t3 - t2 << "\n\n";

    
    int n = 300;
    auto A = generate_matrix(n, n);
    auto B = generate_matrix(n, n);

    t1 = omp_get_wtime();
    auto C1 = multiply_sequential(A, B);
    t2 = omp_get_wtime();

    auto C2 = multiply_parallel(A, B, threads);
    t3 = omp_get_wtime();

    std::cout << "Matrix sequential: " << t2 - t1 << "\n";
    std::cout << "Matrix parallel:   " << t3 - t2 << "\n\n";

    int m = 1000;
    auto X = generate_matrix(m, n);

    t1 = omp_get_wtime();
    auto X1 = square_parallel(X, threads);
    t2 = omp_get_wtime();

    std::cout << "Matrix square sequential: " << t2 - t1 << "\n";
}


double compute_pi_sequential(int num_steps) {
    double step = 1.0 / num_steps;
    double sum = 0.0;

    for (int i = 0; i < num_steps; i++) {
        double x = (i + 0.5) * step;
        sum += 4.0 / (1.0 + x * x);
    }

    return step * sum;
}

double compute_pi_parallel(int num_steps, int num_threads) {
    double step = 1.0 / num_steps;
    double sum = 0.0;

#pragma omp parallel for reduction(+:sum) num_threads(num_threads)
    for (int i = 0; i < num_steps; i++) {
        double x = (i + 0.5) * step;
        sum += 4.0 / (1.0 + x * x);
    }

    return step * sum;
}


void selection_sort_sequential(std::vector<int>& arr) {
    int n = arr.size();

    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;

        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[min_idx])
                min_idx = j;
        }

        std::swap(arr[i], arr[min_idx]);
    }
}

void selection_sort_parallel(std::vector<int>& arr, int num_threads) {
    int n = arr.size();

    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;

#pragma omp parallel for num_threads(num_threads)
        for (int j = i + 1; j < n; j++) {
#pragma omp critical
            {
                if (arr[j] < arr[min_idx]) {
                    min_idx = j;
                }
            }
        }

        std::swap(arr[i], arr[min_idx]);
    }
}


Matrix multiply_sequential(const Matrix& A, const Matrix& B) {
    int n = A.size();
    int m = B[0].size();
    int k = B.size();

    Matrix C(n, std::vector<double>(m, 0));

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            for (int t = 0; t < k; t++)
                C[i][j] += A[i][t] * B[t][j];

    return C;
}

Matrix multiply_parallel(const Matrix& A, const Matrix& B, int num_threads) {
    int n = A.size();
    int m = B[0].size();
    int k = B.size();

    Matrix C(n, std::vector<double>(m, 0));

#pragma omp parallel for num_threads(num_threads)
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            for (int t = 0; t < k; t++)
                C[i][j] += A[i][t] * B[t][j];

    return C;
}

Matrix square_parallel(const Matrix& A, int num_threads) {
    int n = A.size();
    int m = A[0].size();

    Matrix X1(n, std::vector<double>(n, 0));

#pragma omp parallel for num_threads(num_threads)
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            X1[i][j] = A[i][j] * A[i][j];

    return X1;
}


Matrix generate_matrix(int n, int m) {
    Matrix mat(n, std::vector<double>(m));

    std::mt19937 gen(42);
    std::uniform_real_distribution<> dist(0, 10);

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            mat[i][j] = dist(gen);

    return mat;
}

std::vector<int> generate_array(int size) {
    std::vector<int> arr(size);

    std::mt19937 gen(42);
    std::uniform_int_distribution<> dist(0, 10000);

    for (int i = 0; i < size; i++)
        arr[i] = dist(gen);

    return arr;
}
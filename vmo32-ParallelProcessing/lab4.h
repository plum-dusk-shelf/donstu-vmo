#ifndef LAB4_H
#define LAB4_H

#include <vector>

void run4();

double compute_pi_sequential(int num_steps);
double compute_pi_parallel(int num_steps, int num_threads);

void selection_sort_sequential(std::vector<int>& arr);
void selection_sort_parallel(std::vector<int>& arr, int num_threads);

using Matrix = std::vector<std::vector<double>>;

Matrix multiply_sequential(const Matrix& A, const Matrix& B);
Matrix multiply_parallel(const Matrix& A, const Matrix& B, int num_threads);
Matrix square_parallel(const Matrix& A, int num_threads);

Matrix generate_matrix(int n, int m);
std::vector<int> generate_array(int size);

#endif
#ifndef LAB5_H
#define LAB5_H
#include <vector>
#include <string>

void run5(int argc, char* argv[]);
int run5_2(int argc, char* argv[]);

double f(double x);

std::vector<std::vector<double>>
load_csv(const std::string& filename);
void append_zero_rows(const std::string& filename);

double rectangle_method(double a, double b, int n);
double trapezoid_method(double a, double b, int n);
double simpson_method(double a, double b, int n);

double mpi_rectangle(double a, double b, int n, int rank, int size);
double mpi_trapezoid(double a, double b, int n, int rank, int size);
double mpi_simpson(double a, double b, int n, int rank, int size);

void mpi_dropna(
    const std::string& filename,
    int rank,
    int size
);

#endif
#include "lab5.h"
#include <mpi.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>

void run5(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    double a = 0.0, b = 1.0;
    int n = 1000000;

    double start, end;

    if (rank == 0) {
        start = MPI_Wtime();
        double pi = rectangle_method(a, b, n);
        end = MPI_Wtime();
        std::cout << "Sequential rectangle: " << pi
                  << " Time: " << end - start << std::endl;
    }

    MPI_Barrier(MPI_COMM_WORLD);

    start = MPI_Wtime();
    double pi_rect = mpi_rectangle(a, b, n, rank, size);
    end = MPI_Wtime();

    if (rank == 0) {
        std::cout << "MPI rectangle: " << pi_rect
                  << " Time: " << end - start << std::endl;
    }

    start = MPI_Wtime();
    double pi_trap = mpi_trapezoid(a, b, n, rank, size);
    end = MPI_Wtime();

    if (rank == 0) {
        std::cout << "MPI trapezoid: " << pi_trap
                  << " Time: " << end - start << std::endl;
    }

    start = MPI_Wtime();
    double pi_simp = mpi_simpson(a, b, n, rank, size);
    end = MPI_Wtime();

    if (rank == 0) {
        std::cout << "MPI Simpson: " << pi_simp
                  << " Time: " << end - start << std::endl;
    }

    MPI_Finalize();
}

int run5_2(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    double start, end;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    start = MPI_Wtime();
    mpi_dropna("C:\\Users\\simafrus\\CPP\\PCDA\\wine.csv", rank, size);
    end = MPI_Wtime();

    if (rank == 0) {
        std::cout << "MPI Dropna time: " << end - start << std::endl;
    }

    MPI_Finalize();

    return 0;
}

// функция для интегрирования
double f(double x) {
    return 4.0 / (1.0 + x * x);
}


double rectangle_method(double a, double b, int n) {
    double h = (b - a) / n;
    double sum = 0.0;

    for (int i = 0; i < n; i++) {
        double x = a + i * h;
        sum += f(x);
    }

    return sum * h;
}

double trapezoid_method(double a, double b, int n) {
    double h = (b - a) / n;
    double sum = (f(a) + f(b)) / 2.0;

    for (int i = 1; i < n; i++) {
        sum += f(a + i * h);
    }

    return sum * h;
}

double simpson_method(double a, double b, int n) {
    if (n % 2 != 0) n++;

    double h = (b - a) / n;
    double sum = f(a) + f(b);

    for (int i = 1; i < n; i++) {
        double x = a + i * h;
        sum += (i % 2 == 0) ? 2 * f(x) : 4 * f(x);
    }

    return sum * h / 3.0;
}


double mpi_rectangle(double a, double b, int n, int rank, int size) {
    double h = (b - a) / n;
    int local_n = n / size;

    double local_a = a + rank * local_n * h;
    double local_b = local_a + local_n * h;

    double local_sum = rectangle_method(local_a, local_b, local_n);
    double global_sum = 0.0;

    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    return global_sum;
}

double mpi_trapezoid(double a, double b, int n, int rank, int size) {
    double h = (b - a) / n;
    int local_n = n / size;

    double local_a = a + rank * local_n * h;
    double local_b = local_a + local_n * h;

    double local_sum = trapezoid_method(local_a, local_b, local_n);
    double global_sum = 0.0;

    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    return global_sum;
}

double mpi_simpson(double a, double b, int n, int rank, int size) {
    if (n % 2 != 0) n++;

    double h = (b - a) / n;
    int local_n = n / size;

    double local_a = a + rank * local_n * h;
    double local_b = local_a + local_n * h;

    double local_sum = simpson_method(local_a, local_b, local_n);
    double global_sum = 0.0;

    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    return global_sum;
}

void mpi_dropna(
    const std::string& filename,
    int rank,
    int size
) {

    std::vector<std::vector<double>> data;

    if (rank == 0) {
        data = load_csv(filename);
    }


    int total_rows = 0;

    if (rank == 0)
        total_rows = data.size();

    MPI_Bcast(
        &total_rows,
        1,
        MPI_INT,
        0,
        MPI_COMM_WORLD
    );


    int cols = 0;

    if (rank == 0 && total_rows > 0)
        cols = data[0].size();

    MPI_Bcast(
        &cols,
        1,
        MPI_INT,
        0,
        MPI_COMM_WORLD
    );


    std::vector<double> flat_data;

    if (rank == 0) {

        flat_data.resize(total_rows * cols);

        for (int i = 0; i < total_rows; i++) {
            for (int j = 0; j < cols; j++) {
                flat_data[i * cols + j] = data[i][j];
            }
        }
    }

    if (rank != 0)
        flat_data.resize(total_rows * cols);

    MPI_Bcast(
        flat_data.data(),
        total_rows * cols,
        MPI_DOUBLE,
        0,
        MPI_COMM_WORLD
    );


    int rows_per_proc = total_rows / size;

    int start = rank * rows_per_proc;

    int end = (rank == size - 1)
        ? total_rows
        : start + rows_per_proc;

    std::vector<double> local_cleaned;

    int local_rows = 0;

    for (int i = start; i < end; i++) {

        bool all_zero = true;

        for (int j = 0; j < cols; j++) {

            double val = flat_data[i * cols + j];

            if (val != 0.0) {
                all_zero = false;
                break;
            }
        }

        if (!all_zero) {

            for (int j = 0; j < cols; j++) {
                local_cleaned.push_back(
                    flat_data[i * cols + j]
                );
            }

            local_rows++;
        }
    }


    std::vector<int> recv_counts(size);

    MPI_Gather(
        &local_rows,
        1,
        MPI_INT,
        recv_counts.data(),
        1,
        MPI_INT,
        0,
        MPI_COMM_WORLD
    );


    if (rank == 0) {

        std::vector<std::vector<double>> result;

        for (int i = 0; i < local_rows; i++) {

            std::vector<double> row;

            for (int j = 0; j < cols; j++) {
                row.push_back(
                    local_cleaned[i * cols + j]
                );
            }

            result.push_back(row);
        }

        for (int proc = 1; proc < size; proc++) {

            int rows = recv_counts[proc];

            std::vector<double> recv_buffer(
                rows * cols
            );

            MPI_Recv(
                recv_buffer.data(),
                rows * cols,
                MPI_DOUBLE,
                proc,
                0,
                MPI_COMM_WORLD,
                MPI_STATUS_IGNORE
            );

            for (int i = 0; i < rows; i++) {

                std::vector<double> row;

                for (int j = 0; j < cols; j++) {

                    row.push_back(
                        recv_buffer[i * cols + j]
                    );
                }

                result.push_back(row);
            }
        }


        std::ofstream output(filename);

        for (auto& row : result) {

            for (size_t j = 0; j < row.size(); j++) {

                output << row[j];

                if (j != row.size() - 1)
                    output << ",";
            }

            output << "\n";
        }

        output.close();

        std::cout << "CSV cleaned successfully\n";
    }

    else {

        MPI_Send(
            local_cleaned.data(),
            local_rows * cols,
            MPI_DOUBLE,
            0,
            0,
            MPI_COMM_WORLD
        );
    }
}

std::vector<std::vector<double>>
load_csv(const std::string& filename) {

    std::vector<std::vector<double>> data;

    std::ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "Cannot open file: "
                  << filename << std::endl;
        return data;
    }

    std::string line;

    while (std::getline(file, line)) {

        if (line.empty())
            continue;

        std::stringstream ss(line);

        std::vector<double> row;

        std::string cell;

        bool valid_row = true;

        while (std::getline(ss, cell, ',')) {

            if (cell.empty()) {
                valid_row = false;
                break;
            }

            try {
                row.push_back(std::stod(cell));
            }
            catch (...) {
                valid_row = false;
                break;
            }
        }

        if (valid_row && !row.empty()) {
            data.push_back(row);
        }
    }

    return data;
}

void append_zero_rows(const std::string& filename) {

    std::ifstream infile(filename);

    if (!infile.is_open()) {
        std::cerr << "Cannot open file for reading: "
                  << filename << std::endl;
        return;
    }

    std::vector<std::string> lines;

    std::string line;

    while (std::getline(infile, line)) {

        lines.push_back(line);

        std::stringstream ss(line);

        std::string cell;

        int cols = 0;

        while (std::getline(ss, cell, ',')) {
            cols++;
        }

        std::string zero_row;

        for (int i = 0; i < cols; i++) {

            zero_row += "0";

            if (i != cols - 1)
                zero_row += ",";
        }

        lines.push_back(zero_row);
    }

    infile.close();

    std::ofstream outfile(filename);

    if (!outfile.is_open()) {
        std::cerr << "Cannot open file for writing: "
                  << filename << std::endl;
        return;
    }

    for (const auto& l : lines) {
        outfile << l << "\n";
    }

    outfile.close();
}
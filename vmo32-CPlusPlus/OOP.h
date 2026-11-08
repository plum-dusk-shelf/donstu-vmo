#ifndef LABS_OOP_H
#define LABS_OOP_H
#include <vector>
#include <string>
#include <array>
using namespace std;

namespace OOP {
    void run_OOP();

    class Vec {
    private:
        float* coordinates;
        int dim;
        string name;
    public:
        Vec() = default;
        Vec(string name);
        Vec(int dim, float& coordinates, string name);
        Vec(string name, int dim, float& coordinates);

        string getName() const;
        string getCoordinates() const;
    };

    template <typename T>
    class Matrix {
        private:
            vector<vector<T>> data;
        void makeRectangle();

        public:
        Matrix(const vector<vector<T>>& d): data(d) {makeRectangle();}
        size_t getRows() const;
        size_t getColumns() const;
        };

}

#endif //LABS_OOP_H
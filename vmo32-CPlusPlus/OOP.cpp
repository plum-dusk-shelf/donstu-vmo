#include "OOP.h"
#include <iostream>
#include <ostream>
#include <vector>
#include <string>
using namespace OOP;
using namespace std;

void OOP::run_OOP() {
    cout << "Running OOP" << endl;

    vector<vector<float>> pre_m = {{2,3},{5,7}, {9,10}};
    Matrix<float> m(pre_m);
    cout << m.getRows() << endl << m.getColumns() << endl;
}

template<typename T>
void OOP::Matrix<T>::makeRectangle() {
    size_t maxSize = 0;
    for (const auto& row : data) {
        if (row.size() > maxSize) {
            maxSize = row.size();
        }
    }

    for (auto& row : data) {
        row.resize(maxSize);
    }
}


template<typename T>
size_t OOP::Matrix<T>::getRows() const{
    return data.size();
}

template<typename T>
size_t OOP::Matrix<T>::getColumns() const {
    if (data.empty()) {
        return 0;
    }
    return data[0].size();
}


string OOP::Vec::getName() const {
    return name;
}

string OOP::Vec::getCoordinates() const {
    if (coordinates == 0) return "zero-vector";
    string coordinates_str;
    // for (auto i : coordinates) {
    //     coordinates_str += to_string(i) + " ";
    // }
    return coordinates_str;
}

OOP::Vec::Vec(string name) : name(name), coordinates(new float[0]), dim(0){}
OOP::Vec::Vec(string name, int dim, float& coordinates) : name(name), coordinates(&coordinates), dim(dim){}
OOP::Vec::Vec(int dim, float& coordinates, string name) : coordinates(&coordinates), name(name), dim(dim) {}
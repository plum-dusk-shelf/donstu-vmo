//
// Created by simafrus on 10.02.2026.
//

#ifndef PCDA_LAB1_H
#define PCDA_LAB1_H
#include <chrono>

void isAVX();

template<typename Func, typename... Args>
std::chrono::nanoseconds timer(Func *func, Args... args);

void run1();
void print_all_at_once(int n);
float time_compare(std::chrono::nanoseconds a, std::chrono::nanoseconds b);

namespace scalar_algs {
    float y_eq_x(float x);
    float calc_pi(float x);
    float rectangles(float (*func)(float), float a, float b, int n);
    float trapezoida(float (*func)(float), float a, float b, int n);
    float simpson(float (*func)(float), float a, float b, int n);
};

namespace simd_algs {
    __m128 y_eq_x(__m128 x_vec);
    __m128 calc_pi(__m128 x_vec);
    float rectangles(__m128 (*func)(__m128), float a, float b, int n);
    float trapezoida(__m128 (*func)(__m128), float a, float b, int n);
    float simpson(__m128 (*func)(__m128), float a, float b, int n);
}


#endif
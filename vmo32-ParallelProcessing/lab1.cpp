#include <iostream>
#include <ostream>
#include <immintrin.h> 
#include "lab1.h"
#include <string>
#include <chrono>
#include <cmath>
using namespace std;

void run1() {
    isAVX();
    int n = 100*10^6;
    float a = 0, b = 1;
    int rows = 2, cols = 3;
    chrono::nanoseconds times[2][3] = {
        {timer(scalar_algs::rectangles, scalar_algs::calc_pi, 0, 1, n),
            timer(scalar_algs::trapezoida, scalar_algs::calc_pi, 0, 1, n),
            timer(scalar_algs::simpson, scalar_algs::calc_pi, 0, 1, n)},

        {timer(simd_algs::rectangles, simd_algs::calc_pi, 0, 1, n),
            timer(simd_algs::trapezoida, simd_algs::calc_pi, 0, 1, n),
            timer(simd_algs::simpson, simd_algs::calc_pi, 0, 1, n)}
    };

    // int index = 0;
    // for (int row = 0; row < rows; row++) {
    //     for (int col = 0; col < cols; col++) {
    //         cout << times[row][col] << " ";
    //         index++;
    //     }
    //     cout << endl;
    // }

    cout << endl << endl;
    cout << "              " << "Scalar" << "   SIMD" << "    Diff" << endl;
    cout << "Rectangles :  " << times[0][0] << "   " << times[1][0] << "  " << time_compare(times[0][0], times[1][0]) << "%" << endl;
    cout << "Trapezoidas:  " << times[0][1] << "   " << times[1][1] << "  " << time_compare(times[0][1], times[1][1]) << "%" << endl;
    cout << "Simpsons   :  " << times[0][2] << "   " << times[1][2] << "  " << time_compare(times[0][2], times[1][2]) << "%" << endl;
}

void isAVX() {
#ifdef __AVX__
    std::cout << "AVX support is ENABLED!" << std::endl;
#else
    std::cout << "AVX support is DISABLED!" << std::endl;
#endif
}

template<typename Func, typename... Args>
chrono::nanoseconds timer(Func *func, Args... args) {
    using namespace std::chrono;

    auto start = high_resolution_clock::now();
    auto result = func(args...);
    auto end = high_resolution_clock::now();
    auto duration = end - start;

    cout << result << "\t";
    cout << endl;
    return duration_cast<nanoseconds>(duration);
}

float time_compare(std::chrono::nanoseconds a, std::chrono::nanoseconds b) {
    float percents = (1 - static_cast<double>(b.count()) / static_cast<double>(a.count()))*100;
    return percents;
}

float scalar_algs::y_eq_x(float x) {
    return x;
}

float scalar_algs::calc_pi(float x) {
    return 4 * sqrt(1 - pow(x, 2));
}


float scalar_algs::rectangles(float (*func)(float), float a, float b, int n) {
    float h = (b - a) / n; 
    float sum = 0;
    float x_curr  = a;
    for (int i = 0; i < n; i++) {
        sum += func(x_curr);
        x_curr += h;
    }

    return sum * h;
}

float scalar_algs::trapezoida(float (*func)(float), float a, float b, int n) {
    float h = (b - a) / n;
    float sum, x_curr;

    sum = (func(a) + func(b)) / 2;
    for (int i = 0; i < n; i++) {
        x_curr = a + i*h;
        sum += func(x_curr);
    }

    return sum * h;
}

float scalar_algs::simpson(float (*func)(float), float a, float b, int n) {

    if (n % 2 != 0) {
        throw -1;
    }

    float h = (b - a) / n;
    float sum = func(a) - func(b);
    float x_curr = 0;

    for (int i = 2; i <= n-2; i+=2) {
        x_curr = a + i*h;
        sum += 2 * func(x_curr);
    }

    for (int i = 1; i <= n-1; i+=2) {
        x_curr = a + i*h;
        sum += 4 * func(x_curr);
    }

    return  sum * h / 3;
}

__m128 simd_algs::y_eq_x(__m128 x_vec) {
    return x_vec; 
}

__m128 simd_algs::calc_pi(__m128 x_vec) {
    __m128 x_squared = _mm_mul_ps(x_vec, x_vec);

    __m128 one = _mm_set1_ps(1.0f);
    __m128 one_minus_x2 = _mm_sub_ps(one, x_squared);

    __m128 sqrt_result = _mm_sqrt_ps(one_minus_x2);

    __m128 four = _mm_set1_ps(4.0f);
    __m128 result = _mm_mul_ps(four, sqrt_result);

    return result;
}

float horizontal_sum_sse(__m128 v) {
#ifdef __SSE3__
    v = _mm_hadd_ps(v, v);    
    v = _mm_hadd_ps(v, v);    

    float result;
    _mm_store_ps(&result, v);
    return result;
#else
    return horizontal_sum_sse(v);  
#endif
}

float simd_algs::rectangles(__m128 (*func)(__m128), float a, float b, int n) {
    float h = (b - a) / n; 

    __m128 sum_vec = _mm_setzero_ps();  
    __m128 h_vec = _mm_set1_ps(h);          
    __m128 a_vec = _mm_set1_ps(a);          
    __m128 step_vec = _mm_set1_ps(4 * h); 
    __m128 indices = _mm_set_ps( 3.0f, 2.0f, 1.0f, 0.0f);
    __m128 x_vec = _mm_add_ps(a_vec, _mm_mul_ps(indices, h_vec));

    for (int i = 0; i < n/4; i+=1) {
        __m128 f_vec = func(x_vec);
        sum_vec = _mm_add_ps(sum_vec, f_vec);
        x_vec = _mm_add_ps(x_vec, step_vec);
    }

    float sum = horizontal_sum_sse(sum_vec);

    return sum * h;
}

float simd_algs::trapezoida(__m128 (*func)(__m128), float a, float b, int n) {
    float h = (b - a) / n; 

    __m128 sum_vec = _mm_setzero_ps();  
    __m128 h_vec = _mm_set1_ps(h);          
    __m128 a_vec = _mm_set1_ps(a);          
    __m128 step_vec = _mm_set1_ps(4 * h); 
    __m128 indices = _mm_set_ps(3.0f, 2.0f, 1.0f, 0.0f);

    __m128 x_vec = _mm_add_ps(a_vec, _mm_mul_ps(indices, h_vec));

    for (int i = 0; i < n/4; i++) {
        __m128 f_vec = func(x_vec);           
        sum_vec = _mm_add_ps(sum_vec, f_vec); 
        x_vec = _mm_add_ps(x_vec, step_vec);  
    }

    float sum = horizontal_sum_sse(sum_vec);

    return sum * h;
}

float simd_algs::simpson(__m128 (*func)(__m128), float a, float b, int n) {
    if (n % 2 != 0) {
        n++; 
    }

    float h = (b - a) / n; 

    __m128 sum_odd = _mm_setzero_ps();  
    __m128 sum_even = _mm_setzero_ps(); 

    __m128 h_vec = _mm_set1_ps(h);           
    __m128 a_vec = _mm_set1_ps(a);            
    __m128 step_vec = _mm_set1_ps(4 * h);     

    __m128 indices = _mm_set_ps(4.0f, 3.0f, 2.0f, 1.0f);
    __m128 x_vec = _mm_add_ps(a_vec, _mm_mul_ps(indices, h_vec));

    for (int i = 1; i < n/4; i++) {
        __m128 f_vec = func(x_vec); 

        __m128 mask_odd = _mm_set_ps(0.0f, 1.0f, 0.0f, 1.0f); 
        __m128 mask_even = _mm_set_ps(1.0f, 0.0f, 1.0f, 0.0f); 

        sum_odd = _mm_add_ps(sum_odd, _mm_mul_ps(f_vec, mask_odd));
        sum_even = _mm_add_ps(sum_even, _mm_mul_ps(f_vec, mask_even));

        x_vec = _mm_add_ps(x_vec, step_vec);
    }


    float sum_odd_total = horizontal_sum_sse(sum_odd);
    float sum_even_total = horizontal_sum_sse(sum_even);

    float fa = horizontal_sum_sse(func(_mm_set1_ps(a)));
    float fb = horizontal_sum_sse(func(_mm_set1_ps(b)));

    return  (h / 3.0f) * (fa + fb + 4.0f * sum_odd_total + 2.0f * sum_even_total);
}
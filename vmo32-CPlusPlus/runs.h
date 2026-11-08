#include "lab1.h"
#include "lab2.h"
#include "lab3.h"
#include "lab4.h"
#include "lab6.h"
#include "lab7.h"
#include "lab8.h"
#include "lab4_problem3.h"
using namespace lab4;


#ifndef LABS_RUNS_H
#define LABS_RUNS_H

namespace runs {
    inline void run_lab4_problem1() {
        Problem1 problem1;
    }

    inline void run_lab4_problem2() {
        Problem2 problem2;
    }

    inline void run_lab7() {
        lab7::run_lab7();
    }

    inline void run__lab8() {
        lab8::run_lab8();
    }

}
#endif //LABS_RUNS_H
#include <string>
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
using namespace std;

#ifndef LABS_LAB4_PROBLEM3_H
#define LABS_LAB4_PROBLEM3_H

namespace lab4_problem3 {
    void run_lab4_problem3();

    struct Movie{
        int count=0;
        string title;
        float price;
        time_t time;
    };

    class Cinema {
    private:
        string name;
        string db_path;
        fstream fin();
        vector<Movie> movies;

    public:
        Cinema(string name, string db_path);
        void sell_ticket();
        void dumpTickets();
        void addTicket(string title, time_t time, float price);
        void showTickets();
        void saveTickets(vector<Movie> movies_);
        vector<Movie> getTickets(int number);
        Movie getLine(int number, fstream& fin);
    };
}
#endif //LABS_LAB4_PROBLEM3_H
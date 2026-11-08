#include "lab4_problem3.h"
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <utility>
#include <string>
using namespace std;
using namespace lab4_problem3;

void lab4_problem3::run_lab4_problem3() {
    vector<Movie> mvs;
    Cinema* my_cinema = new Cinema("Gorizont", R"(C:\Users\simafrus\CPP\Labs\my_cinema.bin)");
    time_t start_time = time(nullptr);
    my_cinema->addTicket("Shrek", start_time, 100);
    my_cinema->addTicket("Shrek", start_time, 150);
    my_cinema->showTickets();
    my_cinema->dumpTickets();
    mvs = my_cinema->getTickets(0);
    // my_cinema->saveTickets(mvs);
    cout << "Worked!" << endl;
    my_cinema->showTickets();
}

Cinema::Cinema(string name, string db_path) {
    this->name = std::move(name);
    this->db_path = std::move(db_path);
}

void Cinema::dumpTickets() {
    fstream fout(db_path, ios::out | ios::binary);

    int size_m = 0;
    size_m = movies.size();
    fout.write(reinterpret_cast<char*>(&size_m), sizeof(int));

    for (Movie& m: movies) {
        fout.write(reinterpret_cast<const char*>(&m), sizeof(Movie));
    }
    fout.close();
    movies.clear();
}

void Cinema::addTicket(string title, time_t time, float price) {
    bool match = false;
    if (movies.empty()) {
        Movie m;
        m.title = title;
        m.time = time;
        m.price = price;
        movies.push_back(m);
    }
    for (int i=0; i < movies.size(); i++) {
        if (movies[i].title == title && movies[i].time == time) {
            match = true;
            movies[i].count+=1;
            movies[i].price = (movies[i].price + price)/(movies[i].count);
        }
        else if (match == false) {
            Movie m;
            m.title = title;
            m.time = time;
            m.price = price;
            movies.push_back(m);
        }
    }
}

void Cinema::showTickets() {
    cout << endl << "Showing Tickets" << endl;
    for (Movie m: movies) {
        cout << m.title << " in " << m.time << " with " << m.count << endl;
    }
    cout << endl;
}

Movie Cinema::getLine(int number, fstream& fin){
    fin.seekg(sizeof(int)+sizeof(Movie)*number, ios::beg);
    Movie m;
    if (fin.read(reinterpret_cast<char*>(&m), sizeof(Movie))) {
        cout << m.title << " in " << m.time << " with " << m.count << endl;
    }
    else {
        cerr << "Can't read from file" << endl;
    }
    return  m;
}
vector<Movie> Cinema::getTickets(int number = 0) {
    cout << endl << "Getting tickets" << endl;
    fstream fin(db_path, ios::in |ios::binary);

    if (!fin.is_open()) {
        cerr << "Can't open file" << endl;
    }

    int size_m = 0;
    fin.read(reinterpret_cast<char*>(&size_m), sizeof(int));
    cout << "DB size: " << size_m << endl;

    vector<Movie> mvs;
    if (number == 0) {
        for (int i = 0; i < size_m; i++) {
            mvs.push_back(this->getLine(i, fin));
        }
    }

    else {
        mvs.push_back(this->getLine(number, fin));
    }

    this->saveTickets(mvs);

    cout << "Readed: " << mvs.size() << " movies" << endl;
    fin.close();
    cout << "Closed" << endl;
    // this->movies = mvs;
}

void Cinema::saveTickets(vector<Movie> movies_) {
    this->movies = movies_;
}
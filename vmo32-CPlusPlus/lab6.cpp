#include "lab6.h"
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <utility>
#include <string>
using namespace std;
using namespace lab6;

void lab6::run_lab6() {
    cout << "Total automobiles count: " << Automobile::get_automobile_amount() << endl;
    const char* br1 = "MRSD";
    Automobile* a1;
    cout << endl;
    a1 = new Automobile(br1, 150);
    cout << "Total automobiles count: " << Automobile::get_automobile_amount() << endl;
    cout << endl;
    Automobile* a2;
    a2 = create_automobile(200, br1, 20);
    cout << endl;
    a1->buy(945, 14);
    a2->sell(10);
    a2->buy(819, 15);
    cout << endl;
    utilize(*a1);
    utilize(*a2);

}


Automobile::Automobile(const char *br, int pow, float pr): id(++counter), brand(br), power(pow), price(pr), owners_id(0){
    cout << "Automobile number " << id << endl;
}

Automobile::Automobile(int pow, const char *br, float pr): id(++counter), brand(br), power(pow), price(pr), owners_id(0){
    cout << "Automobile number " << id << endl;
}

Automobile::~Automobile() {
    cout << "~Automobile number " << id << " has been destructed" << endl;
}

int Automobile::get_id() {
    return id;
}

int Automobile::get_automobile_amount() {
    return counter;
}

void Automobile::sell(float p) {
    on_sell = true;
    price = p;
}

void Automobile::buy(int owner, float p) {
    if (!on_sell) {
        cout << id << " is not for sale" << endl;
        return;
    }

    if (p < price) {
        cout << "$" << price - p << " more to buy " << id << endl;
        return;
    }

    if (p > price) {
        cout << "$" << p - price << " more than cost" << endl;
    }

    cout << id << " went from " << owners_id << " to " << owner << endl;
    owners_id = owner;
}

Automobile * lab6::create_automobile(int pow, const char *br, float pr) {
    return new Automobile(pow, br, pr);
    // Automobile* a = new Automobile(pow, br, pr);
    // return a;
}

void lab6::utilize(Automobile& automobile) {
    cout << "Automobile number " << automobile.id << " being utilized" << endl;
    delete &automobile;
}

#include "lab8.h"
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <utility>
#include <string>
using namespace std;
using namespace lab8;

void lab8::run_lab8() {
    auto* eu1 = new Euro(100, 99);
    auto* d1 = new Dollar(700, 85);
    auto* p1 = new Pound(30, 120);

    Purse p = Purse();

    p.addCurrency(eu1);
    p.addCurrency(d1);
    p.addCurrency(p1);

    p.seeCurrency();
    p.seeRubles();

    Dollar::setRuble(87);
    p.seeRubles();

    delete d1; delete eu1; delete p1;
}

Currency::Currency(float a): amount(a){};

float Currency::getAmount() {
    return amount;
}

void Dollar::setRuble(float r) {
    ruble = r;
}

void Euro::setRuble(float r) {
    ruble = r;
}

void Pound::setRuble(float r) {
    ruble = r;
}

float Dollar::ruble = 0;
float Euro::ruble = 0;
float Pound::ruble = 0;

char Dollar::getSymbol() {
    return sym;
}

char Euro::getSymbol() {
    return sym;
}

char Pound::getSymbol() {
    return sym;
}

Dollar::Dollar(float a, float r): Currency(a) {setRuble(r);};
Euro::Euro(float a, float r): Currency(a){setRuble(r);};
Pound::Pound(float a, float r): Currency(a){setRuble(r);};

float Dollar::toRuble() {return amount*ruble;}
float Euro::toRuble() {return amount*ruble;}
float Pound::toRuble() {return amount*ruble;}

Purse::Purse() {
    currencies = new vector<Currency*>();
}

Purse::~Purse() {
    for (auto c : *currencies) {
        delete c;
    }
    delete currencies;
}


void Purse::addCurrency(Currency *c) {
    currencies->push_back(c);
}

void Purse::seeCurrency() {
    for (Currency *c : *currencies) {
        cout << c->getSymbol() << c->getAmount() << endl;
    }
}

void Purse::seeRubles() {
    float rub = 0;
    for (Currency *c : *currencies) {
        rub += c->toRuble();
    }
    cout << rub << " rubles" << endl;
}


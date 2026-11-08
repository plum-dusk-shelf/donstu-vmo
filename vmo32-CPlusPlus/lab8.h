#include <string>
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <vector>
using namespace std;

/*
Базовый абстрактный класс должен содержать как абстрактные методы, так и
неабстрактные, в общей сложности не менее 3 методов, если в задании указано
меньшее количество методов, то недостающие придумываем самостоятельно.
Производные классы могут содержать дополнительные методы согласно
заданию и/или вашей фантазии.
Коллекция объектов классов должна иметь в себе представителей от каждого
класса.

11 Создать абстрактный класс Currency для работы с денежными суммами. Определить в
нем методы перевода в рубли и вывода на экран. На его основе реализовать классы
Dollar, Euro и Pound (фунт стерлингов) с возможностью пересчета в центы и пенсы
соответственно.
*Создать класс Purse (кошелек), содержащий массив/параметризованную коллекцию
объектов этих классов в динамической памяти. Предусмотреть возможность вывода
общей суммы, переведенной в рубли, и суммы по каждой из валют. Написать
демонстрационную программу, в которой будут использоваться все методы классов.
*/

#ifndef LABS_LAB8_H
#define LABS_LAB8_H

namespace lab8 {
    void run_lab8();

    class Currency {
    protected:
        float amount;
        char sym = ' ';
    public:
        Currency(float a);
        virtual ~Currency()=default;
        virtual float getAmount();
        virtual float toRuble() = 0;
        virtual char getSymbol() = 0;
    };

    class Dollar: public Currency {
    protected:
        static float ruble;
        char sym = '$';
    public:
        Dollar(float a, float r);
        ~Dollar()=default;
        static void setRuble(float r);
        float toRuble() override;
        char getSymbol() override;
    };
    class Euro: public Currency {
    protected:
        static float ruble;
        char sym = 'E';
    public:
        Euro(float a, float r);
        ~Euro()=default;
        float toRuble() override;
        char getSymbol() override;
        static void setRuble(float r);
    };
    class Pound: public Currency {
    protected:
        static float ruble;
        char sym = 'P';
    public:
        Pound(float a, float r);
        float toRuble() override;
        char getSymbol() override;
        static void setRuble(float r);
        ~Pound()=default;
    };

    class Purse {
    private:
        vector<Currency*>* currencies;
    public:
        Purse();
        ~Purse();
        void addCurrency(Currency* c);
        void seeCurrency();
        void seeRubles();
    };
}

#endif //LABS_LAB8_H
#include <string>
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
using namespace std;

/*
Создать класс согласно варианту (таблица 1). Класс должен содержать поля,
конструктор, методы (которые указаны в варианте, также можно реализовать
собственные методы). Скрыть поля и часть методов. Продемонстрировать работу
класса.
Добавить в класс счетчик созданных объектов на основе статического поля.
Напишите программу-тест, в которой проверяется, сколько объектов класса создано
при входе в функцию main, после статического создания массива объектов, после
динамического создания объекта, после удаления динамического объекта.
Создайте класс с закрытыми конструкторами и деструктором. Реализуйте
методы для создания и уничтожения объектов класса. Напишите программу-тест.
Создайте класс с закрытыми конструкторами и деструктором. Реализуйте
внешние функции для создания и уничтожения объектов класса. Напишите
программу-тест.
Реализовать для класса дружественную функцию и продемонстрировать
принцип работы с ней.
*/

#ifndef LABS_LAB5_H
#define LABS_LAB6_H


namespace lab6 {
    void run_lab6();

    class Automobile {
        private:
        inline static int counter = 0;
        const int id;
        float price = 0;
        int owners_id;
        bool on_sell = false;
        Automobile(int pow, const char* br, float pr = 0);

        public:
        const char* brand;
        const int power;

        Automobile(const char* br, int pow, float pr = 0);
        ~Automobile();

        int get_id();
        static int get_automobile_amount();
        void buy(int owner, float p);
        void sell(float p);
        friend void utilize(Automobile& automobile);
        friend Automobile * create_automobile(int pow, const char* br, float pr);
    };

    void utilize(Automobile& automobile);
    Automobile * create_automobile(int pow, const char *br, float pr);


}
#endif //LABS_LAB6_H
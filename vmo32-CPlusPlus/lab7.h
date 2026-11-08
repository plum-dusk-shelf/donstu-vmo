#include <string>
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <vector>
using namespace std;

/*
Описать класс(ы), реализующий хранение требуемой в соответствие с заданием
информации. Определить инкапсуляцию для полей (private или public). Для закрытых
полей реализовать методы get и set. В классе должно быть реализовано несколько
конструкторов и конструктор копирования. В классе должно быть реализовано
несколько методов. Описать класс, одним из полей которого является коллекция
(массив, вектор, список) объектов согласно выбранному варианту.
Для класса с коллекцией переопределить операцию индексации. Для исходного
класса перегрузить операцию вывода на экран, операцию присвоения.
Придумать варианты перегрузки операции сравнения, арифметических
операций (как с числом, так и с объектом класса).
Написать программу тест, демонстрирующую использование перегруженных
операций.
*/

#ifndef LABS_LAB7_H
#define LABS_LAB7_H

namespace lab7 {
    class Bank;

    void run_lab7();

    class Account {
        private:
        // Fields
        const string accountId;
        float APR = 0;
        string FIO;
        string pasport;
        Bank* bank;
        float total_income = 0, total_outcome = 0;
        // Constructors
        Account(Bank* this_bank, string& fio, string& p);

        public:
        // Constructors
        Account(const Account& a);
        // Funcs
        string getAccountId();
        void setAPR(float apr);
        float getAPR();
        void addIncome(float amount);
        void getWithdraw(float amount);
        float getBalance();
        string getHolder();
        ~Account();
        // Operators
        Account& operator= (const Account& a);
        bool operator< (const Account& a);
        bool operator== (const Account* a);
        bool operator> (const Account& a);
        bool operator< (const int& i);
        bool operator== (const int& i);
        bool operator> (const int& i);
        // Friends
        friend class Bank;
    };

    class Bank {
        private:
        inline static int counter = 0;
        vector<Account*> accounts;

        public:
        // Fields
        const int IDLength = 12;
        string bankName;
        // Constructors
        Bank(string bn);
        Bank(string bn, int idl);
        ~Bank();
        // Funcs
        Account* newAccount(string fio, string p);
        Account* getAccountByID(string accountID);
        string makeNewID();
        void removeAccount(string aid);
        void showBank();
        void showBankDeposits();
        vector<Account*> whoGets(int apr);
        // Operators
        Account* operator[](const string& index);
    };

    ostream& operator<< (ostream& os, Account* a);
}

#endif //LABS_LAB7_H
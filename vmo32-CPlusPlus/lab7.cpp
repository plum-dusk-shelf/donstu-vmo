#include "lab7.h"
#include <iostream>
#include <ostream>
#include <iomanip>
#include <fstream>
#include <utility>
#include <string>
using namespace std;
using namespace lab7;

void lab7::run_lab7() {
    Bank* bank1;
    bank1 = new Bank("T", 4);

    Account* a1;
    a1 = bank1->newAccount("FIO", "pasport");
    Account* a2 = bank1->newAccount("FIO", "pasport");
    a2->setAPR(10);
    cout << "APR on second account = " << a2->getAPR() << endl;
    Account* a3;
    a3 = bank1->newAccount("FIO2", "pasport2");
    Account* a4;
    a4 = bank1->newAccount("FIO2", "pasport2");

    a1->addIncome(1);
    a2->addIncome(2);
    a3->addIncome(3);
    a4->addIncome(4);
    a3->getWithdraw(2);

    cout << a3 << endl;
    cout << (*bank1)[a4->getAccountId()] << endl;

    cout << "Gets 0:\t";
    for (auto& account : bank1->whoGets(0)) {
        cout << "#" << account->getAccountId() << ";\t";
    }
    cout << endl;

    cout << "a1 == a2 is " << (a1 == a2) << endl;
    cout << "a2 == a2 is " << (a2 == a2) << endl;

    bank1->showBank();
    bank1->removeAccount(a3->getAccountId());
    bank1->showBank();

    bank1->showBankDeposits();

    Bank* bank2;
    bank2 = new Bank("Sber");

    delete bank1, bank2, a1,a2,a3,a4;
}

Account::Account(Bank* this_bank, string& fio, string& p): accountId(this_bank->makeNewID()), FIO(fio), pasport(p), bank(this_bank) {
    cout << "Account #" << getAccountId() << " successfuly created" << endl;
}

string Account::getAccountId() {
    return accountId;
}

Account::Account(const Account& a): accountId(a.accountId), FIO(a.FIO), pasport(a.pasport), bank(a.bank) {
    // cout << "Account #" << a.accountId <<  " successfuly copied to #" << getAccountId() << endl;
}

void Account::setAPR(float apr) {
    APR = apr;
}

float Account::getAPR() {
    return APR;
}

void Account::addIncome(float amount) {
    total_income += amount;
}

void Account::getWithdraw(float amount) {
    total_outcome += amount;
}

float Account::getBalance() {
    return total_income-total_outcome;
}

string Account::getHolder() {
    return FIO;
}

Account & Account::operator=(const Account &a){
    FIO = a.FIO;
    pasport = a.pasport;
    bank = a.bank;
    return *this;
}

bool Account::operator==(const Account *a) {
    if (pasport != a->pasport && accountId != a->accountId) {
        return true;
    }
    return false;
}

Bank::Bank(string bn): bankName(bn) {
    cout << bankName << "-Bank has been created" << endl;
}

Bank::Bank(string bn, int idl): bankName(bn), IDLength(idl) {
    cout << bankName << "-Bank has been created" << endl;
}

Account* Bank::newAccount(string fio, string p) {
    Account* ac;
    string id;
    ac = new Account(this, fio, p);
    // cout << 1 << endl;
    accounts.push_back(ac);
    // cout << 2 << endl;
    return ac;
}


string Bank::makeNewID() {
    std::ostringstream os;
    os << std::setfill('0') << std::setw(IDLength) << ++counter;
    return os.str();
}

void Bank::showBank() {
    for (auto& account : accounts) {
        cout << "#" << account->getAccountId() << ";\t";
    }
    cout << endl;
}

void Bank::removeAccount(string aid) {
    for (int a=0; a<accounts.size(); a++) {
        if (aid == accounts[a]->getAccountId()) {
            accounts.erase(accounts.begin() + a);
        }
    }
    cout << "#" << aid << " removed" << endl;
}

void Bank::showBankDeposits() {
    float sum = 0;
    for (auto& account : accounts) {
        sum += account->getBalance();
    }
    cout << bankName << "-Bank has $" << sum << endl;
}

vector<Account *> Bank::whoGets(int apr) {
    vector<Account*> whoGets;
    for (auto& account : accounts) {
        if (account->getAPR() == apr){
            whoGets.push_back(account);
        }
    }
    return whoGets;
}

Account * Bank::operator[](const string& index) {
    for (auto& account : accounts) {
        if (account->getAccountId() == index) {
            return account;
        }
    }
    throw std::out_of_range("Account not found");
}

Bank::~Bank() { cout << bankName << " deleted" << endl; }

ostream & lab7::operator<<(ostream &os, Account* a) {
    os << "Account #" << a->getAccountId() << " with $" << a->getBalance() << " belongs to " << a->getHolder();
    return os;
}

Account::~Account() { cout << "#" << getAccountId() << " deleted" << endl; }

class BankAccount:
    bank = 'GasAgricultureNikelAeroRusSouthBank'

    def __init__(self, holder: str, percents_amount, summ=0):
        self.name_passport = holder
        self.incomes = 0
        self.summ = summ
        self.percents_amount = percents_amount

    def add_income(self, income):
        self.incomes += income
        self.summ += income

    def return_info(self):
        return self.name_passport, self.incomes, self.summ, self.percents_amount


first_holder = 'Икар Расвойтов 6013 345418'
second_holder = 'Мойше Абрамович 6006 228420'

debt1 = BankAccount(first_holder, 15, 1000)
debt2 = BankAccount(second_holder, 21, 80000)
debt3 = BankAccount(second_holder, 11, 1500000)
debts = [debt1, debt2, debt3]

debt1.add_income(14000)

availible_bank_money = 0
specified_percent = int(input('Введите эталонный процент: '))
for debt in debts:
    availible_bank_money += debt.summ
    if debt.percents_amount < specified_percent:
        print(f'{debt.name_passport} получает {debt.percents_amount}%')

print(availible_bank_money)

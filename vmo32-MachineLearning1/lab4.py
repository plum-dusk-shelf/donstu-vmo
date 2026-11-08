# apriori_for_online_retail.py
# Реализация Apriori без OOP и без внешних библиотек (только pandas + stdlib).
# Ожидается, что на вход подаётся pandas.DataFrame с колонками:
#   InvoiceNo  (идентификатор транзакции)
#   Description (название товара)
# Опционально: Quantity — для отбраковки возвратов (Quantity <= 0).
#
# Пример использования:
# df = pd.read_csv("OnlineRetail.csv", encoding="latin1")
# transactions = get_transactions(df, item_col="Description", trans_col="InvoiceNo", quantity_col="Quantity")
# freq_itemsets = apriori(transactions, min_support=0.02)   # min_support — доля (0..1)
# rules = generate_and_print_rules(freq_itemsets, min_confidence=0.6)

import pandas as pd
from itertools import combinations, chain
from collections import defaultdict


def get_transactions(df, item_col='Description', trans_col='InvoiceNo', quantity_col=None, dropna=True):
    """
    Преобразует DataFrame в список транзакций (каждая транзакция — множество товаров).
    Отбрасывает пустые описания. Если указан quantity_col, отбрасывает строки с quantity <= 0.
    Возвращает список множеств и общее число транзакций.
    """
    df = df.copy()
    if dropna:
        df = df[df[item_col].notna()]
    if quantity_col is not None and quantity_col in df.columns:
        df = df[df[quantity_col] > 0]
    # Приведём описания к строкам и уберём лишние пробелы
    df[item_col] = df[item_col].astype(str).str.strip()
    grouped = df.groupby(trans_col)[item_col].apply(lambda items: set(items.tolist()))
    transactions = [t for t in grouped.tolist() if len(t) > 0]
    return transactions


def _count_single_items(transactions):
    counts = defaultdict(int)
    for t in transactions:
        for item in t:
            counts[frozenset([item])] += 1
    return counts


def _support(count, n_transactions):
    return count / n_transactions


def apriori(transactions, min_support=0.01):
    """
    Classic Apriori:
    - transactions: list of sets (items)
    - min_support: минимальная поддержка в долях (0..1)
    Возвращает:
      freq_itemsets: dict {frozenset(items): support_fraction}
    """
    n_trans = len(transactions)
    min_count = max(1, int(min_support * n_trans))  # целочисленный порог для подсчёта

    # L1
    item_counts = _count_single_items(transactions)
    L = {itemset: count for itemset, count in item_counts.items() if count >= min_count}
    freq_itemsets = {k: v / n_trans for k, v in L.items()}  # сохраняем в долях

    k = 2
    prev_L_itemsets = set(L.keys())
    while prev_L_itemsets:
        # Генерация кандидатов: все объединения двух предыдущих множест размер k
        candidate_sets = set()
        prev_itemsets_list = list(prev_L_itemsets)
        for i in range(len(prev_itemsets_list)):
            for j in range(i + 1, len(prev_itemsets_list)):
                union = prev_itemsets_list[i] | prev_itemsets_list[j]
                if len(union) == k:
                    # Пруннинг: все (k-1)-подмножества должны быть частыми
                    all_subsets_frequent = True
                    for subset in combinations(union, k - 1):
                        if frozenset(subset) not in prev_L_itemsets:
                            all_subsets_frequent = False
                            break
                    if all_subsets_frequent:
                        candidate_sets.add(union)
        if not candidate_sets:
            break

        # Подсчёт поддержки кандидатов
        candidate_counts = defaultdict(int)
        for t in transactions:
            for cand in candidate_sets:
                if cand.issubset(t):
                    candidate_counts[cand] += 1

        # Оставляем только те, у кого count >= min_count
        new_L = {cand: cnt for cand, cnt in candidate_counts.items() if cnt >= min_count}
        # Добавляем в общий список частых
        for kset, cnt in new_L.items():
            freq_itemsets[frozenset(kset)] = cnt / n_trans

        prev_L_itemsets = set(new_L.keys())
        k += 1

    return freq_itemsets


def generate_and_print_rules(freq_itemsets, min_confidence=0.5, n_transactions=None):
    # Поддержки уже даны в долях
    supports = freq_itemsets  # имя для понятности
    # вычислим минимальную (мин.кандидатную) поддержку среди найденных itemset'ов
    if supports:
        min_supp_found = min(supports.values())
    else:
        min_supp_found = 0.0

    long_amount = len([_ for _ in supports.keys() if len(_) > 1])
    print(f"Найдено частых наборов: {len(supports)}({long_amount} — длиной > 1). Минимальная поддержка среди них = {min_supp_found:.6f}")
    print(f"Порог минимальной достоверности (confidence) = {min_confidence:.3f}")
    print("-" * 80)
    rules = []
    # Для каждого частого набора размер >=2 генерируем правила
    for itemset, supp_itemset in supports.items():
        if len(itemset) < 2:
            continue
        items = list(itemset)
        # перечисляем все непустые подмножества (кроме самого itemset)
        # но разумно перебирать только непустые proper subsets
        for r in range(1, len(items)):
            for antecedent_tuple in combinations(items, r):
                antecedent = frozenset(antecedent_tuple)
                consequent = itemset - antecedent
                if not consequent:
                    continue
                supp_antecedent = supports.get(antecedent, 0.0)
                supp_consequent = supports.get(consequent, 0.0)
                if supp_antecedent == 0:
                    continue  # защита от деления на ноль
                confidence = supp_itemset / supp_antecedent
                # lift = confidence / support(consequent)
                if supp_consequent == 0:
                    lift = float('inf')
                else:
                    lift = confidence / supp_consequent
                if confidence >= min_confidence:
                    rules.append((antecedent, consequent, supp_itemset, confidence, lift))
    # Сортируем правила по убыванию lift (или по confidence — можно изменить)
    rules.sort(key=lambda x: (x[4], x[3]), reverse=True)
    if not rules:
        print("Правил, удовлетворяющих порогу confidence, не найдено.")
    else:
        print(f"Найдено правил: {len(rules)} (отсортировано по lift).")
        for ant, cons, supp, conf, lift in rules:
            ant_str = ", ".join(sorted(list(ant)))
            cons_str = ", ".join(sorted(list(cons)))
            print(f"{ant_str}  ->  {cons_str}")
            print(f"    support(itemset) = {supp:.6f}, confidence = {conf:.4f}, lift = {lift:.4f}")
    print("-" * 80)
    return rules


# --- Дополнительные полезные утилиты ---

def top_n_itemsets(freq_itemsets, n=20):
    """Вернуть top-n частых наборов по поддержке (descending)."""
    return sorted(freq_itemsets.items(), key=lambda x: x[1], reverse=True)[:n]


# ------------------------------
# Пример: как использовать весь набор функций
if __name__ == "__main__":
    df = pd.read_csv("online_retail_II.csv", encoding="latin1").iloc[:5000]
    df = df.drop(columns=['Description', 'Country', ])
    transactions = get_transactions(df, item_col="StockCode", trans_col="Invoice", quantity_col="Quantity")
    # Задаём пороги (пример)
    min_support = 0.02
    min_confidence = 0.07
    freq_itemsets = apriori(transactions, min_support=min_support)
    # Печать самых частых наборов
    print("Top frequent itemsets:")
    for iset, sup in top_n_itemsets(freq_itemsets, n=1000):
        print(f"{set(iset)} : support = {sup:.2f}")
    # Генерация и печать правил
    rules = generate_and_print_rules(freq_itemsets, min_confidence=min_confidence)
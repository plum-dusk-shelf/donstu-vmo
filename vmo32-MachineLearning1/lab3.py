# c45_from_pandas.py
# Реализация C4.5 (процедурная, без ООП) для pandas.DataFrame
# Автор: (пример). Работает с pandas.DataFrame.
# Поддерживает числовые и категориальные признаки. Результат: вложенный dict-дерево + predict.

import math
from collections import Counter
import pandas as pd

# -----------------------
# Вспомогательные функции
# -----------------------

def entropy_from_counts(counts):
    """Shannon entropy from iterable of counts."""
    total = sum(counts)
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        ent -= p * math.log2(p)
    return ent

def class_counts(series):
    """Возвращает Counter меток целевой переменной (series)."""
    return Counter(series)

def dataset_entropy(df, target_col):
    """Entropy of target in df."""
    cnt = class_counts(df[target_col])
    return entropy_from_counts(cnt.values())

# -----------------------
# Разбиение и пороги
# -----------------------

def possible_splits_numeric(series):
    """
    Для числовой серии (pandas.Series) возвращает список возможных порогов.
    Порог — среднее между соседними уникальными отсортированными значениями.
    """
    vals = series.dropna().unique()
    if len(vals) <= 1:
        return []
    vals = sorted(vals)
    splits = []
    for i in range(len(vals) - 1):
        splits.append((vals[i] + vals[i+1]) / 2.0)
    return splits

def split_dataframe(df, attribute, threshold=None):
    """
    Если threshold is None -> считаем категориальным: возвращаем dict value -> sub-DataFrame
    Если threshold задан -> считаем числовым: возвращаем dict with keys 'le' and 'gt'
    """
    if threshold is None:
        groups = {}
        for val, sub in df.groupby(df[attribute]):
            groups[val] = sub.copy()
        return groups
    else:
        left = df[df[attribute].astype(float) <= threshold].copy()
        right = df[df[attribute].astype(float) > threshold].copy()
        return {'le': left, 'gt': right}

# -----------------------
# Информация о разбиениях
# -----------------------

def split_info(subsets, total_count):
    """Split info: -sum((|Si|/|S|)*log2(|Si|/|S|))"""
    if total_count == 0:
        return 0.0
    parts = []
    for s in subsets:
        size = len(s)
        if size == 0:
            continue
        ratio = size / total_count
        parts.append(-ratio * math.log2(ratio))
    return sum(parts)

def information_gain(parent_entropy, subsets, total_count, target_col):
    """
    parent_entropy: entropy of parent
    subsets: list of DataFrames (partitions)
    """
    weighted_entropy = 0.0
    for s in subsets:
        if len(s) == 0:
            continue
        weighted_entropy += (len(s) / total_count) * dataset_entropy(s, target_col)
    return parent_entropy - weighted_entropy

# -----------------------
# Выбор лучшего атрибута
# -----------------------

def best_split_for_attribute(df, attribute, target_col):
    """
    Возвращает лучшую информацию о разбиении по одному атрибуту.
    Для числового: перебирает пороги, выбирает порог с максимальным gain ratio.
    Для категориального: делает split by value.
    Возвращаемая структура:
    {
      'attribute': attribute,
      'is_numeric': True/False,
      'threshold': best_threshold or None,
      'gain': best_gain,
      'gain_ratio': best_gain_ratio,
      'subsets': dict (как в split_dataframe для этого разбиения)
    }
    """
    total_count = len(df)
    parent_entropy = dataset_entropy(df, target_col)

    # Если все метки одинаковы — нет смысла
    if parent_entropy == 0:
        return None

    # Проверка типа: попробуем преобразовать в числовой
    series = df[attribute]
    is_numeric = pd.api.types.is_numeric_dtype(series)

    best = None

    if is_numeric:
        # перебор порогов
        splits = possible_splits_numeric(series)
        if not splits:
            return None
        best_gain_ratio = -1e9
        best_threshold = None
        best_subsets = None
        best_gain = None

        for thr in splits:
            parts = split_dataframe(df, attribute, threshold=thr)
            subsets = list(parts.values())
            gain = information_gain(parent_entropy, subsets, total_count, target_col)
            si = split_info(subsets, total_count)
            gain_ratio = gain / si if si > 0 else 0.0
            if gain_ratio > best_gain_ratio:
                best_gain_ratio = gain_ratio
                best_threshold = thr
                best_subsets = parts
                best_gain = gain

        if best_threshold is None:
            return None
        return {
            'attribute': attribute,
            'is_numeric': True,
            'threshold': best_threshold,
            'gain': best_gain,
            'gain_ratio': best_gain_ratio,
            'subsets': best_subsets
        }

    else:
        # категориальный
        parts = split_dataframe(df, attribute, threshold=None)
        subsets = list(parts.values())
        gain = information_gain(parent_entropy, subsets, total_count, target_col)
        si = split_info(subsets, total_count)
        gain_ratio = gain / si if si > 0 else 0.0
        return {
            'attribute': attribute,
            'is_numeric': False,
            'threshold': None,
            'gain': gain,
            'gain_ratio': gain_ratio,
            'subsets': parts
        }

def choose_best_attribute(df, attributes, target_col, min_gain_ratio=1e-6):
    """
    Перебирает атрибуты и возвращает лучшее разбиение (best_split_for_attribute)
    Возвращает None, если ни один атрибут не даёт значимого прироста.
    """
    best = None
    for attr in attributes:
        split_info_attr = best_split_for_attribute(df, attr, target_col)
        if split_info_attr is None:
            continue
        if best is None or split_info_attr['gain_ratio'] > best['gain_ratio']:
            best = split_info_attr
    if best is None:
        return None
    if best['gain_ratio'] < min_gain_ratio:
        return None
    return best

# -----------------------
# Построение дерева
# -----------------------

def majority_class(series):
    """Возвращает наиболее частую метку (строку) в series."""
    cnt = class_counts(series)
    return cnt.most_common(1)[0][0]

def build_tree(df, attributes, target_col, max_depth=None, min_samples_split=2, depth=0):
    """
    Рекурсивная функция построения дерева.
    Возвращает дерево в виде вложенных словарей:
    Лист:
      {'type': 'leaf', 'class': chosen_class, 'samples': n}
    Узел (числовой):
      {
        'type': 'node',
        'attribute': attr,
        'is_numeric': True,
        'threshold': thr,
        'samples': n,
        'branches': {'le': subtree, 'gt': subtree}
      }
    Узел (категориальный):
      {
        'type': 'node',
        'attribute': attr,
        'is_numeric': False,
        'samples': n,
        'branches': {value1: subtree, value2: subtree, ...}
      }
    """
    # Базовые случаи
    if len(df) == 0:
        return {'type': 'leaf', 'class': None, 'samples': 0}
    labels = df[target_col]
    if len(set(labels)) == 1:
        return {'type': 'leaf', 'class': labels.iloc[0], 'samples': len(df)}
    if not attributes or (max_depth is not None and depth >= max_depth) or len(df) < min_samples_split:
        return {'type': 'leaf', 'class': majority_class(labels), 'samples': len(df)}

    # Выбор лучшего атрибута
    best = choose_best_attribute(df, attributes, target_col)
    if best is None:
        return {'type': 'leaf', 'class': majority_class(labels), 'samples': len(df)}

    attr = best['attribute']
    node = {
        'type': 'node',
        'attribute': attr,
        'is_numeric': best['is_numeric'],
        'samples': len(df),
        'gain': best['gain'],
        'gain_ratio': best['gain_ratio'],
        'branches': {}
    }

    if best['is_numeric']:
        thr = best['threshold']
        node['threshold'] = thr
        parts = best['subsets']
        # для каждой ветки рекурсивно строим поддерево
        for key in ('le', 'gt'):
            sub = parts.get(key)
            if sub is None or len(sub) == 0:
                node['branches'][key] = {'type': 'leaf', 'class': majority_class(labels), 'samples': 0}
            else:
                # attributes остаются те же (для C4.5 категории остаются доступными)
                node['branches'][key] = build_tree(sub, attributes, target_col, max_depth, min_samples_split, depth+1)
    else:
        parts = best['subsets']
        # для категориального — удаляем этот атрибут из списка признаков (чтобы избежать повторного разбиения по нему)
        new_attributes = [a for a in attributes if a != attr]
        for val, sub in parts.items():
            if sub is None or len(sub) == 0:
                node['branches'][val] = {'type': 'leaf', 'class': majority_class(labels), 'samples': 0}
            else:
                node['branches'][val] = build_tree(sub, new_attributes, target_col, max_depth, min_samples_split, depth+1)

    return node

# -----------------------
# Прогноз (predict)
# -----------------------

def predict_row(tree, row):
    """Прогноз для одной строки (pandas.Series) по дереву."""
    node = tree
    while True:
        if node is None:
            return None
        if node.get('type') == 'leaf':
            return node.get('class')
        attr = node['attribute']
        if node.get('is_numeric'):
            thr = node.get('threshold')
            try:
                val = float(row[attr])
            except Exception:
                # при пропуске — вернуть наиболее частый класс поддерева (approx: choose 'le' branch majority)
                # просто выбираем ветку с большим количеством samples
                b = node['branches']
                # если обе ветки есть, берём ту с большим samples
                left = b.get('le')
                right = b.get('gt')
                if left is None:
                    node = right
                elif right is None:
                    node = left
                else:
                    if left.get('samples',0) >= right.get('samples',0):
                        node = left
                    else:
                        node = right
                continue
            if val <= thr:
                node = node['branches'].get('le')
            else:
                node = node['branches'].get('gt')
        else:
            val = row.get(attr)
            # если значение встретилось в ветках — идём туда, иначе попытка использовать default (majority)
            branches = node['branches']
            if val in branches:
                node = branches[val]
            else:
                # нет такой ветки — выбираем ветку с наибольшим количества образцов
                best_branch = None
                best_samples = -1
                for k, b in branches.items():
                    s = b.get('samples', 0)
                    if s > best_samples:
                        best_samples = s
                        best_branch = b
                node = best_branch

def predict(tree, df):
    """Прогноз для DataFrame: возвращает список предсказаний в том же порядке."""
    preds = []
    for _, row in df.iterrows():
        preds.append(predict_row(tree, row))
    return preds

# -----------------------
# Утилиты вывода дерева (читаемый формат)
# -----------------------

def pprint_tree(node, indent=0):
    """Печатает дерево в читабельном виде."""
    pad = '  ' * indent
    if node.get('type') == 'leaf':
        print(f"{pad}Leaf: class={node.get('class')} (samples={node.get('samples')})")
        return
    attr = node.get('attribute')
    if node.get('is_numeric'):
        thr = node.get('threshold')
        print(f"{pad}Node: {attr} <= {thr:.6g} ? (samples={node.get('samples')}, gain_ratio={node.get('gain_ratio'):.6g})")
        pprint_tree(node['branches'].get('le'), indent+1)
        print(f"{pad}Else ({attr} > {thr:.6g}):")
        pprint_tree(node['branches'].get('gt'), indent+1)
    else:
        print(f"{pad}Node: {attr} (categorical) (samples={node.get('samples')}, gain_ratio={node.get('gain_ratio'):.6g})")
        for val, branch in node['branches'].items():
            print(f"{pad} If {attr} == {val}:")
            pprint_tree(branch, indent+1)

def calculate_accuracy(predictions, target):
    length = len(predictions)
    return sum([predictions[i] == target[i] for i in range(length)])/length

def split_dataset(data: pd.DataFrame, border: int, target):
    classes = data[target].unique().tolist()
    border = border//2
    return pd.merge(data[data['Class'] == classes[0]].iloc[:border], data[data['Class']==classes[1]].iloc[:border]), pd.merge(data[['Class']==classes[0]].iloc[border:], data[data["Class"] == classes[1]].iloc[border:])

# -----------------------

if __name__ == '__main__':
    df = pd.read_csv('Raisin_Dataset.csv')
    target = 'Class'
    (df_train, df_test) = split_dataset(df, 810, target)

    features = [c for c in df.columns if c != target]

    tree = build_tree(df, features, target_col=target, max_depth=5, min_samples_split=1)
    print("Построенное дерево:")
    pprint_tree(tree)

    print("\nПредсказание для тестового набора:")
    preds = predict(tree, df_test)
    print(f'Accuracy: {calculate_accuracy(preds, df_test[target].tolist()):.2%}')


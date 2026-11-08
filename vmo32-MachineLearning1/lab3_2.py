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
    border = border//2
    classes = data[target].unique().tolist()
    data_tuple = []
    for c in classes:
        data_tuple.append(data[data[target] == c])
    return pd.concat([d.iloc[:border] for d in data_tuple], axis=0), pd.concat([d.iloc[border:] for d in data_tuple], axis=0)

import math
import copy
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree

def visualize_nested_tree_sklearn(tree_dict,
                                  feature_names=None,
                                  class_names=None,
                                  samples_per_leaf=10,
                                  eps=1e-3,
                                  figsize=(14,8),
                                  show=True):
    """
    Визуализация вложенного словарного дерева через sklearn.
    Параметры:
      tree_dict        - дерево в формате, описанном пользователем
      feature_names    - опционально: список имён признаков (если None — соберём из дерева)
      class_names      - опционально: список/мэппинг классов (если None — соберём из листьев)
      samples_per_leaf - сколько одинаковых примеров генерировать для каждого листа
      eps              - маленькая величина для отделения интервалов
      figsize          - размер рисунка matplotlib
      show             - если True — вызовет plt.show(); иначе вернёт (clf, X, y, fig, ax)
    Возвращает:
      если show==False: (clf, X_df, y_array, fig, ax)
    """
    # --- вспомогательные функции ---
    def collect_feature_info(node, feat_types):
        """Собрать имена признаков и типы (is_numeric) рекурсивно."""
        if node['type'] == 'leaf':
            return
        # node
        attr = node['attribute']
        is_num = node['is_numeric']
        feat_types[attr] = is_num
        branches = node['branches']
        if is_num:
            # numeric has two branches likely 'le' and 'gt'
            for k in branches:
                collect_feature_info(branches[k], feat_types)
        else:
            for val in branches:
                collect_feature_info(branches[val], feat_types)

    def gather_leaf_constraints(node, current_constraints, leaves):
        """
        Пройти по дереву. current_constraints: dict attr -> constraint.
        Для числовых: (low, high) (inclusive bounds we'll treat as open with eps)
        Для категориальных: set of allowed values (should be single value per path)
        Добавляет tuples (constraints_copy, leaf_class, leaf_samples_count) в leaves.
        """
        if node['type'] == 'leaf':
            leaves.append((copy.deepcopy(current_constraints),
                           node.get('class', node.get('chosen_class', None)),
                           node.get('samples', None)))
            return

        attr = node['attribute']
        is_num = node['is_numeric']
        branches = node['branches']

        if is_num:
            thr = node['threshold']
            # branch keys expected 'le' and 'gt' (but be flexible)
            for bkey, subtree in branches.items():
                # copy constraints for branch
                new_c = copy.deepcopy(current_constraints)
                low, high = new_c.get(attr, (-math.inf, math.inf))
                if bkey.lower() in ('le','<=','l','leq'):
                    # <= thr -> upper bound = min(high, thr)
                    high = min(high, thr)
                elif bkey.lower() in ('gt','>'):
                    low = max(low, thr)
                else:
                    # если непонятный ключ, попытаемся понять по наличию 'le'/'gt'
                    if bkey == 'le':
                        high = min(high, thr)
                    elif bkey == 'gt':
                        low = max(low, thr)
                    else:
                        # если ключ — значение (редко), игнорируем
                        pass
                new_c[attr] = (low, high)
                gather_leaf_constraints(subtree, new_c, leaves)
        else:
            # categorical: branch key is categorical value
            for bkey, subtree in branches.items():
                new_c = copy.deepcopy(current_constraints)
                # set categorical fixed value (if conflict -> will raise later)
                existing = new_c.get(attr, None)
                if existing is None:
                    new_c[attr] = ('cat', bkey)
                else:
                    # если уже установлен и отличается — конфликт
                    if existing != ('cat', bkey):
                        raise ValueError(f"Conflict on categorical {attr}: {existing} vs {bkey}")
                gather_leaf_constraints(subtree, new_c, leaves)

    # --- main ---
    # 1) соберём признаки и их типы
    feat_types = {}
    collect_feature_info(tree_dict, feat_types)
    if feature_names is None:
        feature_names = list(feat_types.keys())
    else:
        # если передали feature_names, дополним типы неизвестным (по умолчанию numeric)
        for fn in feature_names:
            if fn not in feat_types:
                feat_types[fn] = True  # предполагаем числовой, если неизвестно

    # 2) собрать все листья с набором ограничений
    leaves = []
    gather_leaf_constraints(tree_dict, {}, leaves)
    if len(leaves) == 0:
        raise ValueError("Ветка дерева не содержит листьев?")

    # 3) для категориальных признаков собрать набор значений, чтобы закодировать в ints
    cat_values = defaultdict(set)
    for constraints, leaf_class, _ in leaves:
        for attr, val in constraints.items():
            if isinstance(val, tuple) and val[0] == 'cat':
                cat_values[attr].add(val[1])
    # ensure each categorical attr has at least one known value; if not, we'll invent one
    for attr, is_num in feat_types.items():
        if not is_num and attr not in cat_values:
            cat_values[attr].add("__UNKNOWN__")

    # 4) построить для каждого листа одно пригодное значение признаков (вписываем в интервалы)
    X_rows = []
    y = []
    for constraints, leaf_class, samples_count in leaves:
        # compute single example satisfying all constraints
        row = {}
        for attr in feature_names:
            is_num = feat_types.get(attr, True)
            if is_num:
                # default interval
                low, high = constraints.get(attr, (-1e6, 1e6))
                # if low == -inf or high == inf, replace by wide finite bounds
                if low == -math.inf:
                    low = -1e6
                if high == math.inf:
                    high = 1e6
                # To satisfy inequalities we must pick value strictly inside (consider eps)
                # For safety, shrink bounds by eps
                if low + eps > high - eps:
                    # нельзя подобрать — попробуем relax eps
                    val = (low + high) / 2.0
                else:
                    val = (low + high) / 2.0
                row[attr] = float(val)
            else:
                # categorical
                cinfo = constraints.get(attr, None)
                if cinfo is None:
                    # assign some known category (first)
                    chosen = next(iter(cat_values[attr]))
                else:
                    if cinfo[0] != 'cat':
                        raise ValueError(f"Unexpected categorical constraint format for {attr}: {cinfo}")
                    chosen = cinfo[1]
                row[attr] = chosen
        # replicate samples_per_leaf times
        for _ in range(samples_per_leaf):
            X_rows.append(row.copy())
            y.append(leaf_class)

    X_df = pd.DataFrame(X_rows, columns=feature_names)
    y = np.array(y, dtype=object)

    # 5) encode categorical features to integers
    enc_maps = {}
    X_enc = X_df.copy()
    for attr, is_num in feat_types.items():
        if not is_num:
            vals = list(pd.unique(X_df[attr]))
            mapping = {v: i for i, v in enumerate(vals)}
            enc_maps[attr] = mapping
            X_enc[attr] = X_df[attr].map(mapping).astype(int)

    # 6) class names
    unique_classes = list(pd.unique(y))
    if class_names is None:
        class_names = [str(c) for c in unique_classes]
    else:
        # try to align given class_names with unique_classes if mapping provided as dict
        if isinstance(class_names, dict):
            class_names = [str(class_names.get(c, c)) for c in unique_classes]

    # 7) train sklearn DecisionTreeClassifier on synthetic data
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(X_enc.values, y)

    # 8) plot
    fig, ax = plt.subplots(figsize=figsize)
    try:
        plot_tree(clf, feature_names=feature_names, class_names=[str(c) for c in unique_classes],
                  filled=True, rounded=True, ax=ax)
    except Exception:
        # fallback: without class_names
        plot_tree(clf, feature_names=feature_names, filled=True, rounded=True, ax=ax)

    ax.set_title("Visualized tree (sklearn)")
    if show:
        plt.tight_layout()
        plt.show()
        return None
    else:
        return clf, X_enc, y, fig, ax


# -----------------------

if __name__ == '__main__':
    df = pd.read_csv('Raisin_Dataset.csv')
    target = 'Class'
    (df_train, df_test) = split_dataset(df, 630, target)

    features = [c for c in df.columns if c != target]

    tree = build_tree(df, features, target_col=target, max_depth=5, min_samples_split=1)
    visualize_nested_tree_sklearn(tree, show=True)
    pprint_tree(tree)

    print("\nПредсказание для тестового набора:")
    preds = predict(tree, df_test)
    print(f'Accuracy: {calculate_accuracy(preds, df_test[target].tolist()):.2%}')


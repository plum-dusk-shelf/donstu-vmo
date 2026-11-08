"""
C4.5 implementation (basic, educational)
- Reads CSV
- Assumes last column is the target by default (configurable)
- Handles numeric and categorical features
- Uses Gain Ratio for attribute selection
- Outputs a visual representation (Graphviz if available, else networkx)
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import math
from collections import Counter, defaultdict
import itertools
import typing as t

# Visualization imports (optional)
try:
    import graphviz
    _HAS_GRAPHVIZ = True
except Exception:
    _HAS_GRAPHVIZ = False

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    _HAS_NETWORKX = True
except Exception:
    _HAS_NETWORKX = False


class TreeNode:
    def __init__(self,
                 attribute: t.Optional[str] = None,
                 threshold: t.Optional[float] = None,
                 is_leaf: bool = False,
                 prediction: t.Optional[t.Any] = None):
        self.attribute = attribute            # attribute name to split on
        self.threshold = threshold            # for numeric attributes (<= threshold -> left)
        self.children: dict = {}              # for categorical splits: value -> TreeNode
        self.left: t.Optional[TreeNode] = None
        self.right: t.Optional[TreeNode] = None
        self.is_leaf = is_leaf
        self.prediction = prediction          # for leaf nodes: class label

    def __repr__(self):
        if self.is_leaf:
            return f"Leaf({self.prediction})"
        if self.threshold is not None:
            return f"Node({self.attribute} <= {self.threshold})"
        return f"Node({self.attribute})"


def entropy(labels: t.Sequence) -> float:
    total = len(labels)
    if total == 0:
        return 0.0
    cnt = Counter(labels)
    ent = 0.0
    for v in cnt.values():
        p = v / total
        ent -= p * math.log2(p) if p > 0 else 0.0
    return ent


def split_numeric(values: np.ndarray, labels: np.ndarray):
    """
    For a numeric feature, generate candidate thresholds and evaluate splits.
    Returns list of (threshold, info_gain_ratio, left_idx, right_idx)
    """
    # Sort by feature
    idx = np.argsort(values)
    sorted_vals = values[idx]
    sorted_labels = labels[idx]

    # candidate thresholds: midpoints between consecutive distinct values where label changes
    candidates = []
    for i in range(1, len(sorted_vals)):
        if sorted_vals[i] == sorted_vals[i - 1]:
            continue
        if sorted_labels[i] != sorted_labels[i - 1]:
            thr = (sorted_vals[i] + sorted_vals[i - 1]) / 2.0
            candidates.append(thr)
    return candidates


class C45Classifier:
    def __init__(self, min_samples_split: int = 2, max_depth: int = 100):
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
        self.tree: t.Optional[TreeNode] = None
        self.feature_types: dict = {}  # name -> 'numeric'|'categorical'

    def fit(self, X: pd.DataFrame, y: pd.Series):
        # detect feature types
        for col in X.columns:
            if pd.api.types.is_numeric_dtype(X[col]):
                self.feature_types[col] = 'numeric'
            else:
                self.feature_types[col] = 'categorical'
        data = X.copy()
        data['_label_'] = y
        self.tree = self._build_tree(data, depth=0)

    def predict_row(self, row: pd.Series, node: TreeNode) -> t.Any:
        if node.is_leaf:
            return node.prediction
        if self.feature_types[node.attribute] == 'numeric':
            val = row[node.attribute]
            if pd.isna(val):
                # missing -> fallback to majority (right child)
                return node.right.prediction if node.right and node.right.is_leaf else node.right and self.predict_row(row, node.right)
            if val <= node.threshold:
                return self.predict_row(row, node.left)
            else:
                return self.predict_row(row, node.right)
        else:
            val = row[node.attribute]
            child = node.children.get(val)
            if child is None:
                # unseen category -> majority child by size (fallback)
                # choose child with highest support if present
                if node.children:
                    # pick any leaf child prediction (first)
                    first_child = next(iter(node.children.values()))
                    return first_child.prediction if first_child.is_leaf else self.predict_row(row, first_child)
                else:
                    return None
            return self.predict_row(row, child)

    def predict(self, X: pd.DataFrame) -> list:
        if self.tree is None:
            raise ValueError("Model not fitted.")
        preds = []
        for _, row in X.iterrows():
            preds.append(self.predict_row(row, self.tree))
        return preds

    def _build_tree(self, data: pd.DataFrame, depth: int) -> TreeNode:
        labels = data['_label_'].values
        label_counts = Counter(labels)
        # stopping criteria
        if len(label_counts) == 1:
            return TreeNode(is_leaf=True, prediction=next(iter(label_counts)))
        if len(data) < self.min_samples_split or depth >= self.max_depth:
            # make leaf with majority class
            majority = label_counts.most_common(1)[0][0]
            return TreeNode(is_leaf=True, prediction=majority)

        best = self._choose_best_split(data)
        if best is None:
            # cannot split -> leaf
            majority = label_counts.most_common(1)[0][0]
            return TreeNode(is_leaf=True, prediction=majority)

        attribute, split_info = best
        if split_info['type'] == 'numeric':
            thr = split_info['threshold']
            node = TreeNode(attribute=attribute, threshold=thr, is_leaf=False)
            left_mask = data[attribute].le(thr)
            right_mask = ~left_mask
            node.left = self._build_tree(data[left_mask].reset_index(drop=True), depth + 1)
            node.right = self._build_tree(data[right_mask].reset_index(drop=True), depth + 1)
            return node
        else:
            # categorical: split per value
            node = TreeNode(attribute=attribute, is_leaf=False)
            for val, subset in split_info['subsets'].items():
                if subset.shape[0] == 0:
                    # empty -> leaf with majority
                    node.children[val] = TreeNode(is_leaf=True, prediction=Counter(labels).most_common(1)[0][0])
                else:
                    node.children[val] = self._build_tree(subset.reset_index(drop=True), depth + 1)
            return node

    def _choose_best_split(self, data: pd.DataFrame):
        base_entropy = entropy(data['_label_'].values)
        best_gain_ratio = 0.0
        best_attr = None
        best_info = None

        n = len(data)
        for attr in data.columns:
            if attr == '_label_':
                continue
            if self.feature_types[attr] == 'numeric':
                values = data[attr].values
                labels = data['_label_'].values
                candidates = split_numeric(values, labels)
                for thr in candidates:
                    left_idx = data[attr] <= thr
                    right_idx = ~left_idx
                    left_labels = data[left_idx]['_label_'].values
                    right_labels = data[right_idx]['_label_'].values
                    # compute information gain
                    left_entropy = entropy(left_labels)
                    right_entropy = entropy(right_labels)
                    info_after = (len(left_labels)/n) * left_entropy + (len(right_labels)/n) * right_entropy
                    info_gain = base_entropy - info_after
                    # intrinsic information (split info) for gain ratio
                    split_info = 0.0
                    for part in [len(left_labels), len(right_labels)]:
                        if part == 0:
                            continue
                        p = part / n
                        split_info -= p * math.log2(p)
                    if split_info == 0:
                        continue
                    gain_ratio = info_gain / split_info
                    if gain_ratio > best_gain_ratio:
                        best_gain_ratio = gain_ratio
                        best_attr = attr
                        best_info = {'type': 'numeric', 'threshold': thr, 'gain_ratio': gain_ratio}
            else:
                # categorical
                subsets = {}
                intrinsic_parts = []
                info_after = 0.0
                for val, subset in data.groupby(attr):
                    subset_labels = subset['_label_'].values
                    subsets[val] = subset
                    prop = len(subset_labels) / n
                    intrinsic_parts.append(prop)
                    info_after += prop * entropy(subset_labels)
                info_gain = base_entropy - info_after
                split_info = 0.0
                for p in intrinsic_parts:
                    if p > 0:
                        split_info -= p * math.log2(p)
                if split_info == 0:
                    continue
                gain_ratio = info_gain / split_info
                if gain_ratio > best_gain_ratio:
                    best_gain_ratio = gain_ratio
                    best_attr = attr
                    best_info = {'type': 'categorical', 'subsets': subsets, 'gain_ratio': gain_ratio}

        if best_attr is None:
            return None
        return best_attr, best_info


# -------------------------
# Utility: read CSV and run
# -------------------------
def load_data_from_csv(path: str, target: t.Optional[str] = None, **read_csv_kwargs):
    df = pd.read_csv(path, **read_csv_kwargs)
    if target is None:
        target = df.columns[-1]
    X = df.drop(columns=[target])
    y = df[target]
    return X, y


# -------------------------
# Visualization utilities
# -------------------------
def tree_to_graphviz(node: TreeNode, node_id=0, dot=None, label_formatter=None):
    """
    Build a graphviz.Digraph from the tree recursively.
    """
    if dot is None:
        dot = graphviz.Digraph()
    # name for node
    name = f"n{node_id}"
    if node.is_leaf:
        label = f"Leaf\\n{node.prediction}"
        dot.node(name, label=label, shape='box', style='filled', fillcolor='lightgrey')
        return dot, node_id + 1
    if node.threshold is not None:
        label = f"{node.attribute} <= {round(node.threshold, 4)}"
        dot.node(name, label=label)
        # left
        left_id = node_id + 1
        dot, next_id = tree_to_graphviz(node.left, left_id, dot)
        dot.edge(name, f"n{left_id}", label=f"yes")
        # right
        right_id = next_id
        dot, next_id = tree_to_graphviz(node.right, right_id, dot)
        dot.edge(name, f"n{right_id}", label=f"no")
        return dot, next_id
    else:
        label = f"{node.attribute}"
        dot.node(name, label=label)
        cur_id = node_id + 1
        next_id = cur_id
        for val, child in node.children.items():
            dot, next_id = tree_to_graphviz(child, next_id, dot)
            dot.edge(name, f"n{next_id-1}", label=str(val))
        return dot, next_id


def draw_tree_graphviz(tree: TreeNode, filename: str = "c45_tree", view: bool = True):
    if not _HAS_GRAPHVIZ:
        raise RuntimeError("graphviz python package not available")
    dot, _ = tree_to_graphviz(tree, 0, None)
    dot.render(filename, view=view, format='pdf')


def draw_tree_networkx(tree: TreeNode):
    if not _HAS_NETWORKX:
        raise RuntimeError("networkx/matplotlib not available")
    G = nx.DiGraph()
    labels = {}

    def recurse(n: TreeNode, idx: int = 0) -> int:
        my_id = idx
        if n.is_leaf:
            G.add_node(my_id)
            labels[my_id] = f"Leaf\n{n.prediction}"
            return idx + 1
        if n.threshold is not None:
            labels[my_id] = f"{n.attribute}<=\n{round(n.threshold,4)}"
            G.add_node(my_id)
            left_id = idx + 1
            next_idx = recurse(n.left, left_id)
            G.add_edge(my_id, left_id, label="yes")
            right_id = next_idx
            next_idx = recurse(n.right, right_id)
            G.add_edge(my_id, right_id, label="no")
            return next_idx
        else:
            labels[my_id] = f"{n.attribute}"
            G.add_node(my_id)
            cur = idx + 1
            for val, ch in n.children.items():
                child_id = cur
                cur = recurse(ch, child_id)
                G.add_edge(my_id, child_id, label=str(val))
            return cur

    recurse(tree, 0)
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot') if _HAS_GRAPHVIZ else nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color='lightblue', font_size=8)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.axis('off')
    plt.show()


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="C4.5 classifier demo")
    parser.add_argument("--csv", type=str, default="Raisin_dataset.csv", help="Path to CSV file")
    parser.add_argument("--target", type=str, default=None, help="Target column name (default: last column)")
    parser.add_argument("--min_samples", type=int, default=2)
    parser.add_argument("--max_depth", type=int, default=10)
    parser.add_argument("--visualize", action="store_true", help="Try to visualize the tree")
    args = parser.parse_args()

    X, y = load_data_from_csv(args.csv, target=args.target)
    clf = C45Classifier(min_samples_split=args.min_samples, max_depth=args.max_depth)
    print("Fitting...")
    clf.fit(X, y)
    print("Done. Root:", clf.tree)

    # quick accuracy on training data
    preds = clf.predict(X)
    acc = sum(1 for a, b in zip(preds, y) if a == b) / len(y)
    print(f"Training accuracy: {acc:.4f}")

    if _HAS_GRAPHVIZ:
        dot, _ = tree_to_graphviz(clf.tree)
        dot.render("c45_tree", view=True, format="pdf")
        print("Graphviz tree rendered to c45_tree.pdf")
    elif _HAS_NETWORKX:
        draw_tree_networkx(clf.tree)
    else:
        print("No visualization libraries available (install 'graphviz' python package or 'networkx'+'matplotlib').")

# credit_classify.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix, classification_report
from sklearn.impute import SimpleImputer

# ---------- ПАРАМЕТРЫ ----------
PATH_CREDIT = "Credit_card.csv"         # поменяй при необходимости
PATH_LABEL  = "Credit_card_label.csv"   # поменяй при необходимости
RANDOM_STATE = 42
N_FOLDS = 5
EPS_REG = 1e-6
# -------------------------------

def load_and_merge(path_credit, path_label):
    df = pd.read_csv(path_credit)
    labels = pd.read_csv(path_label)
    # Ожидается, что в обоих есть поле Ind_ID для объединения
    if 'Ind_ID' in df.columns and 'Ind_ID' in labels.columns:
        merged = pd.merge(labels, df, on='Ind_ID', how='inner')
    else:
        # если файл уже содержит label под именем 'Label' или 'object'
        merged = df.copy()
        if 'Label' in labels.columns:
            merged = pd.merge(labels, df, left_on='Ind_ID', right_on='Ind_ID', how='inner') if 'Ind_ID' in df.columns else merged
    return merged

def basic_cleaning(df):
    df = df.copy()
    # Удалим идентификаторы и очевидно бесполезные поля
    for col in ['Ind_ID', 'EMAIL_ID', 'Phone', 'Mobile_phone', 'Work_Phone']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    # Нормализуем имена колонок
    df.columns = [c.strip() for c in df.columns]
    return df

def encode_and_engineer(df):
    df = df.copy()
    # Приведём метку к 'object' или 'Label'
    if 'Label' in df.columns and 'object' not in df.columns:
        df.rename(columns={'Label': 'object'}, inplace=True)
    # Простейшее явное кодирование бинарных текстов
    map_yn = {'Y':1, 'N':0, 'Yes':1, 'No':0, 'y':1, 'n':0}
    for col in ['Car_Owner', 'Propert_Owner', 'Mobile_phone', 'Work_phone', 'Phone']:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].map(map_yn).astype(float)
    # Пол
    if 'GENDER' in df.columns:
        df['GENDER'] = df['GENDER'].map({'M':1, 'F':0, 'm':1, 'f':0}).astype(float)
    # Для всех оставшихся категориальных — get_dummies (drop_first чтобы избежать коллинеарности)
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    # Не трогаем метку
    cat_cols = [c for c in cat_cols if c != 'object']
    if cat_cols:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    # Фичи: лог дохода (защищенно), возраст/работа можно трансформировать при наличии
    if 'Annual_income' in df.columns:
        df['Annual_income'] = pd.to_numeric(df['Annual_income'], errors='coerce')
        # логарифм с защиотой от нуля и отрицательных
        df['Annual_income_log'] = np.log1p(df['Annual_income'].clip(lower=0))
    # взаимодействие простая фича
    if 'Car_Owner' in df.columns and 'Annual_income_log' in df.columns:
        df['Car_x_income'] = df['Car_Owner'] * df['Annual_income_log']
    return df

def prepare_matrix(df):
    df = df.copy()
    # Убедимся, что метка бинарная 0/1
    if 'object' not in df.columns and 'Label' in df.columns:
        df.rename(columns={'Label':'object'}, inplace=True)
    if 'object' not in df.columns:
        raise ValueError("Не найден столбец с метками ('object' или 'Label').")
    y = df['object'].astype(int).values
    X = df.drop(columns=['object'])
    # Импутация простая
    imputer = SimpleImputer(strategy='median')
    X_imp = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    return X_imp, y

def diagnostics_and_fisher(X, y):
    print("Shape X:", X.shape)
    print("Class counts:", np.bincount(y))
    # per-feature Fisher score
    def fisher_feature(a, b):
        m0, m1 = a.mean(), b.mean()
        s0 = a.var(ddof=1)
        s1 = b.var(ddof=1)
        return ((m0 - m1)**2) / (s0 + s1) if (s0 + s1) > 0 else 0
    Xvals = X.values
    scores = {}
    for i, col in enumerate(X.columns):
        a = Xvals[y==0, i]
        b = Xvals[y==1, i]
        scores[col] = fisher_feature(a, b)
    # отсортируем и покажем топ-10
    sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    print("Top features by Fisher score (feature:score):")
    for f, s in sorted_scores[:15]:
        print(f, ":", s)
    return scores

def lda_pipeline(X, y, random_state=RANDOM_STATE):
    # стандартизация
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    # Разделение
    X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.25, stratify=y, random_state=random_state)
    # Ковариации по группам (ddof=1)
    X1 = X_train[y_train==0]
    X2 = X_train[y_train==1]
    n1, n2 = len(X1), len(X2)
    s1 = np.cov(X1, rowvar=False, ddof=1)
    s2 = np.cov(X2, rowvar=False, ddof=1)
    SO = ((n1-1)*s1 + (n2-1)*s2) / (n1 + n2 - 2)
    print("SO shape:", SO.shape)
    print("det(SO):", np.linalg.det(SO))
    print("rank(SO):", np.linalg.matrix_rank(SO))
    # Регуляризация
    eps = EPS_REG * np.trace(SO)
    SO_reg = SO + np.eye(SO.shape[0]) * eps
    # Псевдообратная
    SO_inv = np.linalg.pinv(SO_reg)
    mean_diff = X1.mean(axis=0) - X2.mean(axis=0)
    A = SO_inv @ mean_diff
    print("norm(A):", np.linalg.norm(A))
    # Проекция обуч и тест
    F_train = X_train @ A
    F_test = X_test @ A
    # Центрируем по средней границе
    F_all_mean = (F_train.mean() + F_test.mean()) / 2
    F_train_c = F_train - F_all_mean
    F_test_c = F_test - F_all_mean
    # Оценка separability
    sep = (F_train.mean() - F_test.mean())**2 / (F_train.var(ddof=1) + F_test.var(ddof=1))
    print("Fisher separation (projection):", sep)
    # Классификация по порогу 0
    y_pred_test = (F_test_c > 0).astype(int)
    # Метрики
    acc = accuracy_score(y_test, y_pred_test)
    prec = precision_score(y_test, y_pred_test, zero_division=0)
    rec = recall_score(y_test, y_pred_test, zero_division=0)
    # ROC AUC требует вероятностных оценок — используем логит на F (как простая сигмоида)
    try:
        roc = roc_auc_score(y_test, F_test_c)
    except Exception:
        roc = np.nan
    print("LDA (manual proj) test acc/prec/rec/roc:", acc, prec, rec, roc)
    return {
        'A': A, 'scaler': scaler, 'F_train': F_train_c, 'F_test': F_test_c,
        'X_train': X_train, 'X_test': X_test, 'y_train': y_train, 'y_test': y_test,
        'y_pred_test': y_pred_test
    }

def compare_classifiers(X, y):
    Xs = StandardScaler().fit_transform(X)
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    models = {
        'LDA_sklearn': LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto'),
        'Logistic': LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        'RandomForest': RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE)
    }
    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, Xs, y, cv=skf, scoring='roc_auc')
        results[name] = scores
        print(f"{name} ROC AUC folds: {scores}, mean: {scores.mean():.4f}")
    return results

def plot_projection(res):
    Ftr = res['F_train']
    Fte = res['F_test']
    ytr = res['y_train']
    yte = res['y_test']
    plt.figure(figsize=(12,4))
    plt.subplot(1,2,1)
    plt.title("Проекция LDA (обучение)")
    plt.scatter(range(len(Ftr[ytr==0])), Ftr[ytr==0], label='class0', alpha=0.7)
    plt.scatter(range(len(Ftr[ytr==0]), len(Ftr)), Ftr[ytr==1], label='class1', alpha=0.7)
    plt.axhline(0, color='k', linestyle='--')
    plt.legend()
    plt.subplot(1,2,2)
    plt.title("Проекция LDA (тест)")
    plt.scatter(range(len(Fte[yte==0])), Fte[yte==0], label='class0', alpha=0.7)
    plt.scatter(range(len(Fte[yte==0]), len(Fte)), Fte[yte==1], label='class1', alpha=0.7)
    plt.axhline(0, color='k', linestyle='--')
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    print("Загрузка и объединение данных...")
    df = load_and_merge(PATH_CREDIT, PATH_LABEL)
    print("Initial shape:", df.shape)
    df = basic_cleaning(df)
    df = encode_and_engineer(df)
    X, y = prepare_matrix(df)
    # Диагностика фичей
    fisher_scores = diagnostics_and_fisher(X, y)
    # LDA pipeline
    res = lda_pipeline(X, y)
    # Визуализация проекции
    plot_projection(res)
    # Сравнение классификаторов
    print("Cross-validated comparison:")
    compare_classifiers(X, y)
    # Подробный отчет модели на тесте (LogReg для интерпретации)
    Xs = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE)
    clf = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE).fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("Logistic on test set:")
    print(classification_report(y_test, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

if __name__ == "__main__":
    main()

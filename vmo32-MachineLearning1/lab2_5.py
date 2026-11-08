def main():
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.metrics import classification_report, confusion_matrix
    import matplotlib.pyplot as plt

    # Загрузка данных
    data = pd.read_csv('Credit_card_label.csv')
    data_2 = pd.read_csv('Credit_card.csv')
    data_merged = pd.merge(data, data_2, on='Ind_ID').copy()

    # Выбор признаков
    data_processed = data_merged[['Ind_ID', 'object', 'Car_Owner', 'Propert_Owner',
                                  'Annual_income', 'Type_Income', 'EDUCATION',
                                  'Employed_days', 'Type_Occupation']].copy()

    # Предобработка
    data_processed['Annual_income'] = data_processed['Annual_income'] / 10 ** 4
    data_processed.dropna(inplace=True)

    # Разделение на признаки и целевую переменную
    X = data_processed.drop(columns=['object', 'Ind_ID'])
    y = data_processed['object']

    # Кодирование категориальных переменных
    categorical_columns = ['Car_Owner', 'Propert_Owner', 'Type_Income', 'EDUCATION', 'Type_Occupation']
    label_encoders = {}
    for col in categorical_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

    # Масштабирование числовых признаков
    scaler = StandardScaler()
    numerical_columns = ['Annual_income', 'Employed_days']
    X[numerical_columns] = scaler.fit_transform(X[numerical_columns])

    # Разделение на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Обучение LDA
    lda = LinearDiscriminantAnalysis()
    lda.fit(X_train, y_train)

    # Предсказания
    y_pred = lda.predict(X_test)
    y_scores = lda.decision_function(X_test)

    # Оценка модели
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Визуализация
    plt.figure(figsize=(12, 5))

    # Гистограмма дискриминантных scores
    plt.subplot(1, 2, 1)
    for class_label in [0, 1]:
        mask = y_test == class_label
        plt.hist(y_scores[mask], alpha=0.7, label=f'Class {class_label}', bins=20)
    plt.axvline(x=0, color='red', linestyle='--', label='Decision Boundary')
    plt.xlabel('Discriminant Score')
    plt.ylabel('Frequency')
    plt.title('LDA Discriminant Scores')
    plt.legend()

    # ROC-like visualization
    plt.subplot(1, 2, 2)
    class_0_scores = y_scores[y_test == 0]
    class_1_scores = y_scores[y_test == 1]

    plt.scatter(range(len(class_0_scores)), class_0_scores, alpha=0.7, label='Class 0')
    plt.scatter(range(len(class_0_scores), len(class_0_scores) + len(class_1_scores)),
                class_1_scores, alpha=0.7, label='Class 1')
    plt.axhline(y=0, color='red', linestyle='--', label='Decision Boundary')
    plt.xlabel('Sample Index')
    plt.ylabel('Discriminant Score')
    plt.title('LDA Classification Results')
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Анализ важности признаков
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'coefficient': lda.coef_[0]
    }).sort_values('coefficient', key=abs, ascending=False)

    print("\nFeature Importance:")
    print(feature_importance)


if __name__ == '__main__':
    main()

def main():
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    from sklearn.feature_selection import SelectKBest, f_classif
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Загрузка и обработка данных
    data = pd.read_csv('Credit_card_label.csv')
    data_2 = pd.read_csv('Credit_card.csv')
    data_merged = pd.merge(data, data_2, on='Ind_ID')

    print("=== ДИАГНОСТИКА ДАННЫХ ===")
    print(f"Размер датасета: {data_merged.shape}")
    print(f"Количество пропущенных значений: {data_merged.isnull().sum().sum()}")

    # Анализ целевой переменной
    print(f"\nРАСПРЕДЕЛЕНИЕ ЦЕЛЕВОЙ ПЕРЕМЕННОЙ:")
    print(data_merged['object'].value_counts())
    print(f"Доля класса 1: {data_merged['object'].mean():.3f}")

    # Выбор признаков с более тщательным подходом
    features = ['GENDER', 'Car_Owner', 'Propert_Owner', 'CHILDREN',
                'Annual_income', 'Type_Income', 'EDUCATION', 'Marital_status',
                'Housing_type', 'Employed_days', 'Type_Occupation', 'Family_Members']

    data_processed = data_merged[['Ind_ID', 'object'] + features].copy()

    # Более аккуратная обработка пропущенных значений
    print(f"\nПРОПУЩЕННЫЕ ЗНАЧЕНИЯ ПО ПРИЗНАКАМ:")
    print(data_processed.isnull().sum())

    # Заполнение пропущенных значений вместо удаления
    for col in features:
        if data_processed[col].dtype in ['int64', 'float64']:
            data_processed[col].fillna(data_processed[col].median(), inplace=True)
        else:
            data_processed[col].fillna(
                data_processed[col].mode()[0] if len(data_processed[col].mode()) > 0 else 'Unknown', inplace=True)

    # Кодирование категориальных переменных
    label_encoders = {}
    for col in features:
        if data_processed[col].dtype == 'object':
            le = LabelEncoder()
            data_processed[col] = le.fit_transform(data_processed[col].astype(str))
            label_encoders[col] = le

    # Разделение на признаки и целевую переменную
    X = data_processed[features]
    y = data_processed['object']

    print(f"\nАНАЛИЗ ПРИЗНАКОВ:")
    print(f"Количество признаков: {len(features)}")
    print(f"Типы признаков:")
    print(X.dtypes.value_counts())

    # Анализ корреляции с целевой переменной
    correlations = []
    for feature in features:
        if X[feature].dtype in ['int64', 'float64']:
            corr = np.corrcoef(X[feature], y)[0, 1]
            correlations.append((feature, abs(corr)))

    correlations.sort(key=lambda x: x[1], reverse=True)
    print(f"\nТОП-5 ПРИЗНАКОВ ПО КОРРЕЛЯЦИИ С ЦЕЛЕВОЙ ПЕРЕМЕННОЙ:")
    for feat, corr in correlations[:5]:
        print(f"  {feat}: {corr:.3f}")

    # Разделение на обучающую и тестовую выборки с стратификацией
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42, shuffle=True
    )

    print(f"\nРАЗБИЕНИЕ ДАННЫХ:")
    print(f"Обучающая выборка: {X_train.shape[0]} samples")
    print(f"Тестовая выборка: {X_test.shape[0]} samples")
    print(f"Доля класса 1 в обучающей: {y_train.mean():.3f}")
    print(f"Доля класса 1 в тестовой: {y_test.mean():.3f}")

    # Масштабирование признаков
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Отбор признаков
    selector = SelectKBest(score_func=f_classif, k=min(8, len(features)))
    X_train_selected = selector.fit_transform(X_train_scaled, y_train)
    X_test_selected = selector.transform(X_test_scaled)

    selected_features = [features[i] for i in selector.get_support(indices=True)]
    print(f"\nОТОБРАННЫЕ ПРИЗНАКИ ({len(selected_features)}):")
    print(selected_features)

    # Обучение LDA с разными подходами
    lda_models = {}

    # 1. Базовая LDA
    lda_basic = LinearDiscriminantAnalysis()
    lda_basic.fit(X_train_scaled, y_train)
    y_pred_basic = lda_basic.predict(X_test_scaled)
    lda_models['LDA Basic'] = {
        'model': lda_basic,
        'accuracy': (y_pred_basic == y_test).mean(),
        'X_train': X_train_scaled,
        'X_test': X_test_scaled
    }

    # 2. LDA с отобранными признаками
    lda_selected = LinearDiscriminantAnalysis()
    lda_selected.fit(X_train_selected, y_train)
    y_pred_selected = lda_selected.predict(X_test_selected)
    lda_models['LDA Selected Features'] = {
        'model': lda_selected,
        'accuracy': (y_pred_selected == y_test).mean(),
        'X_train': X_train_selected,
        'X_test': X_test_selected
    }

    # 3. LDA с регуляризацией (для численной стабильности)
    lda_regularized = LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto')
    lda_regularized.fit(X_train_scaled, y_train)
    y_pred_regularized = lda_regularized.predict(X_test_scaled)
    lda_models['LDA Regularized'] = {
        'model': lda_regularized,
        'accuracy': (y_pred_regularized == y_test).mean(),
        'X_train': X_train_scaled,
        'X_test': X_test_scaled
    }

    # Выбор лучшей модели
    best_model_name = max(lda_models.items(), key=lambda x: x[1]['accuracy'])[0]
    best_model = lda_models[best_model_name]['model']
    best_X_test = lda_models[best_model_name]['X_test']

    print(f"\n=== РЕЗУЛЬТАТЫ МОДЕЛЕЙ ===")
    for name, result in lda_models.items():
        y_pred = result['model'].predict(result['X_test'])
        accuracy = (y_pred == y_test).mean()
        auc = roc_auc_score(y_test, result['model'].predict_proba(result['X_test'])[:, 1])
        print(f"{name}:")
        print(f"  Точность: {accuracy:.4f}")
        print(f"  AUC-ROC: {auc:.4f}")
        print(f"  Правильных: {np.sum(y_pred == y_test)}/{len(y_test)}")

    # Дискриминантные функции для лучшей модели
    X_lda_train = best_model.transform(lda_models[best_model_name]['X_train'])
    X_lda_test = best_model.transform(best_X_test)

    # Разделяем на классы для визуализации
    class_0_train = X_lda_train[y_train == 0].flatten()
    class_1_train = X_lda_train[y_train == 1].flatten()
    class_0_test = X_lda_test[y_test == 0].flatten()
    class_1_test = X_lda_test[y_test == 1].flatten()

    def visualization():
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. График дискриминантных функций
        ax1 = axes[0, 0]

        # Обучающие данные
        ax1.plot(range(1, len(class_0_train) + 1), class_0_train, 'bo',
                 label='class0 (train)', markersize=4, alpha=0.6)
        ax1.plot(range(len(class_0_train) + 1, len(class_0_train) + len(class_1_train) + 1),
                 class_1_train, 'ro', label='class1 (train)', markersize=4, alpha=0.6)

        # Тестовые данные
        start_test = len(class_0_train) + len(class_1_train) + 1
        ax1.plot(range(start_test, start_test + len(class_0_test)),
                 class_0_test, 'bs', label='class0 (test)', markersize=4, alpha=0.6)
        ax1.plot(range(start_test + len(class_0_test), start_test + len(class_0_test) + len(class_1_test)),
                 class_1_test, 'rs', label='class1 (test)', markersize=4, alpha=0.6)

        ax1.axhline(y=0, color='black', linestyle='--', linewidth=2, label='Decision Boundary')
        ax1.set_xlabel('Object Index')
        ax1.set_ylabel('Discriminant Function')
        ax1.set_title(f'LDA Projection ({best_model_name})\nAccuracy: {lda_models[best_model_name]["accuracy"]:.3f}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Гистограмма распределения
        ax2 = axes[0, 1]
        ax2.hist(class_0_test, bins=20, alpha=0.7, color='blue', label='class0', density=True)
        ax2.hist(class_1_test, bins=20, alpha=0.7, color='red', label='class1', density=True)
        ax2.axvline(x=0, color='black', linestyle='--', linewidth=2, label='Decision Boundary')
        ax2.set_xlabel('Discriminant Function')
        ax2.set_ylabel('Density')
        ax2.set_title('Distribution of Discriminant Functions')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Сравнение моделей
        ax3 = axes[1, 0]
        model_names = list(lda_models.keys())
        accuracies = [lda_models[name]['accuracy'] for name in model_names]

        bars = ax3.bar(model_names, accuracies, color=['skyblue', 'lightcoral', 'lightgreen'])
        for bar, acc in zip(bars, accuracies):
            ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                     f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')

        ax3.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Random Classifier')
        ax3.set_ylabel('Accuracy')
        ax3.set_title('Model Comparison')
        ax3.tick_params(axis='x', rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # 4. Матрица ошибок
        ax4 = axes[1, 1]
        y_pred_best = best_model.predict(best_X_test)
        cm = confusion_matrix(y_test, y_pred_best)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax4,
                    xticklabels=['Predicted 0', 'Predicted 1'],
                    yticklabels=['Actual 0', 'Actual 1'])
        ax4.set_title('Confusion Matrix')

        plt.tight_layout()
        plt.show()

    # Детальный анализ
    print(f"\n=== ДЕТАЛЬНЫЙ АНАЛИЗ ЛУЧШЕЙ МОДЕЛИ ({best_model_name}) ===")

    # Анализ разделимости
    separability_0 = np.sum(class_0_test < 0) / len(class_0_test)
    separability_1 = np.sum(class_1_test > 0) / len(class_1_test)

    print(f"Разделимость class0: {separability_0:.3f} ({np.sum(class_0_test < 0)}/{len(class_0_test)})")
    print(f"Разделимость class1: {separability_1:.3f} ({np.sum(class_1_test > 0)}/{len(class_1_test)})")

    # Если классификация плохая
    if lda_models[best_model_name]['accuracy'] < 0.7:
        print(f"\n⚠️  ВОЗМОЖНЫЕ ПРОБЛЕМЫ:")
        print("1. Признаки слабо связаны с целевой переменной")
        print("2. Сильный дисбаланс классов")
        print("3. Нелинейная зависимость, которую LDA не может уловить")
        print("4. Шум в данных")
        print("\nРЕКОМЕНДАЦИИ:")
        print("• Попробуйте другие алгоритмы (Random Forest, XGBoost)")
        print("• Соберите дополнительные признаки")
        print("• Проведите feature engineering")
        print("• Используйте ансамбли моделей")

    # Визуализация
    visualization()

if __name__ == '__main__':
    main()

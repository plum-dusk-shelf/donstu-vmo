import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from lab3 import predict


def linear_regression_1d(x, y):
    """
    Линейная регрессия y = a*x + b
    """
    x_mean = x.mean()
    y_mean = y.mean()

    numerator = ((x - x_mean) * (y - y_mean)).sum() # Σ[(xᵢ - x̄)(yᵢ - ȳ)]
    denominator = ((x - x_mean) ** 2).sum() # Σ(xᵢ - x̄)²

    a = numerator / denominator # β₁ (угловой коэффициент)
    b = y_mean - a * x_mean # β₀ (свободный член)

    return round(a, digit), round(b, digit)

def calculate_correlation(x, y):
    # Преобразуем в numpy массивы для вычислений
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)

    # Вычисляем коэффициент корреляции Пирсона
    correlation, p_value = stats.pearsonr(x_arr, y_arr)

    # Вычисляем коэффициент детерминации R²
    r_squared = correlation ** 2

    return round(correlation, 3), round(r_squared, 3), round(p_value, 5)

def confidence_interval(x, y, a, b, x_pred, t_value=2.0):
    x = pd.Series(x, dtype=float)
    y = pd.Series(y, dtype=float)

    n = len(x)
    x_mean = x.mean()

    # предсказания на обучающих данных
    y_hat = a * x + b
    residuals = y - y_hat

    # дисперсия ошибок
    sigma2 = (residuals ** 2).sum() / (n - 2)
    sigma = sigma2 ** 0.5

    Sxx = ((x - x_mean) ** 2).sum()

    ci_upper = []
    ci_lower = []

    for x0 in x_pred:
        se = sigma * ((1 / n + (x0 - x_mean) ** 2 / Sxx) ** 0.5) # SE(ŷ₀) = σ̂ * √(1/n + (x₀ - x̄)² / Sxx)
        y0 = a * x0 + b

        ci_upper.append(y0 + t_value * se)
        ci_lower.append(y0 - t_value * se)

    return ci_lower, ci_upper

def confidence_plus_minus(x, y, a, b, t_value=1.96):
    x = pd.Series(x, dtype=float)
    y = pd.Series(y, dtype=float)

    n = len(x)
    y_hat = a * x + b
    residuals = y - y_hat

    sigma = ((residuals ** 2).sum() / (n - 2)) ** 0.5
    delta = t_value * sigma

    return round(delta, digit)

def make_regression(row, ax, years, forecast_years):
    predict_years = list(range(int(years.iloc[0]), int(years.iloc[-1]) + forecast_years + 1))
    country = row.iloc[0]
    values = row.iloc[1:].astype(float)

    x = years
    y = values.values

    correlation, r_squared, p_value = calculate_correlation(x, y)
    print(f'Коэффициент корреляции = {correlation}\n')

    a, b = linear_regression_1d(x, y)

    y_pred = [a * year + b for year in predict_years]

    ci_low, ci_high = confidence_interval(
        x,
        y,
        a,
        b,
        predict_years
    )

    delta = confidence_plus_minus(x,y,a,b)

    ax.plot(x, y, color="blue")
    ax.plot(predict_years, y_pred, linestyle="--" , label=f"y = {a}x + {b}", color="blue")
    ax.scatter(predict_years[-1], y_pred[-1], label=y_pred[-1], color="red")
    ax.fill_between(predict_years, ci_low, ci_high, alpha=0.2, label=f'±{delta}')

    ax.set_title(country)
    ax.set_ylabel("Значение")
    ax.legend()

if __name__ == "__main__":
    digit = 0

    df = pd.read_csv("Coffee_export.csv")
    df = df.drop(columns=["Total_export"])

    # divisor = 10**3
    # numeric_cols = df.select_dtypes(include=[np.number]).columns
    # df[numeric_cols] = df[numeric_cols] / divisor

    years = pd.Series(df.columns[1:].astype(int))

    print(df.iloc[:,0])

    while True:
        forecast_years = int(input("Срок прогноза "))
        action = input("Номер страны в списке ")
        if str(action) in "XxХх":
            break
        elif action == "":
            continue
        else:
            row = int(action)
            ax = plt.subplot()
            make_regression(df.loc[row], ax, years, forecast_years)
            ax.set_xlabel("Год")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

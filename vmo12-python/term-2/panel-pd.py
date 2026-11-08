import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.rand(100, 5), index=range(1, 101), columns=range(1, 6))

# корреляция — похожий набор значений у двух признаков

print(df.describe())

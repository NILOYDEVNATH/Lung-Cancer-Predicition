import pandas as pd

df = pd.read_csv('lung_cancer_prediction.csv')

first_100 = df.head(100)
first_100.to_csv('first_100_rows.csv', index=False)


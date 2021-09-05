import pandas as pd

data = pd.read_csv('/Users/macbook/PycharmProjects/Artwork/Middleware/english.csv')

print(data)
print(data.dropna().empty)

from pprint import pprint
import pandas as pd

path = "/Users/andrewcasanova/Downloads/jehle_verb_database.csv"

with open(path, 'r', encoding='utf-8') as file:
    data = pd.read_csv(file)

print(data['infinitive'].unique().tolist())
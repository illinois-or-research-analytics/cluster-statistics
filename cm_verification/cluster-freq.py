import pandas as pd
from sys import argv
import os

base, ext = os.path.splitext(argv[1])
df = pd.read_csv(argv[1])
df2 = df.groupby(['n'])['n'].count()

df2.to_csv(base + '_freq.csv')
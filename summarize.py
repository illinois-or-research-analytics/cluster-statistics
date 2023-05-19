import os

import pandas as pd
import numpy as np

from sys import argv

stats = pd.read_csv(argv[1])
base, ext = os.path.splitext(argv[1])

overall = stats.iloc[-1]
modularity = overall['modularity']
cpm_score = overall['cpm_score']

mincuts = stats.iloc[:-1]['connectivity']
mincuts_normalized = stats.iloc[:-1]['connectivity_normalized']

mincuts_min = mincuts.min()
mincuts_max = mincuts.max()
mincuts_med = mincuts.median()
mincuts_q1 = mincuts.quantile(0.25)
mincuts_q3 = mincuts.quantile(0.75)
mincuts_normalized_min = mincuts_normalized.min()
mincuts_normalized_max = mincuts_normalized.max()
mincuts_normalized_med = mincuts_normalized.median()
mincuts_normalized_q1 = mincuts_normalized.quantile(0.25)
mincuts_normalized_q3 = mincuts_normalized.quantile(0.75)

summary_stats = pd.Series({
    'modularity': modularity,
    'cpm_score': cpm_score,
    'mincuts_min': mincuts_min,
    'mincuts_q1': mincuts_q1,
    'mincuts_med': mincuts_med,
    'mincuts_q3': mincuts_q3,
    'mincuts_max': mincuts_max,
    'mincuts_min_normalized': mincuts_normalized_min,
    'mincuts_q1_normalized': mincuts_normalized_q1,
    'mincuts_med_normalized': mincuts_normalized_med,
    'mincuts_q3_normalized': mincuts_normalized_q3,
    'mincuts_max_normalized': mincuts_normalized_max
})

summary_stats.to_csv(base + '_summary.csv', header=False)

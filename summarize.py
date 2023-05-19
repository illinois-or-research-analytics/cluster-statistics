import pandas as pd
import numpy as np

from sys import argv

stats = pd.read_csv(argv[1])

num_clusters = stats.shape[0] - 1

stats['log10'] = np.log10

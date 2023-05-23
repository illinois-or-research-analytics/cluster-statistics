# cluster-statistics
Given a clustering in a .tsv format with two columns `node_id, cluster_id`, this software package will report both per-cluster statistics as well as summary statistics. The user is also able to run on a single clustering or batch process multiple clusterings into a table of summary statistics.
## Setup
### Prerequisites
You will need the following:
- Python3.9 or newer (I suggest you run this on a virtual environment)
- OpenMPI of any version (*TODO: Remove this as a reuirement*)
- CMake >3.2.0
- `python39-devel` header to allow C++ interfacing with Python
- gcc and g++ of any version
### Installation
Simply clone this repository and run `setup.sh` via the following command:
```
./setup.sh
```
## Usage
### Collecting stats on a single clustering
To collect a table of per-cluster statistics for a single clustering, run `stats.py`. `stats.py` takes in the following arguments:
- `-i` or `--input`: The whole network that was clustered. This is a 2-column `.tsv` containing an edge list.
- `-e` or `--existing-clustering`: The clustering to report statistics. This is a 2-column `.tsv` containing `node_id, cluster_id` pairs.
- `-c` or `--clusterer`: The clustering algorithm used. Choose from `leiden, leiden_mod, ikc`.
- `-k` or `--k`: _Only required if the clusterer is IKC_. The `k` parameter used with IKC.
- `-g` or `--resolution`: _Only required if the clusterer is Leiden or Leiden with Modularity (leiden_mod)_. The resolution parameter used with Leiden.
  
So if I want to analyse a Leiden resolution 0.01 clustering of CEN, I simply run the following command.
```
python3 stats.py -i cen_cleaned.tsv -e cen_leiden.01_nontree_n10_clusters_cm.txt -c leiden -g 0.01
```
### Returning k-truss nodes
Simply take the same command from `stats.py` and replace `stats.py` with `ktrusses.py`. Here is a command to get the k-truss nodes from the statistics output from above:
```
python3 ktrusses.py -i cen_cleaned.tsv -e cen_leiden.01_nontree_n10_clusters_cm.txt -c leiden -g 0.01
```
## Outputs
### `stats.py`
Output will be in the form of a table stored in a file called `{clustering_name}_stats.csv`. Each row will contain stats on a single cluster. The final row will contain overall statistics, inclusing number of nodes and edges in the network and total modularity and Constant-Potts Model (CPM) score. Each row will have the following measures:
- `cluster`: cluster ID
- `n`: number of nodes in the cluster
- `m`: number of edges in the cluster
- `modularity`
- `cpm_score`
- `connectivity`: size of the minimum cut in the cluster
- `connectivity_normalized`: mincut divided by $log_{10}n$
- `conductance`
- `max_ktruss`: largest $k$ such that there exists a subgraph such that every edge is adjacent to $k-2$ triangles.
### `ktrusses.py`
This will be a three column table in a file called `{clustering_name}_ktruss.csv`. The three columns are:
- `cluster`
- `ktruss_vals`: The value of k (this will repeat for as many rows as there are nodes in the k-truss
- `ktruss_nodes`: The node in the max k-truss of the cluster

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
### `stats.py`: Collecting stats on a single clustering
To collect a table of per-cluster statistics for a single clustering, run `stats.py`. `stats.py` takes in the following arguments:
- `-i` or `--input`: The whole network that was clustered. This is a 2-column `.tsv` containing an edge list.
- `-e` or `--existing-clustering`: The clustering to report statistics. This is a 2-column `.tsv` containing `node_id, cluster_id` pairs.
- `-c` or `--clusterer`: The clustering algorithm used. Choose from `leiden, leiden_mod, ikc`.
- `-k` or `--k`: _Only required if the clusterer is IKC_. The `k` parameter used with IKC.
- `-g` or `--resolution`: _Only required if the clusterer is Leiden or Leiden with Modularity (leiden_mod)_. The resolution parameter used with Leiden.
- `-ub` or `--universal-before`: The `before.json` file that results from CM2Universal in CM/CM++
  
So if I want to analyse a Leiden resolution 0.01 clustering of CEN, I simply run the following command.
```
python3 stats.py -i cen_cleaned.tsv -e cen_leiden.01_nontree_n10_clusters_cm.txt -c leiden -g 0.01
```
### `ktrusses.py`: Returning k-truss nodes
Simply take the same command from `stats.py` and replace `stats.py` with `ktrusses.py`. Here is a command to get the k-truss nodes from the statistics output from above:
```
python3 ktrusses.py -i cen_cleaned.tsv -e cen_leiden.01_nontree_n10_clusters_cm.txt -c leiden -g 0.01
```
### `summarize.py`: Getting the summary of a single clustering
To get a summary of a single clustering using a `stats.py` output file as input, and it will return statistics for the overall clustering. The command format is as follows:
```
python3 summarize.py {stats_output.csv}
```
So for the above example, you would run:
```
python3 summarize.py cen_leiden.01_nontree_n10_clusters_cm_stats.csv
```
### `batch.sh`: Getting a table of summary statistics for a batch of clusters
If you have multiple clustering files that you want to get a table of summary statistics on, you can run `batch.sh`. First you will need to modify `config.tsv` to contain 3 columns in this order from left to right:
- clustering
- resolution
- clusterer
The following is an example `config.tsv`:
```
../benchmarks/citp_post01.tsv   0.1     leiden  
../benchmarks/citp_post001.tsv  0.001   leiden
../benchmarks/citp_pre01.tsv    0.1     leiden
../benchmarks/citp_pre001.tsv   0.001   leiden
```
This will make `batch.sh` run on a batch of four Leiden clusterings on CIT across two resolutions. Now you can run `batch.sh` using the following command format:
```
./batch.sh {network} {output directory (Optional: defaults to current directory)}
```
Here is an example command:
```
./batch.sh cen_cleaned.tsv
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
### `stats.py` `-ub` Output
When you run `stats.py` with the `-ub` tag containing the `before.json` file from CM2Universal, we get two extra outputs:
- **CSV**: A table with the 4 fields:
    - `input_cluster`: The (non-extant) pre-CM++ cluster (this value can repeat)
    - `n`: The size of the cluster (this value can repeat)
    - `descendant`: The post-CM++ cluster that results from this input cluster
    - `desc_n`: The size of the post-CM++ cluster
- **JSON**: It's an array where each entry has the following fields:
    - `input_cluster`
    - `n`
    - `descendants`: an array with each element containing (k, v) pairs where the key is the descendant cluster id and the value is the size of the descendant cluster.
### `ktrusses.py`
This will be a three column table in a file called `{clustering_name}_ktruss.csv`. The three columns are:
- `cluster`
- `ktruss_vals`: The value of k (this will repeat for as many rows as there are nodes in the k-truss
- `ktruss_nodes`: The node in the max k-truss of the cluster
### `summarize.py`
This output will be in the form of a series containing the following fields in this order:
- `modularity`: sum of modularity scores across clusters
- `cpm_score`: sum of CPM scores
- `mincuts_{min,q1,med,q3,max}`: these 5 separate values contain a distribution of mincut sizes
- `mincuts_{min,q1,med,q3,max}_normalized`: same by normalized by $log_{10}n$ where $n$ is per cluster
### `batch.sh`
`batch.sh` will first run `stats.py` on each clustering in the batch, and then run `batch_stats.py` on the group of outputs. This means we will have as many `stats.py` outputs as there are lines in `config.tsv`, and we will also have a table of summary statistics that are indexed by the clustering file name, having the following columns:
- `network`: the entire network being clustered (will repeat)
- `num_clusters`: number of clusters in the clustering
- `network_n`: the number of nodes in the network
- `network_m`: the number of edges in the network
- `total_n`: the total number of nodes across the clusters
- `total_n`: the total number of edges across the clusters
- `{min,q1,med,mean,q3,max}_cluster`: the distribution of cluster sizes in the clustering
- `modularity`: total modularity across all clusters in the clustering
- `modularity_{min,q1,med,mean,q3,max}`: distribution of modularities
- `cpm_score`: total cpm score in the clustering
- `cpm_{min,q1,med,mean,q3,max}`: distribution of cpms
- `conductance_{min,q1,med,mean,q3,max}`: distribution of conductance scores
- `mincuts_{min,q1,med,q3,max}`: these 5 separate values contain a distribution of mincut sizes
- `mincuts_{min,q1,med,q3,max}_normalized`: same by normalized by $log_{10}n$ where $n$ is per cluster

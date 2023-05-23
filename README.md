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

#!/bin/bash
global_graph=$1

# Read the specified column into a shell array
clusterings=($(awk -F' ' '{print $1}' config.tsv))
resolutions=($(awk -F' ' '{print $2}' config.tsv))
clusterers=($(awk -F' ' '{print $3}' config.tsv))

# Print the elements of the array
arr_length=(${#clusterers[@]})
for ((index=0; index<$arr_length; index++))
do
    clustering="${clusterings[index]}"
    resolution="${resolutions[index]}"
    clusterer="${clusterers[index]}"

    python3 stats.py -i $global_graph -e $clustering -c $clusterer -g $resolution
done
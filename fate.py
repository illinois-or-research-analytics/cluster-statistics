import typer
import json

import pandas as pd

from os import path

def compute_ratio(row):
    ''' Compute the ratio of descendant size to input cluster size '''
    if row['extant']:
        return 1
    return int(row['descendant_cluster_size'])/int(row['input_cluster_size'])

def calc_fate(row):
    ''' Compute cluster fate

    parameters
    ----------
    row: DataFrame row containing cluster information

    returns
    -------
    The cluster fate of the input cluster

    Cluster fate can be:
        - extant: The cluster wasn't touched by CM or post-CM filtration
        - degraded: The cluster was completely dissolved by the post-CM 
        - reduced: The cluster was reduced in size by CM
        - split: The cluster resulted in multiple active descendant clusters
    '''
    if row['extant']:
        return 'extant'
    
    n = row['num_active_descendants']
    if n == 0:
        return 'degraded'
    elif n == 1:
        return 'reduced'
    else:
        return 'split'

def main(
    universal_before: str = typer.Option(..., "--universal-before", "-ub", 
        help='The before.json file that resulted from CM2Universal'),
    clustering_file: str = typer.Option(..., "--existing-clustering", "-e", 
        help='Existing clustering: MUST be post-cm filtering'),
    output_file: str = typer.Option("", "--output", "-o", 
        help='(Optional) The name of the output file. Will default to being stored in the same directory as the existing clustering')
):
    # Handle empty output file
    if output_file == "":
        name, _ = path.splitext(clustering_file)
        output_file = name + '_cluster_fate.csv'

    # Construct cluster size table
    clustering = pd.read_csv(clustering_file, header=None, names=['node_id', 'cluster_id'], sep='\t')
    desc_cluster_sizes = clustering.groupby('cluster_id').size().reset_index(name='node_count')

    # Construct table from before.json
    with open(universal_before) as json_file:
        data = json.load(json_file)
        ub_data = pd.DataFrame(data)

    # Refine CM2Universal table
    ub_data['input_cluster_size'] = ub_data['nodes'].apply(lambda x: len(x))
    ub_data['active_descendants'] = ub_data['descendants'].apply(lambda x: [elem for elem in x if elem in desc_cluster_sizes['cluster_id'].tolist()])
    ub_data['num_active_descendants'] = ub_data['active_descendants'].apply(lambda x: len(x))
    ub_data['active_descendants'] = ub_data['active_descendants'].apply(lambda x: [None] if len(x) == 0 else x)

    # Drop unneeded fields and bring arrray columns into multiple rows
    before_table = ub_data[['label', 'input_cluster_size', 'active_descendants', 'num_active_descendants', 'extant']]
    before_table = before_table.explode('active_descendants').reset_index(drop=True)

    # Perform a table join
    final_table = pd.merge(before_table, desc_cluster_sizes, left_on='active_descendants', right_on='cluster_id', how='outer')
    final_table.rename(columns={'node_count': 'descendant_cluster_size', 'label': 'input_cluster'}, inplace=True)
    final_table = final_table.drop('cluster_id', axis=1)
    final_table = final_table[final_table['extant'].notna()]

    # Calculate size ratios
    final_table['size_ratio'] = final_table.apply(compute_ratio, axis=1)

    # Calculate input cluster fate
    final_table['fate'] = final_table.apply(calc_fate, axis=1)

    # Write to csv
    final_table.to_csv(output_file, index=False)

def entry_point():
    typer.run(main)

if __name__ == "__main__":
    entry_point()
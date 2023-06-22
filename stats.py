import typer
import networkit as nk
import pandas as pd
import os
import json

from enum import Enum
from numpy import log10

from clusterers.abstract_clusterer import AbstractClusterer
from clusterers.ikc_wrapper import IkcClusterer
from clusterers.leiden_wrapper import LeidenClusterer, Quality
from graph import Graph, IntangibleSubgraph, RealizedSubgraph
from mincut import viecut

class ClustererSpec(str, Enum):
    """ (VR) Container for Clusterer Specification """  
    leiden = "leiden"
    ikc = "ikc"
    leiden_mod = "leiden_mod"

def main(
    input: str = typer.Option(..., "--input", "-i"),
    existing_clustering: str = typer.Option(..., "--existing-clustering", "-e"),
    clusterer_spec: ClustererSpec = typer.Option(..., "--clusterer", "-c"),
    k: int = typer.Option(-1, "--k", "-k"),
    resolution: float = typer.Option(-1, "--resolution", "-g"),
    noktruss: bool = typer.Option(False, "--noktruss", "-n"),
    universal_before: str = typer.Option("", "--universal-before", "-ub"),
    output: str = typer.Option("", "--output", "-o")
): 
    if output == "":
        base, ext = os.path.splitext(existing_clustering)
        outfile = base + '_stats.csv'
    else:
        outfile = output

    print("Loading clusters...")
    # (VR) Check -g and -k parameters for Leiden and IKC respectively
    if clusterer_spec == ClustererSpec.leiden:
        assert resolution != -1, "Leiden requires resolution"
        clusterer = LeidenClusterer(resolution)
    elif clusterer_spec == ClustererSpec.leiden_mod:
        assert resolution == -1, "Leiden with modularity does not support resolution"
        clusterer = LeidenClusterer(resolution, quality=Quality.modularity)
    else:
        assert k != -1, "IKC requires k"
        clusterer = IkcClusterer(k)

    clusters = clusterer.from_existing_clustering(existing_clustering)
    ids = [cluster.index for cluster in clusters]
    ns = [cluster.n() for cluster in clusters]
    print("Done")

    print("Loading graph...")
    # (VR) Load full graph into Graph object
    edgelist_reader = nk.graphio.EdgeListReader("\t", 0)
    nk_graph = edgelist_reader.read(input)

    global_graph = Graph(nk_graph, "")
    ms = [cluster.count_edges(global_graph) for cluster in clusters]
    print("Done")

    # clusters = [cluster.realize(global_graph) for cluster in clusters]

    print("Computing modularity...")
    modularities = [global_graph.modularity_of(cluster) for cluster in clusters]
    print("Done")

    if resolution != -1:
        print("Computing CPM score...")
        cpms = [global_graph.cpm(cluster, resolution) for cluster in clusters]
        print("Done")

    print("Realizing clusters...")
    clusters = [cluster.realize(global_graph) for cluster in clusters]
    print("Done")

    print("Computing mincut...")
    mincut_results = [viecut(cluster) for cluster in clusters]
    mincuts = [result.get_cut_size() for result in mincut_results]
    mincuts_normalized = [mincut/log10(ns[i]) for i, mincut in enumerate(mincuts)]
    print("Done")

    print("Computing conductance...")
    conductances = []
    for i, cluster in enumerate(clusters):
        conductances.append(cluster.conductance(global_graph))
    print("Done")

    if not noktruss:
        print("Computing k-truss...")
        ktruss_vals = [cluster.ktruss() for cluster in clusters]
        print("Done")

    print("Computing overall stats...")
    m = global_graph.m()
    ids.append("Overall")
    modularities.append(sum(modularities))

    if resolution != -1:
        cpms.append(sum(cpms))


    ns.append(global_graph.n())
    ms.append(m)
    mincuts.append(None)
    mincuts_normalized.append(None)
    if not noktruss:
        ktruss_vals.append(None)
    conductances.append(None)
    # ktruss_nodes.append(None)
    print("Done")

    print("Writing to output file...")

    if resolution != -1:
        if not noktruss:
            df = pd.DataFrame(list(zip(ids, ns, ms, modularities, cpms, mincuts, mincuts_normalized, conductances, ktruss_vals)),
                    columns =['cluster', 'n', 'm', 'modularity', 'cpm_score', 'connectivity', 'connectivity_normalized', 'conductance', 'max_ktruss'])
        else:
            df = pd.DataFrame(list(zip(ids, ns, ms, modularities, cpms, mincuts, mincuts_normalized, conductances)),
                    columns =['cluster', 'n', 'm', 'modularity', 'cpm_score', 'connectivity', 'connectivity_normalized', 'conductance'])
    else:
        if not noktruss:
            df = pd.DataFrame(list(zip(ids, ns, ms, modularities, mincuts, mincuts_normalized, conductances, ktruss_vals)),
                    columns =['cluster', 'n', 'm', 'modularity', 'connectivity', 'connectivity_normalized', 'conductance', 'max_ktruss'])
        else:
            df = pd.DataFrame(list(zip(ids, ns, ms, modularities, mincuts, mincuts_normalized, conductances)),
                    columns =['cluster', 'n', 'm', 'modularity', 'connectivity', 'connectivity_normalized', 'conductance'])

    df.to_csv(outfile, index=False)
    print("Done")

    if len(universal_before) > 0:
        print("Writing extra outputs from CM2Universal")

        cluster_sizes = {key.replace('"', ''): val for key, val in zip(ids, ns)}
        
        output_entries = []
        with open(universal_before) as json_file:
            before = json.load(json_file) 
            for cluster in before:
                if not cluster['extant']:
                    output_entries.append({
                        "input_cluster": cluster['label'],
                        'n': len(cluster['nodes']),
                        'descendants': {
                            desc: cluster_sizes[desc]
                            for desc in cluster['descendants']
                            if desc in cluster_sizes
                        }
                    })

        # Specify the file path for the JSON output
        json_file_path = outfile + '_to_universal.json'
        csv_file_path = outfile + '_to_universal.csv'

        # Get lines for the csv format
        csv_lines = ['input_cluster,n,descendant,desc_n']
        for entry in output_entries:
            if len(entry['descendants']) == 0:
                csv_lines.append(f'{entry["input_cluster"]},{entry["n"]},,')
            else:
                for descendant, desc_n in entry['descendants'].items():
                    csv_lines.append(f'{entry["input_cluster"]},{entry["n"]},{descendant},{desc_n}')

        print("\tWriting JSON")
        # Write the array of dictionaries as formatted JSON to the file
        with open(json_file_path, 'w') as json_file:
            json.dump(output_entries, json_file, indent=4)
        print("\tDone")

        print("\tWriting CSV")
        # Write the lines to the file
        with open(csv_file_path, 'w') as file:
            for line in csv_lines:
                file.write(line + '\n')
        print("\tDone")
        print("Done")


def entry_point():
    typer.run(main)

if __name__ == "__main__":
    entry_point()
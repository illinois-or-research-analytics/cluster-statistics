import typer
import networkit as nk
import pandas as pd
import os

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
    noktruss: bool = typer.Option(False, "--noktruss", "-n")
): 
    base, ext = os.path.splitext(existing_clustering)
    outfile = base + '_stats.csv'

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

    if not noktruss:
        df = pd.DataFrame(list(zip(ids, ns, ms, modularities, cpms, mincuts, mincuts_normalized, conductances, ktruss_vals)),
                columns =['cluster', 'n', 'm', 'modularity', 'cpm_score', 'connectivity', 'connectivity_normalized', 'conductance', 'max_ktruss'])
    else:
        df = pd.DataFrame(list(zip(ids, ns, ms, modularities, cpms, mincuts, mincuts_normalized, conductances)),
                columns =['cluster', 'n', 'm', 'modularity', 'cpm_score', 'connectivity', 'connectivity_normalized', 'conductance'])

    df.to_csv(outfile, index=False)
    print("Done")

def entry_point():
    typer.run(main)

if __name__ == "__main__":
    entry_point()
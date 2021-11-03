import graphviz
import networkx as _nx

from graph.artist_graph import InternalGraph
from utils.profile import profile


@profile
def _get_dot_source(graph):
    return _nx.nx_pydot.to_pydot(graph.g).to_string()


@profile
def _test_render(graph, path):
    graph.gg.render(f"{path}cc")


@profile
def _save_graphviz(graph, path):
    graph.gg.save(path)
    graph.gg.render(path, format="png")


@profile
def _save_networkx(graph, path):
    _nx.nx_pydot.to_pydot(graph.g).write_dot(f"{path}cc")


@profile
def visualize_graph(graph: InternalGraph, path: str):
    _save_graphviz(graph, path)
    _save_networkx(graph, path)

    # _test_render(graph, path)
    #
    # PG = graphviz.Source(_get_dot_soruce(graph))
    # PG.render(path)

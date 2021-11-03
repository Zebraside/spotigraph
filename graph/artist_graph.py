from typing import Iterable
import networkx as _nx
import graphviz
from common.artist import Artist
from utils.profile import profile


class InternalGraph:
    def __init__(self, artists: Iterable[Artist], connections: Iterable):
        self.g = _nx.Graph()
        self.gg = graphviz.Graph()

        self.create_nodes(artists)
        self.create_edges(connections)

    @profile
    def create_nodes(self, artists: Iterable[Artist]):
        for artist in artists:
            self.g.add_node(artist.spotify_id, label=artist.name)
            self.gg.node(artist.spotify_id)

    @profile
    def create_edges(self, connections: Iterable):
        for connection in connections:
            self.g.add_edge(connection[0], connection[1])
            self.gg.edge(connection[0], connection[1])

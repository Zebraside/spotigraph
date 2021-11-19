import os
from typing import Iterable
import networkx as _nx
import graphviz
from common.artist import Artist
from utils.profile import profile
import igraph
import tqdm
from multiprocessing import Pool



class InternalGraph:
    def __init__(self, artists: Iterable[Artist], connections: Iterable):
        self.g = igraph.Graph()
        self.gg = graphviz.Graph()

        self.create_nodes(artists)
        self.create_edges(connections)

    @profile
    def create_nodes(self, artists: Iterable[Artist]):
        for artist in artists:
            self.g.add_vertex(name=artist.spotify_id,
                              label=artist.name,
                              artist_name=artist.spotify_id,
                              followers=artist.followers,
                              popularity=artist.popularity)

            self.gg.node(artist.spotify_id, artist.name)

    @profile
    def create_edges(self, connections: Iterable):
        global vertices
        vertices = set(self.g.vs["name"])

        def have_data(conn):
            if conn[0] not in vertices or conn[1] not in vertices:
                return None
            else:
                return conn

        result = [have_data(conn) for conn in tqdm.tqdm(connections)]

        result = [x for x in result if x is not None]
        self.g.add_edges(tqdm.tqdm(result))

        for edge in tqdm.tqdm(result):
            self.gg.edge(edge[0], edge[1])

        # result = [f"{conn[0]}{conn[1]}" for conn in result]
        # self.gg.edges(result)
        # for connection in tqdm.tqdm(connections):
        #     if connection[0] not in vertices or connection[1] not in vertices:
        #         continue


    @profile
    def export(self, out_folder):
        file_name = "graph.png"
        self.gg.save("graph.dot", out_folder)
        #self.gg.render(os.path.join(out_folder, "graph.gv"), view=True, format='png', renderer='svg')


        igraph.drawing.plot(self.g,
                            os.path.join(out_folder, "reingold.png"),
                            bbox=(0, 0, 10000, 10000),
                            layout=self.g.layout_fruchterman_reingold())

        igraph.drawing.plot(self.g,
                            os.path.join(out_folder, "circle.png"),
                            bbox=(0, 0, 10000, 10000),
                            layout=self.g.layout_circle())

        igraph.drawing.plot(self.g,
                            os.path.join(out_folder, "star.png"),
                            bbox=(0, 0, 10000, 10000),
                            layout=self.g.layout_star())

        igraph.drawing.plot(self.g,
                            os.path.join(out_folder, "auto.png"),
                            bbox=(0, 0, 10000, 10000),
                            layout=self.g.layout_auto())

        igraph.drawing.plot(self.g,
                            os.path.join(out_folder, "grid.png"),
                            bbox=(0, 0, 10000, 10000),
                            layout=self.g.layout_grid())


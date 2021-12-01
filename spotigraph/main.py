from spotigraph.db import ASpotifyDB as SpotifyDB

from spotigraph.graph.artist_graph import InternalGraph
from spotigraph.graph import visualize_graph


if __name__ == '__main__':
    db = SpotifyDB()

    artists = db.get_artists()
    connections = db.get_relations()

    graph = InternalGraph(artists, connections)
    visualize_graph(graph, "data")

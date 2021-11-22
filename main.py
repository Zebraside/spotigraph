import sqlite3
import click
import yaml
from db.alchemy_spotify_db import ASpotifyDB as SpotifyDB

from graph.artist_graph import InternalGraph
from graph.visualization import visualize_graph


if __name__ == '__main__':
    config = None
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    db = SpotifyDB(config)

    artists = db.get_artists()
    connections = db.get_relations()

    graph = InternalGraph(artists, connections)
    visualize_graph(graph, "C:\\Development\\spotigraph")

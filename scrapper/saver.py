import ast

import json

from scrapper.queues import ArtistQueue, ScrapperQueue
from db.alchemy_spotify_db import ASpotifyDB as SpotifyDB
from common.artist import Artist

from utils.profile import profile


class ArtistSaver:
    def __init__(self):
        self.artists_queue = ArtistQueue(self._handle_artist)
        self.scrapper_queue = ScrapperQueue()

        # Init database
        self.db = SpotifyDB()

    def _save_artist(self, artist: Artist):
        artist_id = artist.spotify_id

        if self.db.check_artist_exists(artist_id):
            return

        self.db.add_artist(artist)

    def _save_related(self, artist_id, related_ids):
        self.db.add_relations(artist_id, related_ids)

    @profile
    def _handle_artist(self, ch, method, properties, body):
        body = body.decode("utf-8")

        artist = ast.literal_eval(body)

        related_ids = artist.pop("related_ids")
        artist = Artist(**artist)

        self._save_artist(artist)
        self._save_related(artist.spotify_id, related_ids)

        new_ids = [new_id for new_id in related_ids if not self.db.check_artist_exists(new_id)]

        print("Pushing new", len(new_ids))
        for new_id in new_ids:
            self.scrapper_queue.push(new_id)

    def start(self):
        self.artists_queue.start_consuming()

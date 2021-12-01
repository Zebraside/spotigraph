import time
import ast

from spotigraph.scrapper.queues import ArtistConsumer, ScraperPublisher, MetricsPublisher
from spotigraph.db.alchemy_spotify_db import ASpotifyDB as SpotifyDB
from spotigraph.common.artist import Artist

from spotigraph.utils.profile import profile


class ArtistSaver:
    def __init__(self):
        self.artists_queue = ArtistConsumer(self._handle_artist)
        self.scrapper_queue = ScraperPublisher()
        self.save_queue = MetricsPublisher("save")

        # Init database
        self.db = SpotifyDB()

        self.time = None
        self.counter = 0

    def _save_artist(self, artist: Artist):
        artist_id = artist.spotify_id

        if self.db.check_artist_exists(artist_id):
            return

        self.db.add_artist(artist)
        self.save_queue.push(str(time.time()))

    def _save_related(self, artist_id, related_ids):
        self.db.add_relations(artist_id, related_ids)

    @profile
    def _handle_artist(self, body):
        if self.time is None:
            self.time = time.time()

        self.counter += 1
        self.new_time = time.time()
        if time.time() - self.time > 10:
            print(f"Added new {self.counter} entities. Took {self.new_time - self.time} sec")
            self.time = self.new_time
            self.counter = 0

        body = body.decode("utf-8")

        artist = ast.literal_eval(body)

        related_ids = artist.pop("related_ids")
        artist = Artist(**artist)

        self._save_artist(artist)
        self._save_related(artist.spotify_id, related_ids)

        new_ids = [new_id for new_id in related_ids if not self.db.check_artist_exists(new_id)]

        # print("Pushing new", len(new_ids))
        for new_id in new_ids:
            self.scrapper_queue.push(new_id)

    def start(self):
        self.artists_queue.start_consuming()

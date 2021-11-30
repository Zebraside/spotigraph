import time

from config import InjectionConfig
from scrapper.queues import ScraperPublisher
from db.alchemy_spotify_db import ASpotifyDB as SpotifyDB

from utils.profile import profile


class Injector:
    def __init__(self):
        self.scrapper_queue = ScraperPublisher()

        self.injection_count = InjectionConfig.INJECTION_COUNT
        self.injection_delay_sec = InjectionConfig.INJECTION_DELAY_SEC
        # Init database
        self.db = SpotifyDB()

    @profile
    def _inject(self):
        print("Injection")
        artists, potential = zip(*self.db.get_relations())
        artists = set(artists)
        potential = set(potential)
        diff = list(potential.difference(artists))[:self.injection_count]
        for d in diff:
            self.scrapper_queue.push(d)

    def start(self):
        while True:
            self._inject()
            time.sleep(self.injection_delay_sec)

import logging
import time

from db.alchemy_spotify_db import ASpotifyDB as SpotifyDB


class Monitoring:
    def __init__(self, interval: int = 10):
        # interval in sec
        self.db = SpotifyDB()
        self.interval = interval

        self.last_value = None

    def ping(self):
        new_value = self.db.get_num_artist()
        print(f"Current number of artists is {new_value}. Delta is {new_value - self.last_value}")
        self.last_value = new_value

    def run(self):
        self.last_value = self.db.get_num_artist()
        while True:
            self.ping()
            time.sleep(self.interval)


if __name__ == "__main__":
    monitor = Monitoring()
    monitor.run()

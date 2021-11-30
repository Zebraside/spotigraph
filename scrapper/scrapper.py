import dataclasses
from typing import List
import logging

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

from scrapper.queues import ArtistQueue, ScrapperQueue
from db.alchemy_spotify_db import ASpotifyDB as SpotifyDB
from common.artist import Artist

from utils.profile import Performer, profile


class SpotifyScrapper:
    def __init__(self, initial_artist: str = None):
        # init message queues
        self.scrapper_queue = ScrapperQueue(self._handle_artist)
        self.artists_queue = ArtistQueue()

        # Init Spotify api
        client_credentials_manager = SpotifyClientCredentials()
        self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Init database
        self.db = SpotifyDB()

        if initial_artist:
            self._push_new_artists([initial_artist])

    @staticmethod
    def _parse_artist(artist_result):
        return Artist(name=artist_result["name"],
                      spotify_id=artist_result["id"],
                      followers=artist_result["followers"]["total"],
                      popularity=artist_result["popularity"],
                      genres=artist_result["genres"])

    @profile
    def _get_related_artists(self, artist_id) -> List[Artist]:
        try:
            req = Performer("get related requrest")
            result = self.spotify.artist_related_artists(f'spotify:artist:{artist_id}')
            req.elapsed()
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"Can't get related artists: artist_id {artist_id}")
            return []

        # TODO: only return related ids
        artists = [self._parse_artist(artist) for artist in result["artists"]]
        return [artist for artist in artists if artist is not None]

    @profile
    def _get_artist(self, artist_id: str):
        result = None
        try:
            result = self.spotify.artist(f'spotify:artist:{artist_id}')
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"Can't get information about artist: artist_id {artist_id}")

        if result:
            return self._parse_artist(result)

        return None

    @profile
    def _handle_artist(self, ch, method, properties, body):
        artist_id = body.decode("utf-8")
        logging.debug(f"New artist {artist_id}")

        # if self.db.check_artist_exists(artist_id):
        #     return

        artist = self._get_artist(artist_id)
        related = self._get_related_artists(artist_id)
        if not artist:
            logging.warning(f"Can't get artist {artist_id}")
            return

        related_ids = [r.spotify_id for r in related]
        self._save_artist(artist, related_ids)

        # new_related_ids = [new_id for new_id in related_ids]
        # self._push_new_artists(new_related_ids)

    @profile
    def _push_new_artists(self, artist_ids):
        for new_id in artist_ids:
            self.scrapper_queue.push(new_id)

    @profile
    def _save_artist(self, artist: Artist, related: List[str]):
        new_artist = dataclasses.asdict(artist)
        new_artist["related_ids"] = related
        self.artists_queue.push(str(new_artist))

    def start(self):
        self.scrapper_queue.start_consuming()

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from typing import List
import sys
from dataclasses import dataclass
import pprint
import logging
from threading import Thread
import pika
import time
import click
import yaml
import asyncio

from common.artist import Artist
from db.alchemy_spotify_db import ASpotifyDB as SpotifyDB

from utils.profile import profile

logging.basicConfig(level=logging.ERROR)


class Performer:
    def __init__(self, tag: str = ""):
        self.start_time = time.time()
        self.loop_time = self.start_time

        self.tag = tag

        logging.debug(f"Start measuring {tag}")

    def restart(self):
        self.start_time = time.time()
        self.loop_time = self.start_time

    def section(self, section_tag):
        current_time = time.time()
        logging.debug(
            f"{self.tag}:{section_tag}: Section time: {current_time - self.loop_time}")

        self.loop_time = current_time

    def elapsed(self):
        current_time = time.time()
        logging.debug(
            f"{self.tag}: Total time: {current_time - self.start_time}")


class CrowlerWorker:
    def __init__(self, config):
        # Init RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()

        self.channel.queue_declare(queue='task_queue', durable=True)

        self.channel.basic_consume(queue='task_queue', on_message_callback=self.handle_artist)

        # Init Spotify api
        client_credentials_manager = SpotifyClientCredentials()
        self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Init database
        self.db = SpotifyDB(config)

    def _get_related_artists(self, artist_id) -> List[Artist]:
        result = None
        try:
            req = Performer("get related requrest")
            result = self.spotify.artist_related_artists(f'spotify:artist:{artist_id}')
            req.elapsed()
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"Can't get related artists: artist_id {artist_id}")

        if result:
            artists = [self._parse_artist(artist) for artist in result["artists"]]
            return [artist for artist in artists if artist is not None]

        return []

    def _get_artist(self, artist_id: str):
        result = None
        try:
            result = self.spotify.artist(f'spotify:artist:{artist_id}')
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"Can't get information about artist: artist_id {artist_id}")

        if result:
            return self._parse_artist(result)

        return None

    @staticmethod
    def _parse_artist(artist_result):
        return Artist(name=artist_result["name"],
                      spotify_id=artist_result["id"],
                      followers=artist_result["followers"]["total"],
                      popularity=artist_result["popularity"],
                      genres=artist_result["genres"])

    def _check_visited(self, artist_id):
        return self.db.check_artist_exists(artist_id)

    def _push_artist(self, artist_id: str):
        self.channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=str.encode(artist_id),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    @profile
    def get_artist_info(self, artist_id):
        return self._get_artist(artist_id), self._get_related_artists(artist_id)

    async def test(self):
        print("Test")

    @profile
    def save_artist(self, artist, related_artists):
        artist_id = artist.spotify_id
        if self._check_visited(artist_id):
            return []

        self.db.add_artist(artist)

        related_ids = [related.spotify_id for related in related_artists]

        self.db.add_relations(artist_id, related_ids)

        new = []
        for related in related_artists:
            if self._check_visited(related.spotify_id):
                continue

            new.append(related.spotify_id)
        return new

    @profile
    def push_new(self, new):
        for n in new:
            self._push_artist(n)

    def handle_artist(self, ch, method, properties, body):
        print("handle")
        artist_id = body.decode("utf-8")
        artist, related_artists = self.get_artist_info(artist_id)
        new = self.save_artist(artist, related_artists)
        self.push_new(new)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.start_consuming()


def send_test_message(artist_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    message = artist_id
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    print(" [x] Sent %r" % message)
    connection.close()


def start_listening(config):

    consumer = CrowlerWorker(config)
    consumer.start()


@click.command()
@click.option('--num_workers', default=1, help='number of parallel workers')
@click.option('--initial_artist_id', default="3jOstUTkEu2JkjvRdBA5Gu", help='artist spotify id to start search')
def main(num_workers, initial_artist_id):
    send_test_message(initial_artist_id)
    config = dict()
    with open("C:\\Dev\\spotigraph\\config.yaml", "r") as f:
        config = yaml.safe_load(f)

    for i in range(num_workers):
        new_thread = Thread(target=start_listening, args=(config, ))
        new_thread.start()


if __name__ == "__main__":
    main()

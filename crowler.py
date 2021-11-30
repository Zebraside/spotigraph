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
from multiprocessing import Pool

from common.artist import Artist
from db.alchemy_spotify_db import ASpotifyDB as SpotifyDB

from utils.profile import profile

logging.basicConfig(level=logging.ERROR)

index=0

DURABLE=True
QUEUE_NAME=f"task_queue:{index}"





class CrowlerWorker:
    def __init__(self):
        # Init RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()
        self.channel.basic_qos(prefetch_count=100)
        self.channel.queue_declare(queue=QUEUE_NAME, durable=DURABLE)

        self.channel.basic_consume(queue=QUEUE_NAME, on_message_callback=self.handle_artist, auto_ack=True)

        # Init Spotify api
        client_credentials_manager = SpotifyClientCredentials()
        self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Init database
        self.db = SpotifyDB()

        self.pool = Pool(2)

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
            routing_key=QUEUE_NAME,
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
            if self._check_visited(n):
                continue

            self._push_artist(n)

    def handle_artist(self, ch, method, properties, body):
        print("handle")
        artist_id = body.decode("utf-8")

        if self._check_visited(artist_id):
            print("already visited")
            #ch.basic_ack()
            return

        artist, related_artists = self.get_artist_info(artist_id)
        new = self.save_artist(artist, related_artists)
        self.push_new(new)

        #ch.basic_ack()

    def start(self):
        self.channel.start_consuming()


def send_test_message(artist_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    queue = channel.queue_declare(queue=QUEUE_NAME, durable=DURABLE)

    message = artist_id
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=message,
        properties=pika.BasicProperties(
            #delivery_mode=0,  # make message persistent
        ))
    print(" [x] Sent %r" % message, queue.method.message_count)
    connection.close()


def start_listening():

    consumer = CrowlerWorker()
    consumer.start()


def random_injection(config):
    db = SpotifyDB(config)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    queue = channel.queue_declare(queue=QUEUE_NAME, durable=DURABLE)

    while True:
        logging.info("NEW INJECTION")
        connections = db.get_relations()
        artists = set()
        related = set()
        for conn in connections:
            artists.add(conn[0])
            related.add(conn[1])

        count = 10
        for r in related:
            if count <= 0:
                break
            if r not in artists:
                channel.basic_publish(
                    exchange='',
                    routing_key=QUEUE_NAME,
                    body=r,
                    properties=pika.BasicProperties(
                        # delivery_mode=0,  # make message persistent
                    ))

        time.sleep(10)


def clean_queue(config):
    db = SpotifyDB(config)
    count = 0
    err = False
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    queue = channel.queue_declare(queue=QUEUE_NAME, durable=DURABLE)

    channel.basic_qos(prefetch_count=100)


    def clean(ch, method, properties, body):
        print("clean")
        artist_id = body.decode("utf-8")

        if db.check_artist_exists(artist_id):
            print("Duplicated artist removed")
            return

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=body,
            properties=pika.BasicProperties(
                # delivery_mode=0,  # make message persistent
            ))

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=clean, auto_ack=True)
    channel.start_consuming()


@click.command()
@click.option('--num_workers', default=1, help='number of parallel workers')
@click.option('--initial_artist_id', default="3jOstUTkEu2JkjvRdBA5Gu", help='artist spotify id to start search')
def main(num_workers, initial_artist_id):
    start_artists=["126FigDBtqwS2YsOYMTPQe", "3LC8PXXgk7YtAIobtjSdNi", "4ghjRm4M2vChDfTUycx0Ce"]
    send_test_message(start_artists[index])
    config = dict()
    with open("C:\\Development\\spotigraph\\config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # clean_queue(config)

    new_thread = Thread(target=random_injection, args=(config,))
    new_thread.start()

    while True:
        print("start")
        try:
            if num_workers > 1:
                for i in range(num_workers):
                    new_thread = Thread(target=start_listening, args=(config, ))
                    new_thread.start()
            else:
                start_listening()
        except:
            print("Error occured")


if __name__ == "__main__":
    main()

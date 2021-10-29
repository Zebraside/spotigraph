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

from common.artist import Artist
from db.spotify_db import SpotifyDB


class CrowlerWorker:
    def __init__(self):
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
        self.db = SpotifyDB()


    def _get_related_artists(self, artist_id) -> List[Artist]:
        result = None
        try:
            result = self.spotify.artist_related_artists(f'spotify:artist:{artist_id}')
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"Can't get related artists: artist_id {artist_id}")

        if result:
            artists = [self._get_artist(artist["id"]) for artist in result["artists"]]
            return [artist for artist in artists if artist is not None]

        return []

    def _get_artist(self, artist_id: str):
        result = None
        try:
            result = self.spotify.artist(f'spotify:artist:{artist_id}')
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"Can't get information about artist: artist_id {artist_id}")

        if result:
            return Artist(name=result["name"],
                           spotify_id=result["id"],
                           followers=result["followers"]["total"],
                           popularity=result["popularity"],
                           genres=result["genres"])

        return None

    def _check_visited(self, artist_id):
        return self.db.check_artist_exists(artist_id)

    def _push_artist(self, artist_id: str):
        self.channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=artist_id,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def handle_artist(self, ch, method, properties, body):
        artist_id = body.decode("utf-8")
        if artist_id == "From worker":
            return
        if self._check_visited(artist_id):
            return

        artist = self._get_artist(artist_id)
        self.db.add_artist(artist)

        for related in self._get_related_artists(artist_id):
            if self._check_visited(related.spotify_id):
                continue

            self._push_artist(related.spotify_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.start_consuming()


def send_test_message():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    message = "3jOstUTkEu2JkjvRdBA5Gu"
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    print(" [x] Sent %r" % message)
    connection.close()


def start_listening():
    consumer = CrowlerWorker()
    consumer.start()


if __name__ == "__main__":
    #o = SpotifyCrowler()
    send_test_message()
    for i in range(5):
        new_thread = Thread(target=start_listening)
        new_thread.start()

#    o._get_artist('3jOstUTkEu2JkjvRdBA5Gu')
    #o.crowl('3jOstUTkEu2JkjvRdBA5Gu')
    # try:
    #     name = result['artists']['items'][0]['name']
    #     uri = result['artists']['items'][0]['uri']
    #
    #     related = sp.artist_related_artists(uri)
    #     print('Related artists for', name)
    #     for artist in related['artists']:
    #         print('  ', artist['name'])
    # except BaseException:
    #     print("usage show_related.py [artist-name]")
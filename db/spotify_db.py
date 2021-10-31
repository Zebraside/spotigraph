from typing import List
import sqlite3
import logging


from common.artist import Artist


class SpotifyDB:
    def __init__(self):
        self.conn = sqlite3.connect('C:\\Development\\spotigraph\\data\\spotify.sqlite', timeout=30.0)

    def add_artist(self, artist: Artist):
        cursor = self.conn.cursor()
        try:
            sqlite_insert_query = f"""INSERT INTO "artists" 
                                      (name, spotify_id, popularity, followers)
                                      VALUES  (?, ?, ?, ?);"""

            cursor.execute(sqlite_insert_query, (artist.name, artist.spotify_id, artist.popularity, artist.followers))
            self.conn.commit()

            sql_insert_genre = f"""INSERT INTO "artist_genre" (spotify_id, genre) VALUES (?, ?);"""
            for genre in artist.genres:
                cursor.execute(sql_insert_genre, (artist.spotify_id, genre))
                self.conn.commit()
        except sqlite3.IntegrityError as e:
            logging.warning("Attempt to insert artist that already exists in the DB")

        cursor.close()

    def get_num_artist(self):
        cursor = self.conn.cursor()
        sql = 'SELECT COUNT(*) FROM "artists"'
        cursor.execute(sql)
        number_of_rows = cursor.fetchone()[0]
        cursor.close()
        return number_of_rows

    def add_relation(self, artist_id, related_artist_id):
        cursor = self.conn.cursor()

        sqlite_insert_query = f"""INSERT INTO "connections" 
                                          (artist_id, related_id)
                                          VALUES  (?, ?);"""

        cursor.execute(sqlite_insert_query, (artist_id, related_artist_id))
        self.conn.commit()

        cursor.close()

    def add_relations(self, artist_id, related_ids: List):
        cursor = self.conn.cursor()

        sqlite_insert_query = f"""INSERT INTO "connections" 
                                          (artist_id, related_id)
                                          VALUES  (?, ?);"""

        cursor.executemany(sqlite_insert_query, [(artist_id, related_id) for related_id in related_ids])
        self.conn.commit()

        cursor.close()


    def check_artist_exists(self, artist_id):
        cursor = self.conn.cursor()
        sql = f'SELECT 1 FROM artists WHERE spotify_id = "{artist_id}"'
        cursor.execute(sql)
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists

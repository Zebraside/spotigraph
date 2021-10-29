import sqlite3

from common.artist import Artist


class SpotifyDB:
    def __init__(self):
        self.conn = sqlite3.connect('C:\\Development\\spotigraph\\data\\spotify.sqlite')

    def add_artist(self, artist: Artist):
        cursor = self.conn.cursor()

        sqlite_insert_query = f"""insert into "artists" 
                                  (name, spotify_id, popularity, followers)
                                  VALUES  (?, ?, ?, ?);"""

        cursor.execute(sqlite_insert_query, (artist.name, artist.spotify_id, artist.popularity, artist.followers))
        self.conn.commit()

        cursor.close()

    def check_artist_exists(self, artist_id):
        cursor = self.conn.cursor()
        sql = f'SELECT 1 FROM artists WHERE spotify_id = "{artist_id}"'
        cursor.execute(sql)
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists

from spotigraph.db.schema import AlchemyArtistGenre, AlchemyArtist, AlchemyConnections, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from typing import List
import sqlite3
import logging

from spotigraph.utils.profile import profile

from spotigraph.common.artist import Artist
from spotigraph.config import DB


class ASpotifyDB:
    def __init__(self):
        engine = create_engine(
            f'postgresql://{DB.POSTGRES_NAME}:{DB.POSTGRES_PASS}@{DB.POSTGRES_SERVER}:{DB.POSTGRES_PORT}/{DB.POSTGRES_DB}')

        Base.metadata.bind = engine
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()

    def add_artist(self, artist: Artist):
        try:
            new_person = AlchemyArtist(name=artist.name,
                                       spotify_id=artist.spotify_id,
                                       popularity=artist.popularity,
                                       followers=artist.followers)
            self.session.add(new_person)

            for genre in artist.genres:
                self.session.add(AlchemyArtistGenre(spotify_id=artist.spotify_id,
                                                    genre=genre))

            self.session.commit()
        except sqlite3.IntegrityError as e:
            logging.warning("Attempt to insert artist that already exists in the DB")
        except IntegrityError as e:
            self.session.rollback()
            logging.warning("Attempt to insert artist that already exists in the DB")

    @staticmethod
    def _convert_artist(db_artist: AlchemyArtist):
        return Artist(name=db_artist.name,
                      spotify_id=db_artist.spotify_id,
                      followers=db_artist.followers,
                      popularity=db_artist.popularity,
                      genres=[])

    def get_artists(self):
        try:
            for batch in self.session.query(AlchemyArtist).yield_per(1000):
                yield self._convert_artist(batch)
        except Exception as e:
            logging.error("Can't fetch artist result", e)


    def get_num_artist(self):
        try:
            return self.session.query(AlchemyArtist).count()
        except:
            logging.error("DB get num artists error")

        return 0

    @profile
    def add_relation(self, artist_id, related_artist_id):
        try:
            new_connection = AlchemyConnections(artist_id=artist_id,
                                                related_id=related_artist_id)
            self.session.add(new_connection)
            self.session.commit()
        except Exception as e:
            self.session.rollback()

    @profile
    def add_relations(self, artist_id, related_ids: List):
        try:
            for relation in related_ids:
                new_connection = AlchemyConnections(artist_id=artist_id,
                                                    related_id=relation)
                self.session.add(new_connection)
            self.session.commit()
        except Exception as e:
            self.session.rollback()

    @staticmethod
    def _convert_relation(relation: AlchemyConnections):
        return relation.artist_id, relation.related_id

    def get_relations(self):
        try:
            for batch in self.session.query(AlchemyConnections).yield_per(1000):
                yield self._convert_relation(batch)
        except Exception as e:
            logging.error("Can't fetch connections result", e)

    def check_artist_exists(self, artist_id):
        found = 0
        try:
            found = self.session.query(AlchemyArtist).filter(AlchemyArtist.spotify_id == artist_id).count()
        except PendingRollbackError as e:
            pass
        except Exception as e:
            print(e)
            logging.error("Can't check if artist is already exists")
        return found > 0

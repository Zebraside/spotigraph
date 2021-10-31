import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from typing import List
import sqlite3
import logging

from utils.profile import profile

from common.artist import Artist


Base = declarative_base()


class AlchemyArtistGenre(Base):
    __tablename__ = "artist_genre"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    spotify_id = Column(String(250), nullable=False)
    genre = Column(String(250), nullable=False)


class AlchemyConnections(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    artist_id = Column(String(250), nullable=False)
    related_id = Column(String(250), nullable=False)


class AlchemyArtist(Base):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    spotify_id = Column(String(250), nullable=False)
    popularity = Column(Integer(), nullable=False)
    followers = Column(Integer(), nullable=False)


class ASpotifyDB:
    def __init__(self):
        engine = create_engine('sqlite:///C:/Development/spotigraph/data/spotify.sqlite')
        Base.metadata.bind = engine
        self.session = sessionmaker(bind=engine)()

    def add_artist(self, artist: Artist):
        try:
            new_person = AlchemyArtist(name=artist.name,
                                       spotify_id=artist.spotify_id,
                                       popularity=artist.popularity,
                                       followers=artist.followers)
            self.session.add(new_person)
            self.session.commit()
        except sqlite3.IntegrityError as e:
            logging.warning("Attempt to insert artist that already exists in the DB")
        except IntegrityError as e:
            self.session.rollback()
            logging.warning("Attempt to insert artist that already exists in the DB")

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

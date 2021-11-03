from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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


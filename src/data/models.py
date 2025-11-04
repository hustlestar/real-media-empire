from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

channel_authors = Table(
    "channel_authors", Base.metadata, Column("channel_id", Integer, ForeignKey("channels.id")), Column("author_id", Integer, ForeignKey("authors.id"))
)


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    authors = relationship("Author", secondary=channel_authors, back_populates="channels")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    channels = relationship("Channel", secondary=channel_authors, back_populates="authors")

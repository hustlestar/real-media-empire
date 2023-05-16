# Methods for interacting with the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from data.models import Base, Channel, Author
from config import CONFIG

engine = create_engine(
    f'postgresql://{CONFIG.get("JDBC_USER_NAME")}:{CONFIG.get("JDBC_PASSWORD")}@{CONFIG.get("JDBC_HOST")}:{CONFIG.get("JDBC_PORT")}/{CONFIG.get("JDBC_DATABASE")}')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create(db: Session, model, **kwargs):
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.add(instance)
        db.commit()
        return instance


def add_author(db: Session, name: str) -> Author:
    return get_or_create(db, Author, name=name)


def add_channel(db: Session, name: str) -> Channel:
    return get_or_create(db, Channel, name=name)


def add_author_to_channel(db: Session, channel_name, author_name):
    channel = db.query(Channel).filter_by(name=channel_name).first()
    author = get_or_create(db, Author, name=author_name)
    if channel and author:
        channel.authors.append(author)
        db.commit()


def is_author_used_in_channel(db: Session, channel_name, author_name):
    channel = db.query(Channel).filter_by(name=channel_name).first()
    author = db.query(Author).filter_by(name=author_name).first()
    if channel and author:
        return author in channel.authors
    return False


if __name__ == '__main__':
    add_channel(next(get_db()), 'xxx')

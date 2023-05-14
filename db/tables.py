import os
from sqlalchemy import create_engine, BigInteger
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.orm import Session, scoped_session, sessionmaker

sqlite_file_path = os.environ.get('SQLITE_FILE_PATH', '/home/david/Documents/hb.sqlite')

engine = create_engine(f'sqlite:///{sqlite_file_path}', echo=True)


def get_session() -> Session:
    """Get SQLAlchemy session"""
    return scoped_session(sessionmaker(bind=engine))()


class BaseTable(DeclarativeBase):
    pass


class TgUser(BaseTable):
    __tablename__ = 'tg_user'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    active: Mapped[bool] = mapped_column(default=True)


class Stats(BaseTable):
    __tablename__ = 'stats'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    searches: Mapped[int] = mapped_column(BigInteger, default=0)
    books_read: Mapped[int] = mapped_column(BigInteger, default=0)
    pages_read: Mapped[int] = mapped_column(BigInteger, default=0)


BaseTable.metadata.create_all(engine)
session = get_session()
session.bind = engine
if not session.query(Stats).count():
    session.add(Stats())
    session.commit()

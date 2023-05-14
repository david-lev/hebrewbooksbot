from data import config
from sqlalchemy import create_engine, BigInteger, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.orm import Session, scoped_session, sessionmaker

engine = create_engine(f'sqlite:///{config.get_settings().sqlite_file_path}')  # , echo=True)


def get_session() -> Session:
    """Get SQLAlchemy session"""
    return scoped_session(sessionmaker(bind=engine))()


class BaseTable(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TgUser(BaseTable):
    __tablename__ = 'tg_user'
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    lang: Mapped[str] = mapped_column(String(5))
    active: Mapped[bool] = mapped_column(default=True)
    candle_pressed: Mapped[bool] = mapped_column(default=False)
    

class Stats(BaseTable):
    __tablename__ = 'stats'
    searches: Mapped[int] = mapped_column(BigInteger, default=0)
    books_read: Mapped[int] = mapped_column(BigInteger, default=0)
    pages_read: Mapped[int] = mapped_column(BigInteger, default=0)


BaseTable.metadata.create_all(engine)
session = get_session()
session.bind = engine
if not session.query(Stats).count():
    session.add(Stats())
    session.commit()

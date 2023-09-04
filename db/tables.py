from contextlib import contextmanager
from data import config
from sqlalchemy import create_engine, BigInteger, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker

conf = config.get_settings()
engine = create_engine(
    url=f'sqlite:///{conf.sqlite_file_path}',
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    echo=conf.log_level == 'DEBUG',
)
Session = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Session:
    """Get session"""
    new_session = Session()
    try:
        yield new_session
    finally:
        new_session.close()


class BaseTable(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TgUser(BaseTable):
    __tablename__ = 'tg_user'
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)


class WaUser(BaseTable):
    __tablename__ = 'wa_user'
    wa_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Stats(BaseTable):
    __tablename__ = 'stats'
    inline_searches: Mapped[int] = mapped_column(BigInteger, default=0)
    msg_searches: Mapped[int] = mapped_column(BigInteger, default=0)
    books_read: Mapped[int] = mapped_column(BigInteger, default=0)
    pages_read: Mapped[int] = mapped_column(BigInteger, default=0)
    jumps: Mapped[int] = mapped_column(BigInteger, default=0)

    @property
    def searches(self) -> int:
        return self.inline_searches + self.msg_searches


# class TgFile(BaseTable):
#     __tablename__ = 'tg_file'
#     file_id: Mapped[str] = mapped_column(String(50), unique=True)
#     file_uid: Mapped[str] = mapped_column(String(50), unique=True)
#     hb_ep: Mapped[str] = mapped_column(String(100), unique=True)


# class WaFile(BaseTable):
#     __tablename__ = 'wa_file'
#     file_id: Mapped[str] = mapped_column(String(100), unique=True)
#     upload_date: Mapped[date] = mapped_column(default=date.today)
#     hb_ep: Mapped[str] = mapped_column(String(100), unique=True)


BaseTable.metadata.create_all(engine)
with get_session() as session:
    if not session.query(Stats).count():
        session.add(Stats())

from data import config
from sqlalchemy import create_engine, BigInteger, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, scoped_session, Session, sessionmaker

engine = create_engine(f'sqlite:///{config.get_settings().sqlite_file_path}')  # , echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def get_session() -> Session:
    """Get SQLAlchemy session"""
    return Session()


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
session = get_session()
session.bind = engine
if not session.query(Stats).count():
    session.add(Stats())
    session.commit()

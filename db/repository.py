from enum import Enum
from sqlalchemy.exc import IntegrityError
from db.tables import TgUser, Stats, get_session


def add_tg_user(tg_id: int, lang: str):
    """Add new tg user to db"""
    session = get_session()
    try:
        session.add(TgUser(tg_id=tg_id, lang=lang))
        session.commit()
    except IntegrityError:
        session.rollback()


def get_tg_user(tg_id: int) -> type[TgUser]:
    """Get tg user"""
    session = get_session()
    return session.query(TgUser).filter(TgUser.tg_id == tg_id).first()


def get_tg_users_count() -> int:
    """Get tg users count"""
    session = get_session()
    return session.query(TgUser).count()


def get_tg_user_lang(tg_id: int) -> str | None:
    """Get tg user lang"""
    session = get_session()
    tg_user = session.query(TgUser).filter(TgUser.tg_id == tg_id).first()
    return tg_user.lang if tg_user else None


def set_tg_user_lang(tg_id: int, lang: str):
    """Set tg user lang"""
    session = get_session()
    tg_user = session.query(TgUser).filter(TgUser.tg_id == tg_id).first()
    tg_user.lang = lang
    session.commit()


def get_active_tg_users() -> list[type[TgUser]]:
    """Get active tg users"""
    session = get_session()
    return session.query(TgUser).filter(TgUser.active == True).all()


def set_tg_user_active(tg_id: int, active: bool):
    """Set tg user active"""
    session = get_session()
    tg_user = session.query(TgUser).filter(TgUser.tg_id == tg_id).first()
    tg_user.active = active
    session.commit()


def get_stats() -> type[Stats]:
    """Get stats"""
    session = get_session()
    stats = session.query(Stats).first()
    return stats


class StatsType(Enum):
    INLINE_SEARCHES = 'inline_searches'
    MSG_SEARCHES = 'msg_searches'
    BOOKS_READ = 'books_read'
    PAGES_READ = 'pages_read'
    JUMPS = 'jumps'


def increase_stats(stats_type: StatsType):
    """Increase stats"""
    session = get_session()
    stats = session.query(Stats).first()
    if stats_type == StatsType.INLINE_SEARCHES:
        stats.inline_searches += 1
    elif stats_type == StatsType.MSG_SEARCHES:
        stats.msg_searches += 1
    elif stats_type == StatsType.BOOKS_READ:
        stats.books_read += 1
    elif stats_type == StatsType.PAGES_READ:
        stats.pages_read += 1
    elif stats_type == StatsType.JUMPS:
        stats.jumps += 1
    session.commit()

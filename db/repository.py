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


def press_candle(tg_id: int):
    """Press candle"""
    session = get_session()
    tg_user = session.query(TgUser).filter(TgUser.tg_id == tg_id).first()
    if not tg_user:
        raise ValueError(f'Tg user {tg_id} not found')
    tg_user.candle_pressed = True
    session.commit()


def get_candle_pressed_count() -> int:
    """Get candle pressed count"""
    session = get_session()
    return session.query(TgUser).filter(TgUser.candle_pressed == True).count()


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


def get_stats() -> type[Stats]:
    """Get stats"""
    session = get_session()
    stats = session.query(Stats).first()
    return stats


def increase_search_count():
    """Increase search count"""
    session = get_session()
    stats = session.query(Stats).first()
    stats.searches += 1
    session.commit()


def increase_books_read_count():
    """Increase books read count"""
    session = get_session()
    stats = session.query(Stats).first()
    stats.books_read += 1
    session.commit()


def increase_pages_read_count():
    """Increase pages read count"""
    session = get_session()
    stats = session.query(Stats).first()
    stats.pages_read += 1
    session.commit()

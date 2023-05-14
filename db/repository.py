from sqlalchemy.exc import IntegrityError
from db.tables import TgUser, Stats, get_session


def add_tg_user(tg_id: int):
    """Add new tg user to db"""
    session = get_session()
    try:
        tg_user = TgUser(tg_id=tg_id)
        session.add(tg_user)
        session.commit()
    except IntegrityError:
        session.rollback()


def get_tg_users_count():
    """Get tg users count"""
    session = get_session()
    return session.query(TgUser).count()


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


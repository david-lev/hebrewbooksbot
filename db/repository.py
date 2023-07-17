from enum import Enum
from sqlalchemy.exc import IntegrityError
from db.tables import TgUser, Stats, get_session, WaUser


def add_tg_user(tg_id: int, lang: str) -> bool:
    """Add new tg user to db, return True if new user added"""
    with get_session() as session:
        try:
            session.add(TgUser(tg_id=tg_id, lang=lang))
            return True
        except IntegrityError:
            return False

def get_tg_user(tg_id: int) -> type[TgUser]:
    """Get tg user"""
    with get_session() as session:
        return session.query(TgUser).filter(TgUser.tg_id == tg_id).first()


def get_tg_users_count(active: bool | None = None, lang_code: str = None) -> int:
    """Get tg users count"""
    with get_session() as session:
        tg_users = session.query(TgUser)
        if active is not None:
            tg_users = tg_users.filter(TgUser.active == active)
        if lang_code:
            tg_users = tg_users.filter(TgUser.lang == lang_code)
        return tg_users.count()


def get_tg_user_lang(tg_id: int) -> str | None:
    """Get tg user lang"""
    with get_session() as session:
        tg_user = session.query(TgUser).filter(TgUser.tg_id == tg_id).first()
        return tg_user.lang if tg_user else tg_user


def set_tg_user_lang(tg_id: int, lang: str):
    """Set tg user lang"""
    with get_session() as session:
        session.query(TgUser).filter(TgUser.tg_id == tg_id).update({TgUser.lang: lang})


def get_tg_users(active: bool, lang_code: str | None = None) -> list[type[TgUser]]:
    """Get active tg users"""
    with get_session() as session:
        tg_users = session.query(TgUser).filter(TgUser.active == active)
        if lang_code:
            tg_users = tg_users.filter(TgUser.lang == lang_code)
        return tg_users.all()


def set_tg_user_active(tg_id: int, active: bool):
    """Set tg user active"""
    with get_session() as session:
        session.query(TgUser).filter(TgUser.tg_id == tg_id).update({TgUser.active: active})


def add_wa_user(wa_id: str, lang: str) -> bool:
    """Add new wa user to db, return True if new user added"""
    with get_session() as session:
        try:
            session.add(WaUser(wa_id=wa_id, lang=lang))
            return True
        except IntegrityError:
            return False


def get_wa_user(wa_id: str) -> type[WaUser]:
    """Get wa user"""
    with get_session() as session:
        return session.query(WaUser).filter(WaUser.wa_id == wa_id).first()


def get_wa_users_count(active: bool | None = None, lang_code: str = None) -> int:
    """Get wa users count"""
    with get_session() as session:
        wa_users = session.query(WaUser)
        if active is not None:
            wa_users = wa_users.filter(WaUser.active == active)
        if lang_code:
            wa_users = wa_users.filter(WaUser.lang == lang_code)
        return wa_users.count()


def get_stats() -> type[Stats]:
    """Get stats"""
    with get_session() as session:
        return session.query(Stats).first()


class StatsType(Enum):
    INLINE_SEARCHES = 'inline_searches'
    MSG_SEARCHES = 'msg_searches'
    BOOKS_READ = 'books_read'
    PAGES_READ = 'pages_read'
    JUMPS = 'jumps'


def increase_stats(stats_type: StatsType):
    """Increase stats"""
    with get_session() as session:
        stats = session.query(Stats).first()
        setattr(stats, stats_type.value, getattr(stats, stats_type.value) + 1)

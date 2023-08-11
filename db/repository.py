from enum import Enum
from sqlalchemy.exc import IntegrityError
from db.tables import TgUser, Stats, get_session, WaUser


def add_tg_user(tg_id: int, lang: str) -> bool:
    """Add new tg user to db, return True if new user added"""
    session = get_session()
    try:
        session.add(TgUser(tg_id=tg_id, lang=lang))
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def get_tg_user(tg_id: int) -> type[TgUser]:
    """Get tg user"""
    session = get_session()
    return session.query(TgUser).filter(TgUser.tg_id == tg_id).first()


def get_tg_users_count(active: bool | None = None, lang_code: str = None) -> int:
    """Get tg users count"""
    session = get_session()
    tg_users = session.query(TgUser)
    if active is not None:
        tg_users = tg_users.filter(TgUser.active == active)
    if lang_code:
        tg_users = tg_users.filter(TgUser.lang == lang_code)
    return tg_users.count()


def get_tg_user_lang(tg_id: int) -> str | None:
    """Get tg user lang"""
    session = get_session()
    tg_user = session.query(TgUser).filter(TgUser.tg_id == tg_id).first()
    return tg_user.lang if tg_user else tg_user


def set_tg_user_lang(tg_id: int, lang: str):
    """Set tg user lang"""
    session = get_session()
    session.query(TgUser).filter(TgUser.tg_id == tg_id).update({TgUser.lang: lang})
    session.commit()


def get_tg_users(active: bool, lang_code: str | None = None) -> list[type[TgUser]]:
    """Get active tg users"""
    session = get_session()
    tg_users = session.query(TgUser).filter(TgUser.active == active)
    if lang_code:
        tg_users = tg_users.filter(TgUser.lang == lang_code)
    return tg_users.all()


def set_tg_user_active(tg_id: int, active: bool):
    """Set tg user active"""
    session = get_session()
    session.query(TgUser).filter(TgUser.tg_id == tg_id).update({TgUser.active: active})
    session.commit()


def add_wa_user(wa_id: str, lang: str, active: bool = True) -> bool:
    """Add new wa user to db, return True if new user added"""
    session = get_session()
    try:
        session.add(WaUser(wa_id=wa_id, lang=lang, active=active))
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def get_wa_user(wa_id: str) -> type[WaUser]:
    """Get wa user"""
    session = get_session()
    return session.query(WaUser).filter(WaUser.wa_id == wa_id).first()


def get_wa_users_count(active: bool | None = None, lang_code: str = None) -> int:
    """Get wa users count"""
    session = get_session()
    wa_users = session.query(WaUser)
    if active is not None:
        wa_users = wa_users.filter(WaUser.active == active)
    if lang_code:
        wa_users = wa_users.filter(WaUser.lang == lang_code)
    return wa_users.count()


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
    setattr(stats, stats_type.value, getattr(stats, stats_type.value) + 1)
    session.commit()


def _get_url_path_plus_query(url: str) -> str:
    return f"{parse.urlparse(url).path}{'?' + parse.urlparse(url).query if parse.urlparse(url).query else ''}"


@lru_cache(maxsize=None)
def get_tg_file(url: str) -> type[TgFile]:
    """Get tg file. raise sqlalchemy.orm.exc.NoResultFound if not found"""
    return get_session().query(TgFile).filter(TgFile.hb_ep == _get_url_path_plus_query(url)).one()


def create_tg_file(url: str, file_id: str, file_uid: str) -> None:
    """Create tg file"""
    session = get_session()
    session.add(TgFile(hb_ep=_get_url_path_plus_query(url), file_id=file_id, file_uid=file_uid))
    session.commit()


@cache.cachable(cache_name='wa_file', params='url')
def get_wa_file(*, url: str) -> type[WaFile]:
    """Get wa file. raise sqlalchemy.orm.exc.NoResultFound if not found or if upload_date > 30 days"""
    return get_session().query(WaFile).filter(WaFile.hb_ep == _get_url_path_plus_query(url)).one()


@cache.invalidate(cache_name='wa_file', params='url')
def create_wa_file(*, url: str, file_id: str) -> None:
    """Create wa file"""
    session = get_session()
    session.add(WaFile(hb_ep=_get_url_path_plus_query(url), file_id=file_id))
    session.commit()


@cache.invalidate(cache_name='wa_file', params='url')
def delete_wa_file(*, url: str) -> None:
    """Delete wa file"""
    session = get_session()
    session.query(WaFile).filter(WaFile.hb_ep == _get_url_path_plus_query(url)).delete()
    session.commit()

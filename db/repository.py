from enum import Enum
from sqlalchemy.exc import IntegrityError
from data.cache import cache
from db.tables import global_session, TgUser, Stats, WaUser
# from db.tables import TgFile, WaFile
# from functools import lru_cache
# from urllib import parse


@cache.invalidate(cache_name='tg_user', params=['tg_id'])
def add_tg_user(*, tg_id: int, lang: str, active: bool = True) -> bool:
    """Add new tg user to db, return True if new user added"""
    try:
        global_session.add(TgUser(tg_id=tg_id, lang=lang, active=active))
        global_session.commit()
        return True
    except IntegrityError:
        global_session.rollback()
        return False


@cache.cachable(cache_name='tg_user', params=['tg_id'])
def get_tg_user(*, tg_id: int) -> type[TgUser] | None:
    """Get tg user"""
    return global_session.query(TgUser).filter(TgUser.tg_id == tg_id).first()


@cache.invalidate(cache_name='tg_user', params=['tg_id'])
def update_tg_user(*, tg_id: int, **kwargs) -> None:
    """Update tg user"""
    global_session.query(TgUser).filter(TgUser.tg_id == tg_id).update(kwargs)
    global_session.commit()


def get_tg_users_count(active: bool | None = None, lang_code: str = None) -> int:
    """Get tg users count"""
    return global_session.query(TgUser).filter(
        (TgUser.active == active) if active is not None else True,
        (TgUser.lang == lang_code) if lang_code else True
    ).count()


@cache.invalidate(cache_name='wa_user', params=['wa_id'])
def add_wa_user(*, wa_id: str, lang: str, active: bool = True) -> bool:
    """Add new wa user to db, return True if new user added"""
    try:
        global_session.add(WaUser(wa_id=wa_id, lang=lang, active=active))
        global_session.commit()
        return True
    except IntegrityError:
        global_session.rollback()
        return False


@cache.cachable(cache_name='wa_user', params=['wa_id'])
def get_wa_user(*, wa_id: str) -> type[WaUser] | None:
    """Get wa user"""
    return global_session.query(WaUser).filter(WaUser.wa_id == wa_id).first()


@cache.invalidate(cache_name='wa_user', params=['wa_id'])
def update_wa_user(*, wa_id: str, **kwargs) -> None:
    """Update wa user"""
    global_session.query(WaUser).filter(WaUser.wa_id == wa_id).update(kwargs)
    global_session.commit()


def get_wa_users_count(active: bool | None = None, lang_code: str = None) -> int:
    """Get wa users count"""
    return global_session.query(WaUser).filter(
        (WaUser.active == active) if active is not None else True,
        (WaUser.lang == lang_code) if lang_code else True
    ).count()


def get_stats() -> type[Stats]:
    """Get stats"""
    return global_session.query(Stats).first()


class StatsType(Enum):
    INLINE_SEARCHES = 'inline_searches'
    MSG_SEARCHES = 'msg_searches'
    BOOKS_READ = 'books_read'
    PAGES_READ = 'pages_read'
    JUMPS = 'jumps'


def increase_stats(stats_type: StatsType):
    """Increase stats"""
    stats = global_session.query(Stats).first()
    setattr(stats, stats_type.value, getattr(stats, stats_type.value) + 1)
    global_session.commit()

#
# def _get_url_path_plus_query(url: str) -> str:
#     return f"{parse.urlparse(url).path}{'?' + parse.urlparse(url).query if parse.urlparse(url).query else ''}"
#
#
# @lru_cache(maxsize=None)
# def get_tg_file(url: str) -> type[TgFile]:
#     """Get tg file. raise sqlalchemy.orm.exc.NoResultFound if not found"""
#     return get_global_global_session.query(TgFile).filter(TgFile.hb_ep == _get_url_path_plus_query(url)).one()
#
#
# def create_tg_file(url: str, file_id: str, file_uid: str) -> None:
#     """Create tg file"""
#     session = get_global_session
#     global_session.add(TgFile(hb_ep=_get_url_path_plus_query(url), file_id=file_id, file_uid=file_uid))
#     global_session.commit()
#
#
# @cache.cachable(cache_name='wa_file', params='url')
# def get_wa_file(*, url: str) -> type[WaFile]:
#     """Get wa file. raise sqlalchemy.orm.exc.NoResultFound if not found or if upload_date > 30 days"""
#     return get_global_global_session.query(WaFile).filter(WaFile.hb_ep == _get_url_path_plus_query(url)).one()
#
#
# @cache.invalidate(cache_name='wa_file', params='url')
# def create_wa_file(*, url: str, file_id: str) -> None:
#     """Create wa file"""
#     session = get_global_session
#     global_session.add(WaFile(hb_ep=_get_url_path_plus_query(url), file_id=file_id))
#     global_session.commit()
#
#
# @cache.invalidate(cache_name='wa_file', params='url')
# def delete_wa_file(*, url: str) -> None:
#     """Delete wa file"""
#     session = get_global_session
#     global_session.query(WaFile).filter(WaFile.hb_ep == _get_url_path_plus_query(url)).delete()
#     global_session.commit()

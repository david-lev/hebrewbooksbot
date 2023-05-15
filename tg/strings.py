from enum import Enum, auto

from pyrogram.types import Message, CallbackQuery, InlineQuery

from db import repository


class String(Enum):
    WELCOME = auto()
    SEARCH = auto()
    SEARCH_IN_CHATS = auto()
    BROWSE = auto()
    LIGHT_A_CANDLE = auto()
    GITHUB = auto()
    HEBREWBOOKS_SITE = auto()
    STATS = auto()
    REGISTERED_USERS = auto()
    BOOKS_READ = auto()
    PAGES_READ = auto()
    SEARCHES = auto()
    CANDLE_LIGHTING = auto()
    FAST_READING = auto()
    SHARE = auto()
    DOWNLOAD = auto()
    NEXT = auto()
    PREVIOUS = auto()
    WAIT_FOR_PREVIEW = auto()
    PAGE_X_OF_Y = auto()
    READ_ON_SITE = auto()
    SLOW_DOWN = auto()
    PAGE_NOT_EXIST = auto()
    JUMP_TIP = auto()
    CHOOSE_BROWSE_TYPE = auto()
    SUBJECTS = auto()
    LETTERS = auto()
    DATES = auto()
    BACK = auto()
    START_SEARCH_INLINE = auto()
    SEARCH_INLINE_TIP = auto()
    BOOK_NOT_FOUND = auto()
    PRESS_TO_SHARE = auto()
    X_RESULTS_FOR_S = auto()
    NO_RESULTS_FOR_S = auto()
    SEARCH_INLINE = auto()
    ORIGINAL_SEARCH_DELETED = auto()


_STRINGS = {
    String.WELCOME: {
        'en': "**📚 Welcome to HebrewBooksBot! 📚**\n\n"
              "This bot allows you to search for books on HebrewBooks.org and read them quickly.\n\n"
              "To get started, press the \"Search\" button below or send a search query.\n\n"
              "__🕯 In memory of my grandfather, Rabbi Aharon Yitzchak ben Shmuel Zanvil z\"l 🕯__\n\n",
        'he': "**📚 ברוכים הבאים להיברו-בוקס בטלגרם! 📚**\n\n"
              "🔎 בוט זה מאפשר חיפוש ועיון ספרים באתר hebrewbooks.org\n"
              "**📜 הוראות שימוש:** לחצו על חיפוש או על עיון או שלחו מילת חיפוש.\n"
              "**💡 טיפ:** ניתן לחפש בפורמט `כותר:מחבר` כדי לקבל תוצאות מדוייקות יותר.\n\n"
              "__🕯 לעילוי נשמת סבי הרב אהרן יצחק בן שמואל זנוויל זצ״ל 🕯__\n\n"
    },
    String.SEARCH: {
        'en': '🔎 Search',
        'he': '🔎 חיפוש'
    },
    String.BROWSE: {
        'en': '📖 Browse',
        'he': '📖 עיון'
    }
}


def get_string(mqc: Message | CallbackQuery | InlineQuery, string: String) -> str:
    """Get a string in the user's language."""
    try:
        lang = repository.get_tg_user_lang(mqc.from_user.id) \
               or mqc.from_user.language_code \
               or 'en'
    except AttributeError:
        lang = 'en'
    return _STRINGS[string].get(lang, _STRINGS[string]['en'])

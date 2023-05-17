from enum import Enum, auto

from pyrogram.types import Message, CallbackQuery, InlineQuery

from db import repository


class String(Enum):
    WELCOME = auto()  # V
    SEARCH = auto()  # V
    SEARCH_IN_CHATS = auto()
    BROWSE = auto()  # V
    LIGHT_A_CANDLE = auto()  # V
    GITHUB = auto()  # V
    HEBREWBOOKS_SITE = auto()  # V
    STATS = auto()  # V
    REGISTERED_USERS = auto()
    BOOKS_READ = auto()  # V
    PAGES_READ = auto()
    SEARCHES = auto()
    CANDLE_LIGHTING = auto()
    FAST_READING = auto()
    SHARE = auto()  # V
    DOWNLOAD = auto()  # V
    NEXT = auto()  # V
    PREVIOUS = auto()  # V
    WAIT_FOR_PREVIEW = auto()  # V
    PAGE_X_OF_Y = auto()  # RTL ⚠️
    READ_ON_SITE = auto()  # V
    SLOW_DOWN = auto()  # V
    PAGE_NOT_EXIST = auto()  # V
    JUMP_TIP = auto()  # V
    CHOOSE_BROWSE_TYPE = auto()  # V
    SUBJECTS = auto()  # V
    LETTERS = auto()  # V
    DATES = auto()  # V
    BACK = auto()
    CHOOSE = auto()  # V
    START_SEARCH_INLINE = auto()  # V
    SEARCH_INLINE_TIP = auto()  # V
    BOOK_NOT_FOUND = auto()  # V
    PRESS_TO_SHARE = auto()  # V
    X_RESULTS_FOR_S = auto()  # RTL ⚠️
    NO_RESULTS_FOR_S = auto()  # V
    SEARCH_INLINE = auto()  # V
    ORIGINAL_SEARCH_DELETED = auto()  # V


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
    },
    String.LIGHT_A_CANDLE: {
        'en': '🕯 Light a candle ({})',
        'he': '🕯 הדליקו נר ({})'
    },
    String.GITHUB: {
        'en': '⭐️ GitHub ⭐️',
        'he': '⭐️ גיטהאב ⭐️'
    },
    String.HEBREWBOOKS_SITE: {
        'en': '🌍 Hiberbox site 🌍',
        'he': '🌍 אתר היברובוקס 🌍'
    },
    String.STATS: {
        'en': (
            "📊 Bot Stats 📊\n\n",
            "👥 Registered users: {users_count}\n",
            "🕯 Candles lit: {candle_pressed_count}\n"
            "📚 Books read: {books_read}\n",
            "📖 Pages read: {pages_read}\n",
            "🔎 Searches performed: {searches}\n",
        ),
        'he': (
            "📊 סטטיסטיקות הבוט 📊\n\n",
            "👥 משתמשים רשומים: {users_count}\n",
            "🕯 נרות הודלקו: {candle_pressed_count}\n"
            "📚 ספרים נקראו: {books_read}\n",
            "📖 עמודים נקראו: {pages_read}\n",
            "🔎 חיפושים בוצעו: {searches}\n",
        )
    },
    String.BOOKS_READ: {
        'en': '📖 Quick reading 📖',
        'he': '📖 קריאה מהירה 📖'
    },
    String.SHARE: {
        'en': '♻️ Sharing ♻️',
        'he': '♻️ שיתוף ♻️'
    },
    String.DOWNLOAD: {
        'en': '⬇️ Download ⬇️',
        'he': '⬇️ הורדה ⬇️'
    },
    String.NEXT: {
        'en': 'Next ⏪',
        'he': 'הבא ⏪'
    },
    String.PREVIOUS: {
        'en': '⏩ the previous one',
        'he': '⏩ הקודם'
    },
    String.WAIT_FOR_PREVIEW: {
        'en': 'Wait a few seconds for the preview to load',
        'he': 'יש להמתין מספר שניות לטעינת התצוגה המקדימה'
    },
    String.READ_ON_SITE: {
        'en': '🌍 Reading on the site 🌍',
        'he': '🌍 קריאה באתר 🌍'
    },
    String.SLOW_DOWN: {
        'en': "I'm not an angel.. slower",
        'he': "אני לא מלאך.. לאט יותר"
    },
    String.JUMP_TIP: {
        'en': 'Tip: instead of browsing, comment on this message with the page number you want to read.\
              \nYou can also edit the number you sent and the page will change accordingly.',
        'he': 'טיפ: במקום לדפדף, הגיבו על ההודעה הזו עם מספר העמוד שברצונכם לקרוא.\
             \nניתן גם לערוך את המספר ששלחתם והעמוד ישתנה בהתאם.'
    },
    String.PAGE_NOT_EXIST: {
        'en': 'The page does not exist! (Number of pages: {})',
        'he': 'העמוד לא קיים! (כמות עמודים: {})'
    },
    String.SEARCH_INLINE_TIP: {
        'en': "Tip: You can search in the 'Title: Author' format in order to get accurate results",
        'he': "טיפ: ניתן לחפש בפורמט 'כותרת:מחבר' על מנת לקבל תוצאות מדוייקות"
    },
    String.START_SEARCH_INLINE: {
        'en': 'start looking',
        'he': 'התחילו לחפש'
    },
    String.BOOK_NOT_FOUND: {
        'en': 'Book not found',
        'he': 'ספר לא נמצא'
    },
    String.PRESS_TO_SHARE: {
        'en': 'Click on the result to share {}',
        'he': 'לחצו על התוצאה כדי לשתף את {}'
    },
    String.NO_RESULTS_FOR_S: {
        'en': 'no results were found for: {}',
        'he': 'לא נמצאו תוצאות עבור: {}'
    },
    String.SEARCH_INLINE: {
        'en': '🔎 Inline search',
        'he': '🔎 חיפוש באינליין'
    },
    String.ORIGINAL_SEARCH_DELETED: {
        'en': 'The original search has been deleted',
        'he': 'החיפוש המקורי נמחק'
    },
    String.CHOOSE_BROWSE_TYPE: {
        'en': 'Select a browsing type',
        'he': 'בחר סוג דפדוף'
    },
    String.SUBJECTS: {
        'en': '🗂 Themes',
        'he': '🗂 נושאים'
    },
    String.LETTERS: {
        'en': '🔠 letters',
        'he': '🔠 אותיות'
    },
    String.DATES: {
        'en': '📅 Dates',
        'he': '📅 תאריכים'
    },
    String.CHOOSE: {
        'en': 'choose',
        'he': 'בחר'
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
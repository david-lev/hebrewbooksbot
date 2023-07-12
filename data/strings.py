from enum import Enum, auto

RTL = '\u200f'
LTR = '\u200e'


class String(Enum):
    WELCOME = auto()  # V
    SEARCH = auto()  # V
    SEARCH_IN_CHATS = auto()  # V
    BROWSE = auto()  # V
    INSTANT_READ = auto()  # V
    BACK = auto()  # V
    GITHUB = auto()  # V
    HEBREWBOOKS_SITE = auto()  # V
    STATS = auto()  # V
    SHOW_STATS = auto()  # V
    SHOW_STATS_ADMIN = auto()  # V
    SHARE = auto()  # V
    DOWNLOAD = auto()  # V
    NEXT = auto()  # V
    PREVIOUS = auto()  # V
    WAIT_FOR_PREVIEW = auto()  # V
    PAGE_X_OF_Y = auto()  # RTL ⚠️
    READ_ON_SITE = auto()  # V
    SLOW_DOWN = auto()  # V
    PAGE_NOT_EXIST = auto()  # V
    JUMP_NUMBERS_ONLY = auto()  # V
    JUMP_TIP = auto()  # V
    CHOOSE_BROWSE_TYPE = auto()  # V
    SHAS = auto()  # V
    TUR_AND_SA = auto()  # V
    SUBJECTS = auto()  # V
    LETTERS = auto()  # V
    DATE_RANGES = auto()  # V
    CHOOSE = auto()  # V
    CHOOSE_LETTER = auto()  # V
    CHOOSE_SUBJECT = auto()  # V
    CHOOSE_DATE_RANGE = auto()  # V
    CHOOSE_MASECHET = auto()  # V
    START_SEARCH_INLINE = auto()  # V
    SEARCH_INLINE_TIP = auto()  # V
    BOOK_NOT_FOUND = auto()  # V
    PRESS_TO_SHARE = auto()  # V
    SEARCH_RESULTS = auto()  # V
    X_RESULTS_FOR_S = auto()  # RTL ⚠️
    X_TO_Y_OF_TOTAL_FOR_S = auto()  # RTL ⚠️
    X_TO_Y_OF_TOTAL = auto()  # RTL ⚠️
    NO_RESULTS_FOR_Q = auto()  # V
    SEARCH_INLINE = auto()  # V
    ORIGINAL_SEARCH_DELETED = auto()  # V
    IMAGE = auto()
    DOCUMENT = auto()
    TEXT = auto()
    NOT_REGISTERED = auto()  # V
    CHOOSE_LANGUAGE = auto()  # V
    CHANGE_LANGUAGE = auto()  # V
    LANGUAGE_CHANGED = auto()  # V
    SEARCHING_FOR_Q = auto()  # V
    NAVIGATE_BETWEEN_RESULTS = auto()  # V


STRINGS = {
    String.WELCOME: {
        'en': "\n".join([
            "**📚 Welcome to the HebrewBook bot on Telegram! 📚**\n",
            "This bot allows searching and browsing books on hebrewbooks.org\n",
            "**⚡️ Features:**",
            "\t🔎 Searching for books in inline mode or by sending a message",
            "\t📓 Browsing through the Shas masechtot",
            "\t📚 Browse the library by category, date or letter",
            "\t📖 Reading mode as an image or as a PDF (text coming soon)",
            "\t⏩ Jump to page",
            "\t♻️ Sharing books with friends\n",
            "**💡 Tips:**",
            "\t• To search for a book by title or author, use the format `title:author`",
            "\t• In Read Mode, you can jump to a page by replying to the message with the page number\n",
            "**🔜 Coming soon:**",
            "\t• A bot for WhatsApp",
            "\t• Search the contents of the books",
            "\t• Saving favorite books and bookmarks",
            "\t• Change language manually\n",
            "📮 For feedback and comments - @davidlev\n",
            "__🕯 In memory of my grandfather, Rabbi Aharon Yitzchak ben Shmuel Zanvil z\"l 🕯__"
        ]),
        'he': "\n".join([
            "**📚 ברוכים הבאים לבוט היברובוקס בטלגרם! 📚**\n",
            "בוט זה מאפשר לחפש ולעיין בספרים באתר hebrewbooks.org\n",
            "**⚡️ פיצ'רים:**",
            "\t🔎 חיפוש ספרים במצב אינליין או על ידי שליחת הודעה",
            "\t📓 עיון במסכתות הש\"ס",
            "\t📚 עיון בספריה לפי קטגוריה, תאריך או אות",
            "\t📖 מצב קריאה כתמונה או כקובץ PDF (טקסט בקרוב)",
            "\t⏪ קפיצה לעמוד",
            "\t♻️ שיתוף ספרים עם חברים\n",
            "**💡 טיפים:**",
            "\t• כדי לחפש ספר לפי כותרת או מחבר, השתמשו בפורמט `כותרת:מחבר`",
            "\t• במצב קריאה, ניתן לקפוץ לדף מסוים על ידי תגובה להודעה עם מספר העמוד\n",
            "**🔜 בקרוב:**",
            "\t• בוט לוואטסאפ",
            "\t• חיפוש בתוכן הספרים",
            "\t• שמירת ספרים מועדפים וסימניות",
            "\t• שינוי שפה באופן ידני\n",
            "📮 למשוב והערות - @davidlev\n",
            "__🕯 לעילוי נשמת סבי, הרב אהרן יצחק בן שמואל זנוויל ז\"ל 🕯__"
        ])
    },
    String.SEARCH: {
        'en': '🔎 Search',
        'he': '🔎 חיפוש'
    },
    String.SEARCH_IN_CHATS: {
        'en': '🔎 Search in chats',
        'he': '🔎 חיפוש בצאטים'
    },
    String.BROWSE: {
        'en': '📖 Browse',
        'he': '📖 עיון'
    },
    String.BACK: {
        'en': '🔙 Back',
        'he': '🔙 חזרה'
    },
    String.GITHUB: {
        'en': '⭐️ GitHub ⭐️',
        'he': '⭐️ גיטהאב ⭐️'
    },
    String.HEBREWBOOKS_SITE: {
        'en': '🌍 HebrewBooks Website 🌍',
        'he': '🌍 אתר היברובוקס 🌍'
    },
    String.STATS: {
        'en': '📊 Stats',
        'he': '📊 סטטיסטיקות'
    },
    String.SHOW_STATS: {
        'en': (
            "📊 Bot Stats 📊\n\n",
            "📚 Books read: {books_read:,}\n",
            "📖 Pages read: {pages_read:,}\n",
            "🔎 Searches: {searches:,}\n"
        ),
        'he': (
            "📊 סטטיסטיקות הבוט 📊\n\n",
            "📚 ספרים נקראו: {books_read:,}\n",
            "📖 דפים נקראו: {pages_read:,}\n",
            "🔎 חיפושים: {searches:,}\n"
        )
    },
    String.SHOW_STATS_ADMIN: {
        'en': (
            "📊 Bot Stats 📊\n\n",
            "👥 Registered users: {users_count:,}\n",
            "📚 Books read: {books_read:,}\n",
            "📖 Pages read: {pages_read:,}\n",
            "🔎 Inline Searches: {inline_searches:,}\n"
            "💬 Message Searches: {msg_searches:,}\n"
            "⏭ Jumps to page: {jumps:,}\n"
        ),
        'he': (
            "📊 סטטיסטיקות הבוט 📊\n\n",
            "👥 משתמשים רשומים: {users_count:,}\n",
            "📚 ספרים נקראו: {books_read:,}\n",
            "📖 דפים נקראו: {pages_read:,}\n",
            "🔎 חיפושים באינליין: {inline_searches:,}\n"
            "💬 חיפושים בהודעות: {msg_searches:,}\n"
            "⏭ קפיצות לדף: {jumps:,}\n"
        )
    },
    String.INSTANT_READ: {
        'en': '📖 Instant Read 📖',
        'he': '📖 קריאה מהירה 📖'
    },
    String.SHARE: {
        'en': '♻️ Share ♻️',
        'he': '♻️ שיתוף ♻️'
    },
    String.DOWNLOAD: {
        'en': '⬇️ Download ⬇️',
        'he': '⬇️ הורדה ⬇️'
    },
    String.NEXT: {
        'en': 'Next ⏩',
        'he': 'הבא ⏪'
    },
    String.PREVIOUS: {
        'en': '⏪ Previous',
        'he': '⏩ הקודם'
    },
    String.WAIT_FOR_PREVIEW: {
        'en': 'Wait a few seconds for the preview to load',
        'he': 'יש להמתין מספר שניות לטעינת התצוגה המקדימה'
    },
    String.READ_ON_SITE: {
        'en': '🌍 Read on site 🌍',
        'he': '🌍 קריאה באתר 🌍'
    },
    String.SLOW_DOWN: {
        'en': "Slow down...",
        'he': "אני לא מלאך.. לאט יותר"
    },
    String.JUMP_NUMBERS_ONLY: {
        'en': 'Please enter numbers only',
        'he': 'יש לשלוח מספרים בלבד'
    },
    String.JUMP_TIP: {
        'en': 'Tip: instead of browsing, reply to this message with the page number you want to read.\
              \nYou can also edit the number you sent and the page will update accordingly.',
        'he': 'טיפ: במקום לדפדף, הגיבו על ההודעה הזו עם מספר העמוד שברצונכם לקרוא.\
             \nניתן גם לערוך את המספר ששלחתם והעמוד ישתנה בהתאם.'
    },
    String.PAGE_NOT_EXIST: {
        'en': 'The page does not exist! (Choose a page between {start} and {total})',
        'he': 'הדף אינו קיים! (בחרו עמוד בין {start} ל-{total})'
    },
    String.SEARCH_INLINE_TIP: {
        'en': "Tip: You can search in the 'Title:Author' format in order to get more accurate results",
        'he': "טיפ: ניתן לחפש בפורמט 'כותרת:מחבר' על מנת לקבל תוצאות מדוייקות"
    },
    String.START_SEARCH_INLINE: {
        'en': 'Start searching',
        'he': 'התחילו לחפש'
    },
    String.BOOK_NOT_FOUND: {
        'en': 'Book not found',
        'he': 'ספר לא נמצא'
    },
    String.PRESS_TO_SHARE: {
        'en': 'Click on the result to share {title}',
        'he': 'לחצו על התוצאה כדי לשתף את {title}'
    },
    String.NO_RESULTS_FOR_Q: {
        'en': 'No results found for: {q}',
        'he': 'לא נמצאו תוצאות עבור: {q}'
    },
    String.SEARCH_INLINE: {
        'en': '🔎 Inline Search',
        'he': '🔎 חיפוש באינליין'
    },
    String.ORIGINAL_SEARCH_DELETED: {
        'en': 'The original search was deleted',
        'he': 'החיפוש המקורי נמחק'
    },
    String.CHOOSE_BROWSE_TYPE: {
        'en': 'Choose a browse type',
        'he': 'בחר סוג עיון'
    },
    String.SHAS: {
        'en': '📚 Shas',
        'he': '📚 ש"ס'
    },
    String.TUR_AND_SA: {
        'en': '📓 Tur & Shulchan Aruch',
        'he': '📓 טור ושולחן ערוך'
    },
    String.SUBJECTS: {
        'en': '🗂 Subjects',
        'he': '🗂 נושאים'
    },
    String.LETTERS: {
        'en': '🔠 Letters',
        'he': '🔠 אותיות'
    },
    String.DATE_RANGES: {
        'en': '📅 Date Ranges',
        'he': '📅 תאריכים'
    },
    String.CHOOSE: {
        'en': 'Choose',
        'he': 'בחרו'
    },
    String.CHOOSE_LETTER: {
        'en': 'Choose a letter',
        'he': 'בחרו אות'
    },
    String.CHOOSE_SUBJECT: {
        'en': 'Choose a subject',
        'he': 'בחרו נושא'
    },
    String.CHOOSE_DATE_RANGE: {
        'en': 'Choose a date range',
        'he': 'בחרו טווח תאריכים'
    },
    String.CHOOSE_MASECHET: {
        'en': 'Choose a masechet',
        'he': 'בחרו מסכת'
    },
    String.PAGE_X_OF_Y: {
        'en': 'Page {page} of {pages}',
        'he': 'עמוד {page} מתוך {pages}'
    },
    String.SEARCH_RESULTS: {
        'en': '📚 Results 📚',
        'he': '📚 תוצאות חיפוש 📚'
    },
    String.X_RESULTS_FOR_S: {
        'en': '{x:,} results for: {s}',
        'he': '%s{x:,} תוצאות עבור: {s}' % RTL
    },
    String.X_TO_Y_OF_TOTAL_FOR_S: {
        'en': '{x:,} - {y:,} from {total:,} results for: {s}',
        'he': '%s{x:,} - {y:,} מתוך {total:,} תוצאות עבור: {s}' % RTL
    },
    String.X_TO_Y_OF_TOTAL: {
        'en': '{x:,} - {y:,} from {total:,} results',
        'he': '%s{x:,} - {y:,} מתוך {total:,} תוצאות' % RTL
    },
    String.IMAGE: {
        'en': '🖼 Image',
        'he': '🖼 תמונה'
    },
    String.TEXT: {
        'en': '📜 Text',
        'he': '📜 טקסט'
    },
    String.DOCUMENT: {
        'en': '📄 Document',
        'he': '📄 מסמך'
    },
    String.NOT_REGISTERED: {
        'en': 'You are not registered in the bot. Please send /start to the bot in order to register.',
        'he': 'אינכם רשומים בבוט. נא לשלוח /start לבוט על מנת להירשם.'
    },
    String.SEARCHING_FOR_Q: {
        'en': '🔎 Searching for: {q}',
        'he': '🔍 מתבצע חיפוש עבור: "{q}"'
    },
    String.NAVIGATE_BETWEEN_RESULTS: {
        'en': 'Navigate between results',
        'he': 'נווטו בין התוצאות'
    },
}

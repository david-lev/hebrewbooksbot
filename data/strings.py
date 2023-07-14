from enum import Enum, auto

RTL = '\u200f'
LTR = '\u200e'


class String(Enum):
    TG_WELCOME = auto()  # V
    WA_WELCOME_HEADER = auto()  # V
    WA_WELCOME_BODY = auto()  # V
    IN_MEMORY_FOOTER = auto()  # V
    SEARCH = auto()  # V
    SEARCH_INSTRUCTIONS = auto()  # V
    SEARCH_IN_CHATS = auto()  # V
    BROWSE = auto()  # V
    INSTANT_READ = auto()  # V
    BACK = auto()  # V
    GITHUB = auto()  # V
    ABOUT = auto()  # V
    WA_ABOUT_MSG = auto()  # V
    PYWA_CREDIT = auto()  # V
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
    PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y = auto()  # V
    NUMBERS_ONLY = auto()  # V
    JUMP_TIP = auto()  # V
    CHOOSE_BROWSE_TYPE = auto()  # V
    SHAS = auto()  # V
    SHAS_CMD = auto()  # V
    TUR_AND_SA = auto()  # V
    TUR_AND_SA_CMD = auto()  # V
    SUBJECTS = auto()  # V
    SUBJECTS_CMD = auto()  # V
    LETTERS = auto()  # V
    LETTERS_CMD = auto()  # V
    DATE_RANGES = auto()  # V
    DATE_RANGES_CMD = auto()  # V
    CHOOSE = auto()  # V
    CHOOSE_LETTER = auto()  # V
    CHOOSE_SUBJECT = auto()  # V
    CHOOSE_DATE_RANGE = auto()  # V
    CHOOSE_MASECHET = auto()  # V
    START_SEARCH_INLINE = auto()  # V
    SEARCH_TIP = auto()  # V
    BOOK_NOT_FOUND = auto()  # V
    MASECHET_NOT_FOUND = auto()  # V
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
    String.TG_WELCOME: {
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
            "\t• חיפוש בתוכן הספרים",
            "\t• שמירת ספרים מועדפים וסימניות",
            "\t• שינוי שפה באופן ידני\n",
            "📮 למשוב והערות - @davidlev\n",
            "__🕯 לעילוי נשמת סבי, הרב אהרן יצחק בן שמואל זנוויל ז\"ל 🕯__"
        ])
    },
    String.WA_WELCOME_HEADER: {
        'en': "📚 Welcome to the HebrewBook bot on WhatsApp! 📚\n",
        'he': "📚 ברוכים הבאים לבוט היברובוקס בוואטסאפ! 📚\n"
    },
    String.WA_WELCOME_BODY: {
        'en': "\n".join([
            "This bot allows searching and browsing books on hebrewbooks.org\n",
            "*⚡️ Features:*",
            "🔎 Searching for books by sending a message",
            "📖 Reading mode as an image or as a PDF (text coming soon)",
            "⏩ Jump to page",
            "♻️ Sharing books with friends\n",
            "*💡 Tips:*",
            "• To search for a book by title or author, use the format ```title:author```",
            "*🔜 Coming soon:*",
            "• Browse the library by category, date or letter",
            "• Browsing through the Shas masechtot",
            "• Search the contents of the books",
            "• Saving favorite books and bookmarks",
            "• Change language manually\n",
            "📮 For feedback and comments - t.me/davidlev\n"
        ]),
        'he': "\n".join([
            "בוט זה מאפשר לחפש ולעיין בספרים באתר hebrewbooks.org\n",
            "*⚡️ פיצ'רים:*",
            "🔎 חיפוש ספרים על ידי שליחת הודעה",
            "📖 מצב קריאה כתמונה או כקובץ PDF (טקסט בקרוב)",
            "⏪ קפיצה לעמוד",
            "♻️ שיתוף ספרים עם חברים\n",
            "*💡 טיפים:*",
            "• כדי לחפש ספר לפי כותרת או מחבר, השתמשו בפורמט ```כותרת:מחבר```",
            "*🔜 בקרוב:*",
            "• עיון בספריה לפי קטגוריה, תאריך או אות",
            "• עיון במסכתות הש\"ס",
            "• חיפוש בתוכן הספרים",
            "• שמירת ספרים מועדפים וסימניות",
            "• שינוי שפה באופן ידני\n",
            "📮 למשוב והערות - t.me/davidlev\n"
        ])
    },
    String.PYWA_CREDIT: {
        'en': "⚡ Powered by PyWa",
        'he': "⚡ נבנה באמצעות PyWa"
    },
    String.IN_MEMORY_FOOTER: {
        'en': "🕯 In memory of Rabbi Aharon Yitzchak ben Shmuel Zanvil z\"l",
        'he': "🕯 לעילוי נשמת הרב אהרן יצחק בן שמואל זנוויל ז\"ל"
    },
    String.WA_ABOUT_MSG: {
        'en': "\n".join((
            "This bot was built with the aim of making the content of the hebrewbooks.org website accessible via WhatsApp.",
            "The use is completely free and In memory my grandfather, Rabbi Aharon Yitzchak ben Shmuel Zanvil zt'l",
            "If you would like to donate to cover the costs (server + access to the WhatsApp API), you can do so using one of the following options",
            "- PayPal paypal.me/davidlev",
            "- GitHub github.com/sponsors/david-lev",
            "- Contact us on Telegram t.me/davidlev",
            "\nAn improved version of the bot is also available on Telegram: t.me/hebooksbot",
            "\nThe bot source code is available on GitHub: github.com/david-lev/hebrewbooksbot"
            "\nThe bot was built using the pywa library github.com/david-lev/pywa"
        )),
        'he': "\n".join((
            "*בוט זה נבנה במטרה להנגיש את תוכן אתר hebrewbooks.org באמצעות וואטסאפ.*",
            "\nהשימוש בבוט חינמי לחלוטין ולעילוי נשמת סבי, הרב אהרן יצחק בן שמואל זנוויל ז\"ל",
            "אם ברצונכם לתרום לצורך כיסוי העלויות (שרת + גישה ל-WhatsApp API), תוכלו לעשות זאת באמצעות אחת מהאפשרויות הבאות",
            "- פייפאל paypal.me/davidlev",
            "- גיטהאב github.com/sponsors/david-lev",
            "- פנו בטלגרם t.me/davidlev",
            "\nגרסה משופרת של הבוט קיימת גם בטלגרם: t.me/hebooksbot",
            "\nקוד הבוט זמין בגיטהאב github.com/david-lev/hebrewbooksbot",
            "\nהבוט נבנה באמצעות ספריית pywa github.com/david-lev/pywa",
        ))
    },
    String.SEARCH_INSTRUCTIONS: {
        'en': '🔎 To search for a book, send a message with your search query',
        'he': '🔎 כדי לחפש ספר, שלחו הודעה עם מילות החיפוש'
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
        'en': "\n".join((
            "📊 Bot Stats 📊\n",
            "📚 Books read: {books_read:,}",
            "📖 Pages read: {pages_read:,}",
            "🔎 Searches: {searches:,}"
        )),
        'he': "\n".join((
            "📊 סטטיסטיקות הבוט 📊\n",
            "📚 ספרים נקראו: {books_read:,}",
            "📖 דפים נקראו: {pages_read:,}",
            "🔎 חיפושים: {searches:,}"
        ))
    },
    String.SHOW_STATS_ADMIN: {
        'en': "\n".join((
            "📊 Bot Stats 📊\n",
            "👥 Registered users: {users_count:,}",
            "📚 Books read: {books_read:,}",
            "📖 Pages read: {pages_read:,}",
            "🔎 Inline Searches: {inline_searches:,}"
            "💬 Message Searches: {msg_searches:,}"
            "⏭ Jumps to page: {jumps:,}"
        )),
        'he': "\n".join((
            "📊 סטטיסטיקות הבוט 📊\n",
            "👥 משתמשים רשומים: {users_count:,}",
            "📚 ספרים נקראו: {books_read:,}",
            "📖 דפים נקראו: {pages_read:,}",
            "🔎 חיפושים באינליין: {inline_searches:,}"
            "💬 חיפושים בהודעות: {msg_searches:,}"
            "⏭ קפיצות לדף: {jumps:,}"
        ))
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
    String.NUMBERS_ONLY: {
        'en': 'Please use numbers only',
        'he': 'יש להשתמש במספרים בלבד'
    },
    String.JUMP_TIP: {
        'en': 'Tip: instead of browsing, reply to this message with the page number you want to read.\
              \nYou can also edit the number you sent and the page will update accordingly.',
        'he': 'טיפ: במקום לדפדף, הגיבו על ההודעה הזו עם מספר העמוד שברצונכם לקרוא.\
             \nניתן גם לערוך את המספר ששלחתם והעמוד ישתנה בהתאם.'
    },
    String.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y: {
        'en': 'The page does not exist! (Choose a page between {x} and {y})',
        'he': 'הדף אינו קיים! (בחרו עמוד בין {x} ל-{y})'
    },
    String.SEARCH_TIP: {
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
    String.MASECHET_NOT_FOUND: {
        'en': 'Masechet not found',
        'he': 'מסכת לא נמצאה'
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
    String.SHAS_CMD: {
        'en': '!shas ברכות, יז:',
        'he': '!שס ברכות, יז:'
    },
    String.TUR_AND_SA: {
        'en': '📓 Tur & Shulchan Aruch',
        'he': '📓 טור ושולחן ערוך'
    },
    String.TUR_AND_SA_CMD: {
        'en': '!tur, טור יורה דעה קכז ג',
        'he': '!טור, טור יורה דעה קכז ג'
    },
    String.SUBJECTS: {
        'en': '🗂 Subjects',
        'he': '🗂 נושאים'
    },
    String.SUBJECTS_CMD: {
        'en': '!sub, מוסר',
        'he': '!נושא, מוסר'
    },
    String.LETTERS: {
        'en': '🔠 Letters',
        'he': '🔠 אותיות'
    },
    String.LETTERS_CMD: {
        'en': '!let, א',
        'he': '!אות, א'
    },
    String.DATE_RANGES: {
        'en': '📅 Date Ranges',
        'he': '📅 תאריכים'
    },
    String.DATE_RANGES_CMD: {
        'en': '!date, 1945',
        'he': '!תאריך, תר"נ'
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
        'en': 'Page {x} of {y}',
        'he': 'עמוד {x} מתוך {y}'
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
    String.ABOUT: {
        'en': 'ℹ️ About',
        'he': f'{RTL}ℹ️ אודות'
    }
}

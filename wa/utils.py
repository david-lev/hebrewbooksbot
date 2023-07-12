from pywa import WhatsApp
from pywa.types import Message, CallbackSelection, InlineButton, CallbackButton
from data import api
from wa import helpers


def show_commands(_: WhatsApp, msg_or_cb: Message | CallbackButton):
    msg_or_cb.reply_text(
        text="Here are the commands",
    )


def on_search_button(_: WhatsApp, msg_or_cb: Message | CallbackButton):
    msg_or_cb.reply_text(
        text="Send any text to search"
    )


def show_help(_: WhatsApp, msg_or_cb: Message | CallbackButton):
    msg_or_cb.reply_text(
        text="Here is the help",
    )


def on_book(_: WhatsApp, msg_or_cb: Message | CallbackSelection):
    try:
        book = api.get_book(
            int((msg_or_cb.data if isinstance(msg_or_cb, CallbackSelection) else msg_or_cb.text).split(":")[1])
        )
    except ValueError:
        msg_or_cb.react("❌")
        msg_or_cb.reply_text(
            text="Book must be an integer",
            quote=True
        )
        return
    if book is None:
        msg_or_cb.react("❌")
        msg_or_cb.reply_text(
            text="Book not found",
            quote=True
        )
        return
    msg_or_cb.react("⬆️")
    msg_or_cb.reply_document(
        caption="".join((
            f"📚 {book.title}\n",
            f"👤 {book.author}\n",
            f"📅 {book.year}\n" if book.year else "",
            f"🏙 {book.city}\n" if book.city else "",
            f"📖 {book.pages}\n",
        )),
        document=book.pdf_url,
        file_name=f"{book.title} • {book.author}.pdf",
        footer="⚡️ Powered by PyWa",
        quote=True,
        buttons=[
            InlineButton(
                title="♻️ Share",
                callback_data=f"share:{book.id}"
            ),
            InlineButton(
                title="📖 Read",
                callback_data=f"read:{book.id}"
            )
        ]
    )


def on_share(_: WhatsApp, clb: CallbackButton):
    print(clb.data)
    book_id = int(clb.data.split(":")[1])
    book = api.get_book(book_id)
    clb.reply_text(
        text="".join((
            "*שתפו את הספר עם חברים:*\n\n"
            f"📚 {book.title}\n",
            f"👤 {book.author}\n",
            f"📅 {book.year}\n" if book.year else "",
            f"🏙 {book.city}\n" if book.city else "",
            f"📖 {book.pages}\n",
            f"🔗 {helpers.get_self_share(f'!book:{book_id}')}"
        )),
        quote=True,
    )


def on_start(_: WhatsApp, msg: Message):
    msg.reply_text(
        header="📚 ברוכים הבאים לבוט היברובוקס בוואטסאפ!",
        text="\n".join([
            "בוט זה מאפשר לחפש ולעיין בספרים באתר hebrewbooks.org\n",
            "*⚡️ פיצ'רים:*",
            "🔎 חיפוש ספרים במצב אינליין או על ידי שליחת הודעה",
            "📓 עיון במסכתות הש\"ס",
            "📚 עיון בספריה לפי קטגוריה, תאריך או אות",
            "📖 מצב קריאה כתמונה או כקובץ PDF (טקסט בקרוב)",
            "⏪ קפיצה לעמוד",
            "♻️ שיתוף ספרים עם חברים\n",
            "*💡 טיפים:*",
            "• כדי לחפש ספר לפי כותרת או מחבר, השתמשו בפורמט ```כותרת:מחבר```",
            "• במצב קריאה, ניתן לקפוץ לדף מסוים על ידי תגובה להודעה עם מספר העמוד\n",
            "*🔜 בקרוב:*",
            "• חיפוש בתוכן הספרים",
            "• שמירת ספרים מועדפים וסימניות",
            "• שינוי שפה באופן ידני\n",
            "📮 למשוב והערות - @davidlev\n",
        ]),
        keyboard=[
            InlineButton(
                title="Search",
                callback_data="search"
            ),
            InlineButton(
                title="Browse",
                callback_data="browse"
            ),
            InlineButton(
                title="Help",
                callback_data="help"
            )
        ],
        footer="🕯 לעילוי נשמת סבי, הרב אהרן יצחק בן שמואל זנוויל ז\"ל"
    )

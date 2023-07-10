from pywa import WhatsApp
from pywa.types import Message, CallbackButton, CallbackSelection, InlineButton, SectionList, Section, SectionRow
from pywa.filters import TextFilter, CallbackFilter, StickerFilter
from fastapi import FastAPI
from data.config import get_settings
from data import api
from wa import helpers

conf = get_settings()

fastapi_app = FastAPI()

wa = WhatsApp(
    token=conf.wa_token,
    phone_id=conf.wa_phone_id,
    server=fastapi_app,
    verify_token=conf.wa_verify_token,
)


@wa.on_message(TextFilter.command("start", "התחל"))
def on_message(client: WhatsApp, msg: Message):
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


@wa.on_message(TextFilter.command("!search", "!חיפוש"))
@wa.on_callback_button(CallbackFilter.data_matches("search"))
def on_search_button(client: WhatsApp, msg_or_cb: Message | CallbackButton):
    msg_or_cb.reply_text(
        text="Send any text to search"
    )


@wa.on_message(TextFilter.match("!", "!!"))
@wa.on_message(TextFilter.command("commands", "פקודות"))
@wa.on_callback_button(CallbackFilter.data_matches("commands"))
def show_commands(client: WhatsApp, msg: Message):
    msg.reply_text(
        text="Here are the commands",
    )


@wa.on_message(TextFilter.match("?", "??"))
@wa.on_message(TextFilter.command("help", "עזרה"))
@wa.on_callback_button(CallbackFilter.data_matches("help"))
def show_help(client: WhatsApp, msg: Message):
    msg.reply_text(
        text="Here is the help",
    )


@wa.on_message(TextFilter.length((3, 72)))
@wa.on_callback_button(CallbackFilter.data_startswith("search:"))
def on_search(client: WhatsApp, msg: Message | CallbackSelection):
    query = msg.text if isinstance(msg, Message) else msg.description
    msg.react("🔍")
    if isinstance(msg, Message):
        msg.reply_text(
            text=f"Searching for \"{query}\"",
            quote=True
        )
    title, author = helpers.get_title_author(query)
    results, total = api.search(title=title, author=author, offset=1, limit=9)
    if total == 0:
        msg.reply_text(
            text="No results found",
            quote=True
        )
        return

    books = (api.get_book(r.id) for r in results)
    sections = [
        Section(
            title="Search Results",
            rows=[
                SectionRow(
                    title=f"{b.title[:24]}",
                    description=f"{b.author}{f' • {b.year}' if b.year else ''}{f' • {b.city}' if b.city else ''}"[:72],
                    callback_data=f"book:{b.id}"
                ) for b in books
            ]
        )
    ]
    next_offset = helpers.get_offset(1, total, increase=8)
    if next_offset:
        sections.append(
            Section(
                title=f"More results ({next_offset} - {(next_offset + 8) if (next_offset + 8 < total) else total})",
                rows=[
                    SectionRow(
                        title="See more results",
                        description=msg.text,
                        callback_data=f"search:{next_offset}"
                    )
                ]
            )
        )
    msg.reply_text(
        text=f"Found {total} results. Showing from {next_offset - 8 if next_offset > 8 else 1} to {next_offset or total}",
        quote=True,
        keyboard=SectionList(
            button_title="See search results",
            sections=sections
        )
    )


@wa.on_callback_selection(CallbackFilter.data_startswith("book:"))
def on_book(_: WhatsApp, msg: CallbackSelection):
    book = api.get_book(int(msg.data.split(":")[1]))
    if book is None:
        msg.reply_text(
            text="Book not found",
            quote=True
        )
        return
    msg.reply_document(
        caption=f"{book.title}\n"
                f"{book.author}{f' • {book.year}' if book.year else ''}{f' • {book.city}' if book.city else ''}",
        document=book.pdf_url,
        file_name=f"{book.title}-{book.author}.pdf",
        footer="Powered by PyWa",
        quote=True,
        buttons=[
            InlineButton(
                title="Share",
                callback_data=f"share:{book.id}"
            ),
            InlineButton(
                title="Read",
                callback_data=f"read:{book.id}"
            )
        ]
    )

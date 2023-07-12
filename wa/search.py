import data
from pywa import WhatsApp
from pywa.types import Message, CallbackSelection, SectionRow, SectionList
from data import api
from pywa.types import Section
from data.callbacks import SearchNavigation, ShowBook
from data.strings import String as s
from wa.helpers import get_string as gs, slice_long_string as sls


def on_search(_: WhatsApp, msg: Message | CallbackSelection):
    query = msg.text if isinstance(msg, Message) else msg.description
    msg.react("🔍")
    if isinstance(msg, Message):
        msg.reply_text(
            text=gs(s.SEARCHING_FOR_Q, q=query),
            quote=True
        )
        offset = 1
    else:
        offset = SearchNavigation.from_callback(msg.data).offset
    title, author = data.helpers.get_title_author(query)
    results, total = api.search(title=title, author=author, offset=offset, limit=9 if offset == 1 else 8)
    if total == 0:
        msg.reply_text(
            text=gs(s.NO_RESULTS_FOR_Q, q=query),
            quote=True
        )
        return

    books = (api.get_book(r.id) for r in results)
    sections = [
        Section(
            title=gs(s.SEARCH_RESULTS),
            rows=[
                SectionRow(
                    title=sls(b.title, 24),
                    description=sls(f"{b.author}{f' • {b.year}' if b.year else ''}{f' • {b.city}' if b.city else ''}", 72),
                    callback_data=ShowBook(b.id).to_callback()
                ) for b in books
            ]
        )
    ]
    next_offset = data.helpers.get_offset(offset, total, increase=8)
    nav_section_rows = []
    if next_offset:
        nav_section_rows.append(
            SectionRow(
                title=gs(s.NEXT),
                description=sls(query, 72),
                callback_data=SearchNavigation(offset=next_offset, total=total).to_callback()
            )
        )
    if offset > 1:
        nav_section_rows.append(
            SectionRow(
                title=gs(s.PREVIOUS),
                description=sls(query, 72),
                callback_data=SearchNavigation(offset=offset - 8, total=total).to_callback()
            )
        )
    if nav_section_rows:
        sections.append(
            Section(
                title=gs(s.NAVIGATE_BETWEEN_RESULTS),
                rows=nav_section_rows
            )
        )
    msg.reply_text(
        text=gs(s.X_TO_Y_OF_TOTAL_FOR_S, x=offset, y=(offset + 8) if (offset + 8 < total) else total, total=total, s=query),
        keyboard=SectionList(
            button_title=gs(s.SEARCH_RESULTS),
            sections=sections
        )
    )

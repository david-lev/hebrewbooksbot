import data
from pywa import WhatsApp
from pywa.types import Message, CallbackSelection, SectionRow, SectionList, Button
from data import api
from db import repository
from db.repository import StatsType
from pywa.types import Section
from data.callbacks import SearchNavigation, ShowBook
from data.strings import String as s
from wa.helpers import get_string as gs, slice_long_string as sls
from wa.utils import Menu


def on_search(_: WhatsApp, mc: Message | CallbackSelection):
    wa_id = mc.from_user.wa_id
    query = mc.text if isinstance(mc, Message) else mc.description
    if len(query) < 3:
        mc.react("❌")
        mc.reply_text(
            text=gs(wa_id, s.SEARCH_TOO_SHORT),
            footer=gs(wa_id, s.HB_FOOTER),
            buttons=(
                Button(title=sls(gs(wa_id, s.SEARCH), 20), callback_data=Menu.SEARCH),
                Button(title=sls(gs(wa_id, s.BACK), 20), callback_data=Menu.START),
            ),
        )
        return
    mc.react("🔍")
    offset = (
        1 if isinstance(mc, Message) else SearchNavigation.from_callback(mc.data).offset
    )
    title, author = data.helpers.get_title_author(query)
    results, total = api.search(
        title=title, author=author, offset=offset, limit=9 if offset == 1 else 8
    )
    if total == 0:
        mc.react("❌")
        mc.reply_text(
            text=gs(wa_id, s.NO_RESULTS_FOR_Q, q=query),
            footer=gs(wa_id, s.HB_FOOTER),
            buttons=(
                Button(title=sls(gs(wa_id, s.SEARCH), 20), callback_data=Menu.SEARCH),
                Button(title=sls(gs(wa_id, s.BACK), 20), callback_data=Menu.START),
            ),
        )
        return

    books = (api.get_book(r.id) for r in results)
    sections = [
        Section(
            title=sls(gs(wa_id, s.SEARCH_RESULTS), 24),
            rows=[
                SectionRow(
                    title=sls(b.title, 24),
                    description=sls(b.description, 72),
                    callback_data=ShowBook(b.id).to_callback(),
                )
                for b in books
            ],
        )
    ]
    next_offset = data.helpers.get_offset(offset, total, increase=8)
    nav_section_rows = []
    if next_offset:
        nav_section_rows.append(
            SectionRow(
                title=sls(gs(wa_id, s.NEXT), 24),
                description=sls(query, 72),
                callback_data=SearchNavigation(
                    offset=next_offset, total=total
                ).to_callback(),
            )
        )
    if offset > 1:
        nav_section_rows.append(
            SectionRow(
                title=sls(gs(wa_id, s.PREVIOUS), 24),
                description=sls(query, 72),
                callback_data=SearchNavigation(
                    offset=offset - 8, total=total
                ).to_callback(),
            )
        )
    if nav_section_rows:
        sections.append(
            Section(
                title=sls(gs(wa_id, s.NAVIGATE_BETWEEN_RESULTS), 24),
                rows=nav_section_rows,
            )
        )
    mc.reply_text(
        text=gs(
            wa_id,
            s.X_TO_Y_OF_TOTAL_FOR_S,
            x=offset,
            y=(offset + 8) if (offset + 8 < total) else total,
            total=total,
            s=query,
        ),
        footer=gs(wa_id, s.HB_FOOTER),
        buttons=SectionList(
            button_title=sls(gs(wa_id, s.SEARCH_RESULTS), 20), sections=sections
        ),
    )
    repository.increase_stats(StatsType.MSG_SEARCHES)

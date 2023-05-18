from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from data import api
from data.enums import BrowseType as BrowseTypeEnum
from tg import helpers
from tg.helpers import Menu
from tg.strings import String as s, get_string as gs
from tg.callbacks import BrowseNavigation, BrowseType, ShowBook


def browse_menu(_: Client, query: CallbackQuery):
    """
    Browse menu

    query.data format: "browse_menu"
    """
    menu = [
        [(BrowseTypeEnum.SHAS, s.SHAS), (BrowseTypeEnum.SUBJECT, s.SUBJECTS)],
        [(BrowseTypeEnum.LETTER, s.LETTERS), (BrowseTypeEnum.DATERANGE, s.DATE_RANGES)]
    ]
    query.edit_message_text(
        text=gs(mqc=query, string=s.CHOOSE_BROWSE_TYPE),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=string),
                        callback_data=BrowseType(browse_type).to_callback()
                    ) for browse_type, string in item
                ] for item in menu
            ] + [[
                InlineKeyboardButton(
                    text=gs(mqc=query, string=s.BACK),
                    callback_data=Menu.START
                )
            ]]
        )
    )


def browse_types(_: Client, clb: CallbackQuery):
    """
    Browse types
    """
    browse_type = BrowseType.from_callback(clb.data)
    _results, _, choose, buttons_in_row = helpers.get_browse_type_data(browse_type.type)
    results = _results()
    clb.edit_message_text(
        text=gs(mqc=clb, string=choose),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{res.name}{f' ({res.total})' if res.total else ''}",
                        callback_data=BrowseNavigation(
                            type=browse_type.type,
                            id=str(res.id),
                            offset=1,
                            total=res.total or 0
                        ).to_callback()
                    ) for res in results
                ][i:i + buttons_in_row][::-1] for i in range(0, len(results), buttons_in_row)
            ] + [[
                InlineKeyboardButton(
                    text=gs(mqc=clb, string=s.BACK),
                    callback_data=Menu.BROWSE
                )
            ]]
        )
    )


def browse_books_navigator(_: Client, clb: CallbackQuery):
    """
    Browse books navigator
    """
    browse_nav = BrowseNavigation.from_callback(clb.data)
    results, total = api.browse(
        browse_type=browse_nav.type,
        browse_id=browse_nav.id,
        offset=browse_nav.offset,
        limit=5
    )
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{book.title} • {book.author}{f' • {book.year}' if book.year else ''}"
                     f"{f' • {book.city}' if book.city else ''}",
                callback_data=ShowBook(id=book.id).join_to_callback(browse_nav)
            )
        ] for book in (api.get_book(result.id) for result in results)
    ]
    next_offset = helpers.get_offset(browse_nav.offset, int(total), increase=5)

    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.NEXT),
                callback_data=BrowseNavigation(
                    type=browse_nav.type,
                    id=browse_nav.id,
                    offset=next_offset,
                    total=total
                ).to_callback()
            )
        )
    if (browse_nav.offset - 5) > 0:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.PREVIOUS),
                callback_data=BrowseNavigation(
                    type=browse_nav.type,
                    id=browse_nav.id,
                    offset=browse_nav.offset - 5,
                    total=total
                ).to_callback()
            )
        )
    if next_previous_buttons:
        buttons.append(next_previous_buttons)

    buttons.append(
        [
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.BACK),
                callback_data=BrowseType(browse_nav.type).to_callback()
            )
        ]
    )
    clb.edit_message_text(
        text=gs(mqc=clb, string=s.CHOOSE),
        reply_markup=InlineKeyboardMarkup(
            buttons
        )
    )

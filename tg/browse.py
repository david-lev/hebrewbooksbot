from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import data
from data import api
from data.enums import BrowseType as BrowseTypeEnum
from db import repository
from db.repository import StatsType
from tg import helpers
from tg.helpers import Menu, get_string as gs, get_lang_code as glc
from data.strings import String as s
from data.callbacks import BrowseNavigation, BrowseType, ShowBook, BookType, ReadBook, ReadMode


def browse_menu(_: Client, query: CallbackQuery):
    """
    Browse menu

    query.data format: "browse_menu"
    """
    menu = [
        [(BrowseTypeEnum.SHAS, s.SHAS), (BrowseTypeEnum.SUBJECT, s.SUBJECTS)],
        [(BrowseTypeEnum.LETTER, s.LETTERS), (BrowseTypeEnum.DATERANGE, s.DATE_RANGES)],
        [(BrowseTypeEnum.TURSA, s.TUR_AND_SA)],
    ]
    query.edit_message_text(
        text=gs(mqc=query, string=s.CHOOSE_BROWSE_TYPE),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=string),
                        callback_data=BrowseType(type=browse_type, id="").to_callback()
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
    _browse_type, *others = clb.data.split(",")
    browse_type = BrowseType.from_callback(_browse_type)
    func, choose_msg, buttons_in_row = helpers.get_browse_type_data(browse_type.type)
    results = func(browse_type.id) if browse_type.id else func()

    clb.edit_message_text(
        text=gs(mqc=clb, string=choose_msg),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{res.name}{f' ({res.total})' if res.total else ''}",
                        callback_data=BrowseType(
                            id=str(res.id),
                            type=browse_type.type
                        ).join_to_callback(browse_type, *others)
                        if browse_type.type == BrowseTypeEnum.TURSA and res.has_children
                        else ReadBook(
                            id=str(res.id),
                            page=1,
                            total=-1,  # There is no `total`
                            read_mode=ReadMode.PDF,
                            book_type=BookType.TURSA
                        ).join_to_callback(browse_type, *others)
                        if browse_type.type == BrowseTypeEnum.TURSA and not res.has_children
                        else BrowseNavigation(
                            type=browse_type.type,
                            id=res.id,
                            offset=1,
                            total=res.total or 0
                        ).to_callback()
                        if browse_type.type != BrowseTypeEnum.SHAS
                        else ReadBook(
                            id=res.id,
                            page=1,
                            total=-1,  # There is no `total` yet
                            read_mode=ReadMode.IMAGE,
                            book_type=BookType.MASECHET
                        ).join_to_callback(browse_type)
                    ) for res in results
                ][i:i + buttons_in_row][::-1] for i in range(0, len(results), buttons_in_row)
            ] + [[
                InlineKeyboardButton(
                    text=gs(mqc=clb, string=s.BACK),
                    callback_data=",".join(others) or Menu.BROWSE
                )
            ]]
        )
    )
    if browse_type.type == BrowseTypeEnum.SHAS:
        repository.increase_stats(StatsType.BOOKS_READ)


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
                text=res.title,
                callback_data=ShowBook(id=res.id).join_to_callback(browse_nav)
            )
        ] for res in results
    ]
    next_offset = data.helpers.get_offset(browse_nav.offset, int(total), increase=5)

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
        buttons.append(next_previous_buttons if glc(clb) == "he" else next_previous_buttons[::-1])

    buttons.append(
        [
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.BACK),
                callback_data=BrowseType(id="", type=browse_nav.type).to_callback()
            )
        ]
    )
    clb.edit_message_text(
        text=gs(mqc=clb, string=s.X_TO_Y_OF_TOTAL).format(
            x=browse_nav.offset, y=next_offset - 1 if next_offset else total, total=total),
        reply_markup=InlineKeyboardMarkup(
            buttons
        )
    )

from data import api
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, CallbackQuery

from data.api import get_book
from tg.utils import get_offset


def browse_menu(_: Client, query: CallbackQuery):
    query.edit_message_text(
        text="בחר סוג עיון",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("אותיות", callback_data="browse:letter"),
                    InlineKeyboardButton("תאריכים", callback_data="browse:daterange"),
                    InlineKeyboardButton("נושאים", callback_data="browse:subject"),
                    InlineKeyboardButton("חזור", callback_data="start_menu")
                ]
            ]
        )
    )


def browse(_: Client, query: CallbackQuery):
    _type = query.data.split(":")[-1]
    if _type == "letter":
        results = api.get_letters()
    elif _type == "daterange":
        results = api.get_date_ranges()
    else:
        results = api.get_subjects()
    query.edit_message_text(
        text="בחר",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{result.name} ({result.total})",
                        callback_data=f"browse:{_type}:{result.id}:1:{result.total}"
                    )
                ] for result in results
            ] + [[
                InlineKeyboardButton(text="חזור", callback_data="browse_menu")
            ]]
        )
    )


def browse_results(_: Client, query: CallbackQuery):
    browse_type, browse_id, offset, total = query.data.split(":")[1:]
    results, total = api.browse(browse_type, browse_id, offset=int(offset), limit=5)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{book.author} • {book.year} • {book.city}",
                callback_data=f"book_{book.id}"
            )
        ] for book in (get_book(result.id) for result in results)
    ]
    next_offset = get_offset(int(offset), int(total), increase=5)

    next_previous_bts = []
    if next_offset:
        next_previous_bts.append(
            InlineKeyboardButton(
                text="הבא",
                callback_data=f"browse:{browse_type}:{browse_id}:{next_offset}:{total}"
            )
        )
    if offset != "1" and int(offset) - 5 > 0:
        next_previous_bts.append(
            InlineKeyboardButton(
                text="הקודם",
                callback_data=f"browse:{browse_type}:{browse_id}:{int(offset) - 5}:{total}"
            )
        )
    if next_previous_bts:
        buttons.append(next_previous_bts)

    buttons.append(
        [
            InlineKeyboardButton(text="חזור", callback_data=f"browse:{browse_type}")
        ]
    )

    query.edit_message_text(
        text="בחר",
        reply_markup=InlineKeyboardMarkup(
            buttons
        )
    )

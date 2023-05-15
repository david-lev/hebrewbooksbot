from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from data import api
from data.api import get_book
from tg import helpers
from tg.strings import String as s, get_string as gs


def browse_menu(_: Client, query: CallbackQuery):
    """
    Browse menu

    query.data format: "browse_menu"
    """
    query.edit_message_text(
        text=gs(mqc=query, string=s.CHOOSE_BROWSE_TYPE),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(gs(mqc=query, string=s.SUBJECTS), callback_data="browse_type:subject"),
                    InlineKeyboardButton(gs(mqc=query, string=s.LETTERS), callback_data="browse_type:letter"),
                    InlineKeyboardButton(gs(mqc=query, string=s.DATES), callback_data="browse_type:daterange"),
                ],
                [InlineKeyboardButton("🔙", callback_data="start")]
            ]
        )
    )


def browse_types(_: Client, query: CallbackQuery):
    """
    Browse types

    query.data format: "browse_type:{type}"
    """
    _type = query.data.split(":")[-1]
    if _type == "letter":
        results = api.get_letters()
    elif _type == "daterange":
        results = api.get_date_ranges()
    else:
        results = api.get_subjects()
    query.edit_message_text(
        text=gs(mqc=query, string=s.CHOOSE),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{result.name} ({result.total})",
                        callback_data=f"browse_nav:{_type}:{result.id}:1:{result.total}"
                    )
                ] for result in results
            ] + [[
                InlineKeyboardButton(text="🔙", callback_data="browse_menu")
            ]]
        )
    )


def browse_books_navigator(_: Client, clb: CallbackQuery):
    """
    Browse books navigator

    clb.data format: "browse_nav:{browse_type}:{browse_id}:{offset}:{total}"
    """
    browse_type, browse_id, offset, total = clb.data.split(":")[1:]
    results, total = api.browse(browse_type, browse_id, offset=int(offset), limit=5)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{book.title} • {book.author}{f' • {book.year}' if book.year else ''}"
                     f"{f' • {book.city}' if book.city else ''}",
                callback_data=f"show:{book.id}:{clb.data}"
            )
        ] for book in (get_book(result.id) for result in results)
    ]
    next_offset = helpers.get_offset(int(offset), int(total), increase=5)

    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.NEXT),
                callback_data=f"browse_nav:{browse_type}:{browse_id}:{next_offset}:{total}"
            )
        )
    if offset != "1" and int(offset) - 5 > 0:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.PREVIOUS),
                callback_data=f"browse_nav:{browse_type}:{browse_id}:{int(offset) - 5}:{total}"
            )
        )
    if next_previous_buttons:
        buttons.append(next_previous_buttons)

    buttons.append(
        [
            InlineKeyboardButton(text="🔙", callback_data=f"browse_type:{browse_type}")
        ]
    )

    clb.edit_message_text(
        text=gs(mqc=clb, string=s.CHOOSE),
        reply_markup=InlineKeyboardMarkup(
            buttons
        )
    )

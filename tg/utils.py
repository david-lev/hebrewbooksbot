from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from data import api


def callback_query(_: Client, clb: CallbackQuery):
    action, *data = clb.data.split("_")
    if action == "next":
        kb = [[InlineKeyboardButton(
            text=f"{book.title} | {book.author}",
            callback_data=f"book_{book.id}")]
            for book in (api.get_book(b.id) for b in api.search(data[1], offset=int(data[0]))[0])
        ]

        kb.append([InlineKeyboardButton(
            text="Next",
            callback_data=f"action_next_10_{data[1]}_{utils.get_offset(data[0], int(data[2]))}"
        )])

        clb.edit_message_text(
            text="Results",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    elif action == "book":
        book = api.get_book(int(data[0]))
        clb.edit_message_text(
            text=f"{book.title} | {book.author}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Download",
                            url=book.pdf_url
                        )
                    ]
                ]
            )
        )


